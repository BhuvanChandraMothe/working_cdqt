import { useEffect, useState, useRef } from "react";
import Keycloak from "keycloak-js";
 
const useAuth = () => {
  const [isLogin, setIsLogin] = useState(false);
  const [keycloak, setKeycloak] = useState(null);
  const isRun = useRef(false);
 
  useEffect(() => {
    if (isRun.current) return;
 
    isRun.current = true;
    const client = new Keycloak({
      realm: 'Data Quality App',
      url: 'http://localhost:8080/',
      clientId: 'Bhuvan'
    });
 
    client.init({ onLoad: 'login-required' })
      .then((authenticated) => {
        setIsLogin(authenticated);
        setKeycloak(client);
      })
      .catch((err) => {
        console.error("Keycloak initialization failed", err);
      });
 
  }, []);
 
  return { isLogin, keycloak };
};
 
export default useAuth;