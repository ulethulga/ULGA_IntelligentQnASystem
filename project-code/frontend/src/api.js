const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export async function apiRequest(path, options = {}, token) {
  const headers = {
    ...(options.headers || {}),
  };

  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let detail = "Request failed";
    try {
      const body = await response.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      detail = await response.text();
    }
    throw new Error(detail);
  }

  return response.json();
}

export function parseJwt(token) {
  try {
    const payload = token.split(".")[1];
    return JSON.parse(atob(payload));
  } catch {
    return {};
  }
}
