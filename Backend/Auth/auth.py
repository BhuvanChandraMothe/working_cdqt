from fastapi import Request, HTTPException, Depends, status # Import status for HTTP status codes
from fastapi.responses import JSONResponse # Import JSONResponse to return custom headers
from starlette.middleware.base import BaseHTTPMiddleware,RequestResponseEndpoint
import jwt
from jose import jwk # Import jwk for handling JSON Web Keys
import httpx # Import httpx for making HTTP requests (needed for JWKS)
import time # For caching JWKS
import os
from dotenv import load_dotenv
import urllib.parse

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env') # Example if .env is one level up
load_dotenv(dotenv_path=dotenv_path)

# --- Configuration Variables (Review these carefully) ---
# Your Keycloak URL, including the '/auth' path if present (e.g., "http://localhost:8080/auth")
KEYCLOAK_BASE_URL = os.getenv("KEYCLOAK_BASE_URL", "http://localhost:8080")
# Your Keycloak Realm Name (e.g., "master" or "your-realm")
keycloak_realm = os.getenv("KEYCLOAK_REALM", "Data Quality App")
KEYCLOAK_REALM=urllib.parse.quote(keycloak_realm)
# The Client ID of your FastAPI application registered in Keycloak
# This is the 'audience' (aud) your FastAPI expects in the access token.
FASTAPI_CLIENT_ID = os.getenv("KEYCLOAK_FASTAPI_CLIENT_ID", "FastAPI-Tester")

# Derived Keycloak URLs
KEYCLOAK_CERTS_URL = f"{KEYCLOAK_BASE_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"
KEYCLOAK_ISSUER_URL = f"{KEYCLOAK_BASE_URL}/realms/{KEYCLOAK_REALM}"

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM","RS256") # Should match your Keycloak client's token settings

# Cache for Keycloak public keys (JWKS)
# This prevents hitting Keycloak's certs endpoint on every single request.
JWKS_CACHE = {}
JWKS_LAST_FETCHED = 0
JWKS_CACHE_TTL = 3600 # Cache for 1 hour (adjust as needed)

async def get_keycloak_public_keys():
    """
    Fetches and caches Keycloak's public keys (JWKS) for token signature verification.
    """
    global JWKS_CACHE, JWKS_LAST_FETCHED
    if not JWKS_CACHE or (time.time() - JWKS_LAST_FETCHED) > JWKS_CACHE_TTL:
        print("Fetching new JWKS from Keycloak...")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(KEYCLOAK_CERTS_URL)
                response.raise_for_status() # Raise an exception for bad status codes
                JWKS_CACHE = response.json()
                JWKS_LAST_FETCHED = time.time()
                print("Successfully fetched new JWKS.")
            except httpx.HTTPStatusError as e:
                print(f"Error fetching JWKS: HTTP Status {e.response.status_code} - {e.response.text}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Could not retrieve Keycloak public keys due to HTTP error."
                )
            except httpx.RequestError as e:
                print(f"Network error fetching JWKS: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Could not connect to Keycloak to retrieve public keys."
                )
    return JWKS_CACHE

def format_keycloak_public_key(raw_key: str) -> str:

    key = raw_key.replace('-----BEGIN PUBLIC KEY-----', '')
    key = key.replace('-----END PUBLIC KEY-----', '')
    key = key.replace('\n', '')
    key = key.strip()
    formatted_key = "-----BEGIN PUBLIC KEY-----\n"
    chunks = [key[i:i+64] for i in range(0, len(key), 64)]
    formatted_key += '\n'.join(chunks)
    formatted_key += "\n-----END PUBLIC KEY-----"
    return formatted_key


class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        # Skip auth for specific paths
        if request.url.path in ["/docs", "/redoc", "/openapi.json", "/auth/login"]:
            return await call_next(request)

        request.state.auth_user = None
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "missing_authorization",
                    "message": "Authorization header is missing"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "invalid_auth_format",
                    "message": "Authorization header must start with 'Bearer '"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.split(" ")[1]
        try:
            # 1. Fetch Keycloak Public Keys (JWKS)
            # This replaces your static TOKEN_SECRET_KEY and format_keycloak_public_key
            jwks = await get_keycloak_public_keys()
            header = jwt.get_unverified_header(token)
            kid = header.get("kid") # Key ID

            if not kid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Key ID (kid) missing from token header. Cannot verify signature.",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            key = None
            for jwk_key in jwks["keys"]:
                if jwk_key["kid"] == kid:
                    # Construct the public key from JWK format
                    key = jwk.construct(jwk_key)
                    break

            if not key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Public key for token's Key ID (kid) not found in Keycloak's JWKS. Token might be invalid or issued by an unknown source.",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # 2. Decode and Verify the Access Token
            payload = jwt.decode(
                token,
                key.to_pem().decode('utf-8'),
                algorithms=[JWT_ALGORITHM], # Use the algorithm from your config
                audience=FASTAPI_CLIENT_ID, # Validate against your FastAPI client ID
                issuer=KEYCLOAK_ISSUER_URL, # Validate against your Keycloak Realm's issuer URL
                options={
                    "verify_aud": True, # CRITICAL: Ensure Audience is verified
                    "verify_exp": True, # Ensure Expiration is verified (already was True)
                    "verify_iss": True, # CRITICAL: Ensure Issuer is verified
                    "verify_sub": True
                }
            )
            request.state.auth_user = payload
            print("Authentication successful")
        except jwt.ExpiredSignatureError:
            # This is the primary signal for the frontend to use a refresh token.
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "token_expired",
                    "message": "Access token has expired. Please refresh."
                },
                headers={"WWW-Authenticate": f"Bearer realm=\"{KEYCLOAK_REALM}\", error=\"invalid_token\", error_description=\"Access token expired\""},
            )
        except jwt.InvalidAudienceError: # Specific error for Audience mismatch
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "invalid_audience",
                    "message": f"Token audience does not match FastAPI client ID ('{FASTAPI_CLIENT_ID}')."
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidIssuerError: # Specific error for Issuer mismatch
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "invalid_issuer",
                    "message": f"Token issuer does not match Keycloak realm ('{KEYCLOAK_ISSUER_URL}')."
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.PyJWTError as e: # Catch other JWT validation errors
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "invalid_token",
                    "message": f"Invalid token: {str(e)}"
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            # Catch any other unexpected errors during the process
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "authentication_error",
                    "message": f"An unexpected authentication error occurred: {str(e)}"
                },
            )

        response = await call_next(request)
        return response

async def get_current_user(request: Request):
    """
    Dependency to easily access the authenticated user payload in your routes.
    """
    if request.state.auth_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return request.state.auth_user