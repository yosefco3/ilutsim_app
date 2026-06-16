/**
 * Builder API client — part B (schedule builder).
 *
 * All part-B requests go through this client so the part-A / part-B boundary is
 * explicit on the frontend too. It reuses the shared `request` helper from
 * adminApiClient (single auth / 401 handling path).
 *
 * Endpoints are added alongside the screens that need them (see prompt 04:
 * profiles CRUD). Empty for now — only re-exports the shared base.
 */

export { request } from './adminApiClient';
