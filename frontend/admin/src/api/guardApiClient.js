/**
 * Guard API client — for Telegram-authenticated guard submissions.
 * Uses Telegram initData for auth (not JWT).
 * All requests go through Vite proxy (/api → localhost:8000).
 */

const API_BASE = import.meta.env.VITE_API_URL || '/api';

/**
 * Perform an HTTP request with Telegram initData auth.
 * @param {string} path - API path (e.g. "/submissions/current-week")
 * @param {RequestInit} options - Fetch options
 * @param {string} initData - Telegram WebApp initData for auth
 * @returns {Promise<{data: any, error: string|null}>}
 */
async function request(path, options, initData) {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'X-Telegram-Init-Data': initData,
        ...options.headers,
      },
    });

    if (!res.ok) {
      let error;
      if (res.status === 401) {
        error = 'שגיאת אימות — נסה שוב דרך הבוט';
      } else if (res.status === 403 || res.status === 409) {
        error = 'השבוע נעול להגשות';
      } else if (res.status === 422) {
        const body = await res.json();
        error = body?.detail || 'אירעה שגיאה — נסה שוב';
      } else {
        error = 'אירעה שגיאה — נסה שוב';
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
    return { data: null, error: 'בעיית תקשורת — בדוק את החיבור לאינטרנט' };
  }
}

/**
 * GET request with Telegram initData.
 */
async function get(path, initData) {
  return request(path, { method: 'GET' }, initData);
}

/**
 * POST request with Telegram initData.
 */
async function post(path, body, initData) {
  return request(
    path,
    {
      method: 'POST',
      body: JSON.stringify(body),
    },
    initData,
  );
}

/**
 * Fetch the current open week (or null/404 if none).
 */
async function getCurrentWeek(initData) {
  return get('/weeks/current', initData);
}

export { get, post, getCurrentWeek };