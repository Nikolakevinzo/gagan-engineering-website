import axios from "axios";

export function getApiBaseUrl() {
  if (
    typeof window !== "undefined" &&
    window.location.hostname !== "localhost" &&
    window.location.hostname !== "127.0.0.1"
  ) {
    return "/api"; // In production, ALWAYS use relative /api
  }
  const envUrl = process.env.REACT_APP_BACKEND_URL;
  if (envUrl) {
    return `${envUrl.replace(/\/+$/, "")}/api`;
  }
  return "/api";
}

export const API = getApiBaseUrl();
export const api = axios.create({ baseURL: API });

