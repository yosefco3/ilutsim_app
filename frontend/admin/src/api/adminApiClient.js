/**
 * Admin API client — thin wrapper around fetch for the admin dashboard.
 * All requests go through Vite proxy (/api → localhost:8000).
 */

const API_BASE = import.meta.env.VITE_API_URL || '/api';

function getToken() {
  return localStorage.getItem('admin_token');
}

export function isLoggedIn() {
  return !!getToken();
}

function setToken(token) {
  localStorage.setItem('admin_token', token);
}

function clearToken() {
  localStorage.removeItem('admin_token');
}

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };

  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(url, { ...options, headers });

  if (res.status === 401) {
    clearToken();
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${res.status}`);
  }

  // Handle 204 No Content (e.g. DELETE responses)
  if (res.status === 204) {
    return null;
  }

  // Handle blob responses (Excel export)
  if (endpoint.includes('/export/')) {
    return res.blob();
  }

  return res.json();
}

// ──── Auth ────
export function adminLogin(username, password) {
  return request('/auth/admin/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  }).then((data) => {
    setToken(data.access_token);
    return data;
  });
}

export function adminLogout() {
  clearToken();
}

export function getAdminProfile() {
  return request('/auth/admin/me');
}

// ──── Guards (Users) ────
export function fetchGuards(params = {}) {
  const query = new URLSearchParams(params).toString();
  return request(`/admin/users?${query}`);
}

export function fetchGuard(id) {
  return request(`/admin/users/${id}`);
}

export function createGuard(data) {
  return request('/admin/users', { method: 'POST', body: JSON.stringify(data) });
}

export function updateGuard(id, data) {
  return request(`/admin/users/${id}`, { method: 'PATCH', body: JSON.stringify(data) });
}

export function deleteGuard(id) {
  return request(`/admin/users/${id}`, { method: 'DELETE' });
}

// ──── Weeks ────
export function fetchWeeks(params = {}) {
  const query = new URLSearchParams(params).toString();
  return request(`/admin/weeks?${query}`);
}

export function fetchWeek(id) {
  return request(`/admin/weeks/${id}`);
}

export function createWeek(data) {
  return request('/admin/weeks', { method: 'POST', body: JSON.stringify(data) });
}

export function updateWeekStatus(id, status) {
  return request(`/admin/weeks/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  });
}

export function sendWeekReminders(id) {
  return request(`/admin/weeks/${id}/remind`, { method: 'POST' });
}

export function lockWeek(id) {
  return updateWeekStatus(id, 'locked');
}

export function unlockWeek(id) {
  return updateWeekStatus(id, 'open');
}

// Open a week for submission (closed/locked → open). Sends guard notifications.
export function openWeek(id) {
  return request(`/admin/weeks/${id}/open`, { method: 'POST' });
}

export function publishWeek(id) {
  return updateWeekStatus(id, 'published');
}

export function deleteWeek(id) {
  return request(`/admin/weeks/${id}`, { method: 'DELETE' });
}

// ──── Submissions ────
export function fetchSubmissions(weekId) {
  return request(`/admin/weeks/${weekId}/submissions`);
}

export function fetchSubmissionsDetailed(weekId) {
  return request(`/admin/weeks/${weekId}/submissions/detailed`);
}

// A guard's existing submission for one week (admin-only), or null. Used to
// pre-fill the admin constraints form so the admin can edit what the guard
// (or a previous admin) already submitted — including Telegram submissions.
export function fetchGuardSubmission(userId, weekId) {
  const query = new URLSearchParams({ user_id: userId, week_id: weekId }).toString();
  return request(`/submissions/admin?${query}`);
}

// Admin fills a guard's weekly constraints on their behalf (e.g. guards
// without Telegram). Works regardless of the week's status.
export function createGuardSubmission(payload) {
  return request('/submissions/admin', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

// ──── Notifications ────
export function sendNotifications(weekId) {
  return request(`/admin/notifications/week/${weekId}`, { method: 'POST' });
}

// ──── Export ────
export async function exportWeekExcel(weekId) {
  const blob = await request(`/admin/export/constraints/${weekId}`);
  return blob;
}

// ──── Settings ────
export function fetchSettings() {
  return request('/admin/settings');
}

export function updateSettings(settingsMap) {
  return request('/admin/settings', {
    method: 'PUT',
    body: JSON.stringify({ settings: settingsMap }),
  });
}

// ──── Admins ────
export function fetchAdmins() {
  return request('/admin/admins');
}

export function createAdmin(data) {
  return request('/admin/admins', { method: 'POST', body: JSON.stringify(data) });
}

export function deleteAdmin(id) {
  return request(`/admin/admins/${id}`, { method: 'DELETE' });
}

// ──── Aliases used by pages ────
export const exportExcel = exportWeekExcel;
export const login = adminLogin;
export const sendReminder = sendWeekReminders;

export default {
  adminLogin,
  adminLogout,
  getAdminProfile,
  fetchGuards,
  fetchGuard,
  createGuard,
  updateGuard,
  deleteGuard,
  fetchWeeks,
  fetchWeek,
  createWeek,
  updateWeekStatus,
  sendWeekReminders,
  lockWeek,
  unlockWeek,
  deleteWeek,
  fetchSubmissions,
  fetchSubmissionsDetailed,
  sendNotifications,
  exportWeekExcel,
  fetchSettings,
  updateSettings,
  fetchAdmins,
  createAdmin,
  deleteAdmin,
};