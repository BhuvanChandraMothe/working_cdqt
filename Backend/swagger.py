from fastapi import FastAPI

from fastapi.openapi.utils import get_openapi
 
def custom_openapi(app: FastAPI):

    if app.openapi_schema:

        return app.openapi_schema

    openapi_schema = get_openapi(

        title="My API",

        version="1.0.0",

        routes=app.routes,

    )

    openapi_schema["components"] = openapi_schema.get("components", {})  # Ensure 'components' exists

    openapi_schema["components"]["securitySchemes"] = {

        "bearerAuth": {

            "type": "http",

            "scheme": "bearer",

            "bearerFormat": "JWT"

        }

    }

    openapi_schema["security"] = [{"bearerAuth": []}]

    app.openapi_schema = openapi_schema

    return app.openapi_schema
 