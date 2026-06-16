/**
 * Builder API client — part B (schedule builder).
 *
 * All part-B requests go through this client so the part-A / part-B boundary is
 * explicit on the frontend too. It reuses the shared `request` helper from
 * adminApiClient (single auth / 401 handling path).
 */

import { request } from './adminApiClient';

export { request };

const BASE = '/admin/builder/profiles';

export function listProfiles() {
  return request(BASE);
}

export function createProfile(body) {
  return request(BASE, { method: 'POST', body: JSON.stringify(body) });
}

export function getProfile(id) {
  return request(`${BASE}/${id}`);
}

export function updateProfile(id, body) {
  return request(`${BASE}/${id}`, { method: 'PATCH', body: JSON.stringify(body) });
}

export function duplicateProfile(id, body = {}) {
  return request(`${BASE}/${id}/duplicate`, { method: 'POST', body: JSON.stringify(body) });
}

export function deleteProfile(id) {
  return request(`${BASE}/${id}`, { method: 'DELETE' });
}
