import axios from "axios";
import { baseURL } from "../utilities/constants";

const http = axios.create({
    baseURL: baseURL, 
    headers: {
        "Content-Type": "application/json",
    },
});

export default http;
