
const API_URL = (
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "");

const CSRF_COOKIE = "csrf_token";
const CSRF_HEADER = "X-CSRF-Token";

let csrfToken = null;

//This function reads a particular cookie from the browser.

function readCookie(name) {
  const prefix = `${name}=`;
  const cookie = document.cookie
  //document is a built-in JavaScript object provided by the browser.
    .split("; ")
    .find((item) => item.startsWith(prefix));

    console.log(cookie.split(";"));

  return cookie
    ? decodeURIComponent(cookie.slice(prefix.length))
    : null;
    //If the cookie exists, slice() removes the cookie name and equals sign.
    //decodeURIComponent() decodes URL-encoded characters.
}

async function parseResponse(response) {
  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const detail = data?.detail;
    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg).join(", ")
      : typeof detail === "string"
        ? detail
        : data?.message || `Request failed (${response.status})`;

    throw new Error(message);
  }

  return data;
}

export async function initializeCsrf() {
  const response = await fetch(`${API_URL}/api/auth/csrf`, {
    method: "GET",
    credentials: "include",
  });

  const data = await parseResponse(response);

  csrfToken = readCookie(CSRF_COOKIE) || data?.csrf_token || null;
  //data?.csrf_token mein ?. optional chaining hai. Agar data null ya undefined hai, to error throw karne ke bajaye expression undefined return karega.

  if (!csrfToken) {
    throw new Error("CSRF token missing. Check your backend cookie.");
  }

  return csrfToken;
}

export async function apiRequest(path, options = {}) {
  const method = (options.method || "GET").toUpperCase();
  const headers = { ...options.headers };
  //... ko spread operator kehte hain. Ye options.headers ki properties ko naye object mein copy karta hai.

  if (options.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
    if (!csrfToken || !readCookie(CSRF_COOKIE)) {
      await initializeCsrf();
    }

    headers[CSRF_HEADER] = readCookie(CSRF_COOKIE) || csrfToken;
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    method,
    headers,
    credentials: "include",
    //credentials: "include" — browser ko applicable cookies request ke saath bhejne aur eligible response cookies accept karne deta hai.
  });

  return parseResponse(response);
}

export const authApi = {
  register: (payload) =>
    apiRequest("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  login: (payload) =>
    apiRequest("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  me: () => apiRequest("/api/auth/me"),

  logout: () =>
    apiRequest("/api/auth/logout", {
      method: "POST",
    }),
};

