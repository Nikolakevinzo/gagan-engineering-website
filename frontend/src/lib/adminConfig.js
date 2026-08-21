// Helper for resolving backend API URL reliably in all environments

export function getBackendUrl() {
  if (process.env.REACT_APP_BACKEND_URL) {
    return process.env.REACT_APP_BACKEND_URL.replace(/\/+$/, "");
  }
  if (
    typeof window !== "undefined" &&
    (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
  ) {
    return "http://127.0.0.1:8000";
  }
  return "";
}
