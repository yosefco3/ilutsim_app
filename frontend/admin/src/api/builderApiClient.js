/**
 * Builder API client — part B (schedule builder).
 *
 * All part-B requests go through this client so the part-A / part-B boundary is
 * explicit on the frontend too. It reuses the shared `request` helper from
 * adminApiClient (single auth / 401 handling path).
 */

import { request } from './adminApiClient';

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

// ── Positions (within a profile) ───────────────────────────────────────

export function listPositions(profileId) {
  return request(`${BASE}/${profileId}/positions`);
}

export function createPosition(profileId, body) {
  return request(`${BASE}/${profileId}/positions`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export function getPosition(id) {
  return request(`/admin/builder/positions/${id}`);
}

export function updatePosition(id, body) {
  return request(`/admin/builder/positions/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(body),
  });
}

export function deletePosition(id) {
  return request(`/admin/builder/positions/${id}`, { method: 'DELETE' });
}

// ── Requirement-attribute vocabulary ───────────────────────────────────

const ATTRS_BASE = '/admin/builder/attributes';

export function listAttributes() {
  return request(ATTRS_BASE);
}

export function createAttribute(body) {
  return request(ATTRS_BASE, { method: 'POST', body: JSON.stringify(body) });
}

export function updateAttribute(id, body) {
  return request(`${ATTRS_BASE}/${id}`, { method: 'PATCH', body: JSON.stringify(body) });
}

export function deleteAttribute(id) {
  return request(`${ATTRS_BASE}/${id}`, { method: 'DELETE' });
}
