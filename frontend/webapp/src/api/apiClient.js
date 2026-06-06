/**
 * API client wrapper with Telegram initData auth.
 * Returns { data, error } tuple for every request.
 */
import { messages } from "../utils/messages.js";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Perform an HTTP request with auth headers.
 * @param {string} path - API path (e.g. "/api/submissions/current-week")
 * @param {RequestInit} options - Fetch options
 * @param {string} initData - Telegram WebApp initData for auth
 * @returns {Promise<{data: any, error: string|null}>}
 */
async function request(path, options, initData) {
  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${initData}`,
        ...options.headers,
      },
    });

    if (!res.ok) {
      let error;
      if (res.status === 401) {
        error = messages.ERR_AUTH;
      } else if (res.status === 403 || res.status === 409) {
        error = messages.ERR_LOCKED;
      } else if (res.status === 422) {
        const body = await res.json();
        error = body?.detail || messages.ERR_GENERIC;
      } else {
        error = messages.ERR_GENERIC;
      }
      return { data: null, error };
    }

    // 204 No Content
    if (res.status === 204) {
      return { data: null, error: null };
    }

    const data = await res.json();
    return { data, error: null };
  } catch {
    return { data: null, error: messages.ERR_NETWORK };
  }
}

/**
 * GET request.
 */
async function _get(path, initData) {
  return request(path, { method: "GET" }, initData);
}

/**
 * POST request.
 */
async function _post(path, body, initData) {
  return request(
    path,
    {
      method: "POST",
      body: JSON.stringify(body),
    },
    initData,
  );
}

/**
 * PUT request.
 */
async function _put(path, body, initData) {
  return request(
    path,
    {
      method: "PUT",
      body: JSON.stringify(body),
    },
    initData,
  );
}

/**
 * Default api object for convenience.
 */
export const api = { get: _get, post: _post, put: _put };

/**
 * Fetch the current open week (or null/404 if none).
 */
async function _getCurrentWeek(initData) {
  return _get("/api/weeks/current", initData);
}

export { _get as get, _post as post, _put as put, _getCurrentWeek as getCurrentWeek };
