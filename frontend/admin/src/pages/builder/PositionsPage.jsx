import { useState, useEffect, useCallback } from 'react';
import {
  listProfiles,
  listPositions,
  createPosition,
  updatePosition,
  deletePosition,
  listAttributes,
  createAttribute,
  deleteAttribute,
} from '../../api/builderApiClient';
import { useToast } from '../../components/Toast';
import ConfirmDialog from '../../components/ConfirmDialog';
import messages from '../../utils/messages';
import {
  DAY_NAMES_SHORT as DAY_NAMES,
  DAY_HALF_HOUR_OPTIONS,
} from '../../utils/guardMessages.js';

// Build a blank editor form, optionally seeded from an existing position.
function makeForm(position) {
  const days = {};
  for (let i = 0; i < 7; i += 1) {
    const key = String(i);
    const existing = position?.day_schedules?.[key];
    days[i] = {
      active: !!existing,
      start: existing?.start || '07:00',
      end: existing?.end || '15:00',
    };
  }
  return {
    id: position?.id || null,
    name: position?.name || '',
    days,
    required: new Set(position?.required_attributes || []),
  };
}

// Duration of a shift in hours, treating the end as always *after* the start:
// the security day runs 07:00 → 07:00, so an end at/<= start wraps to the next
// day (07:00→17:00 = 10h; 23:00→07:00 = 8h; 07:00→07:00 = a full 24h).
function shiftHours(start, end) {
  const toMin = (t) => {
    const [h, m] = t.split(':').map(Number);
    return h * 60 + m;
  };
  let diff = (toMin(end) - toMin(start) + 1440) % 1440;
  if (diff === 0) diff = 1440;
  const h = diff / 60;
  return Number.isInteger(h) ? h : h.toFixed(1);
}

// Collapse the editor's day grid into the API's day_schedules map.
function toDaySchedules(days) {
  const out = {};
  Object.entries(days).forEach(([i, d]) => {
    if (d.active) out[String(i)] = { start: d.start, end: d.end };
  });
  return out;
}

function daySummary(daySchedules) {
  const active = Object.keys(daySchedules || {})
    .map(Number)
    .sort((a, b) => a - b);
  if (!active.length) return '—';
  return active.map((i) => DAY_NAMES[i]).join(', ');
}

export default function PositionsPage() {
  const toast = useToast();
  const m = messages.positions;

  const [profiles, setProfiles] = useState([]);
  const [profileId, setProfileId] = useState('');
  const [positions, setPositions] = useState([]);
  const [attributes, setAttributes] = useState([]);
  const [loading, setLoading] = useState(true);

  const [editor, setEditor] = useState(null); // editor form or null
  const [confirmDelete, setConfirmDelete] = useState(null);
  const [showAttrs, setShowAttrs] = useState(false);
  const [attrForm, setAttrForm] = useState({ key: '', label: '' });
  const [confirmDeleteAttr, setConfirmDeleteAttr] = useState(null);

  const attrLabel = useCallback(
    (key) => attributes.find((a) => a.key === key)?.label || key,
    [attributes],
  );

  // Initial load: profiles + attributes, then default profile selection.
  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const [profs, attrs] = await Promise.all([listProfiles(), listAttributes()]);
        setProfiles(profs);
        setAttributes(attrs);
        const def = profs.find((p) => p.is_default) || profs[0];
        setProfileId(def ? def.id : '');
      } catch (err) {
        toast.error(err.message || messages.common.error);
      } finally {
        setLoading(false);
      }
    })();
  }, [toast]);

  const loadPositions = useCallback(async () => {
    if (!profileId) {
      setPositions([]);
      return;
    }
    try {
      setPositions(await listPositions(profileId));
    } catch (err) {
      toast.error(err.message || messages.common.error);
    }
  }, [profileId, toast]);

  useEffect(() => {
    loadPositions();
  }, [loadPositions]);

  const refreshAttrs = async () => {
    try {
      setAttributes(await listAttributes());
    } catch (err) {
      toast.error(err.message || messages.common.error);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    const body = {
      name: editor.name.trim(),
      day_schedules: toDaySchedules(editor.days),
      required_attributes: Array.from(editor.required),
    };
    if (!body.name) return;
    if (!Object.keys(body.day_schedules).length) {
      toast.error(m.needOneDay);
      return;
    }
    try {
      if (editor.id) {
        await updatePosition(editor.id, body);
        toast.success(m.updated);
      } else {
        await createPosition(profileId, body);
        toast.success(m.created);
      }
      setEditor(null);
      await loadPositions();
    } catch (err) {
      toast.error(err.message || messages.common.error);
    }
  };

  const handleDelete = async () => {
    const p = confirmDelete;
    setConfirmDelete(null);
    try {
      await deletePosition(p.id);
      toast.success(m.deleted);
      await loadPositions();
    } catch (err) {
      toast.error(err.message || messages.common.error);
    }
  };

  const handleAddAttr = async (e) => {
    e.preventDefault();
    if (!attrForm.key.trim() || !attrForm.label.trim()) return;
    try {
      await createAttribute({ key: attrForm.key.trim(), label: attrForm.label.trim() });
      setAttrForm({ key: '', label: '' });
      toast.success(m.attrCreated);
      await refreshAttrs();
    } catch (err) {
      toast.error(err.message || messages.common.error);
    }
  };

  const handleDeleteAttr = async () => {
    const a = confirmDeleteAttr;
    setConfirmDeleteAttr(null);
    try {
      await deleteAttribute(a.id);
      toast.success(m.attrDeleted);
      await refreshAttrs();
    } catch (err) {
      toast.error(err.message || messages.common.error);
    }
  };

  const toggleRequirement = (key) => {
    setEditor((prev) => {
      const required = new Set(prev.required);
      if (required.has(key)) required.delete(key);
      else required.add(key);
      return { ...prev, required };
    });
  };

  const setDay = (i, patch) => {
    setEditor((prev) => ({
      ...prev,
      days: { ...prev.days, [i]: { ...prev.days[i], ...patch } },
    }));
  };

  if (loading) return <div className="loading">{messages.common.loading}</div>;

  return (
    <div className="page">
      <div className="page-header">
        <h2>{m.title}</h2>
        <p className="page-subtitle">{m.subtitle}</p>
      </div>

      <div className="positions-toolbar">
        <label htmlFor="profile-select">{m.profile}</label>
        <select
          id="profile-select"
          aria-label={m.profile}
          value={profileId}
          onChange={(e) => setProfileId(e.target.value)}
        >
          {profiles.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
        <button
          className="btn btn-primary"
          disabled={!profileId}
          onClick={() => setEditor(makeForm())}
        >
          {m.newPosition}
        </button>
        <button className="btn btn-secondary" onClick={() => setShowAttrs(true)}>
          {m.manageAttrs}
        </button>
      </div>

      {!positions.length ? (
        <p className="empty-state">{m.empty}</p>
      ) : (
        <div className="position-cards">
          {positions.map((p) => (
            <div key={p.id} className="position-card">
              <div className="position-card-header">
                <span className="position-card-name">{p.name}</span>
              </div>
              <p className="position-card-days">{daySummary(p.day_schedules)}</p>
              {p.required_attributes?.length > 0 && (
                <div className="position-card-tags">
                  {p.required_attributes.map((key) => (
                    <span key={key} className="position-tag">
                      {attrLabel(key)}
                    </span>
                  ))}
                </div>
              )}
              <div className="position-card-actions">
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => setEditor(makeForm(p))}
                >
                  {m.edit}
                </button>
                <button
                  className="btn btn-danger btn-sm"
                  onClick={() => setConfirmDelete(p)}
                >
                  {m.delete}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {editor && (
        <div className="modal-overlay" onClick={() => setEditor(null)}>
          <div className="modal-content modal-wide" onClick={(e) => e.stopPropagation()}>
            <h3 className="modal-title">{editor.id ? m.editTitle : m.addTitle}</h3>
            <form onSubmit={handleSave}>
              <div className="form-group">
                <label htmlFor="pos-name">{m.name}</label>
                <input
                  id="pos-name"
                  type="text"
                  aria-label={m.name}
                  autoFocus
                  placeholder={m.namePlaceholder}
                  value={editor.name}
                  onChange={(e) => setEditor({ ...editor, name: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label>{m.days}</label>
                <p className="form-hint">{m.hoursHint}</p>
                <div className="day-grid">
                  {DAY_NAMES.map((dayName, i) => (
                    <div key={i} className="day-row">
                      <label className="day-toggle">
                        <input
                          type="checkbox"
                          aria-label={dayName}
                          checked={editor.days[i].active}
                          onChange={(e) => setDay(i, { active: e.target.checked })}
                        />
                        {dayName}
                      </label>
                      <select
                        aria-label={`${dayName}-${m.start}`}
                        disabled={!editor.days[i].active}
                        value={editor.days[i].start}
                        onChange={(e) => setDay(i, { start: e.target.value })}
                      >
                        {DAY_HALF_HOUR_OPTIONS.map((t) => (
                          <option key={t} value={t}>
                            {t}
                          </option>
                        ))}
                      </select>
                      <select
                        aria-label={`${dayName}-${m.end}`}
                        disabled={!editor.days[i].active}
                        value={editor.days[i].end}
                        onChange={(e) => setDay(i, { end: e.target.value })}
                      >
                        {DAY_HALF_HOUR_OPTIONS.map((t) => (
                          <option key={t} value={t}>
                            {t}
                          </option>
                        ))}
                      </select>
                      <span className="day-duration">
                        {editor.days[i].active
                          ? `${shiftHours(editor.days[i].start, editor.days[i].end)} ${m.hours}`
                          : ''}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="form-group">
                <label>{m.requirements}</label>
                {!attributes.length ? (
                  <p className="empty-state">{m.noRequirements}</p>
                ) : (
                  <div className="requirement-checks">
                    {attributes.map((a) => (
                      <label key={a.id} className="requirement-check">
                        <input
                          type="checkbox"
                          aria-label={a.label}
                          checked={editor.required.has(a.key)}
                          onChange={() => toggleRequirement(a.key)}
                        />
                        {a.label}
                      </label>
                    ))}
                  </div>
                )}
              </div>

              <div className="modal-actions">
                <button type="submit" className="btn btn-primary" disabled={!editor.name.trim()}>
                  {messages.common.save}
                </button>
                <button type="button" className="btn btn-secondary" onClick={() => setEditor(null)}>
                  {messages.common.cancel}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showAttrs && (
        <div className="modal-overlay" onClick={() => setShowAttrs(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3 className="modal-title">{m.attrsTitle}</h3>
            <form className="attr-create-form" onSubmit={handleAddAttr}>
              <input
                type="text"
                aria-label={m.attrKey}
                placeholder={m.attrKeyPlaceholder}
                value={attrForm.key}
                onChange={(e) => setAttrForm({ ...attrForm, key: e.target.value })}
              />
              <input
                type="text"
                aria-label={m.attrLabel}
                placeholder={m.attrLabelPlaceholder}
                value={attrForm.label}
                onChange={(e) => setAttrForm({ ...attrForm, label: e.target.value })}
              />
              <button
                type="submit"
                className="btn btn-primary btn-sm"
                disabled={!attrForm.key.trim() || !attrForm.label.trim()}
              >
                {m.addAttr}
              </button>
            </form>
            {!attributes.length ? (
              <p className="empty-state">{m.noAttrs}</p>
            ) : (
              <ul className="attr-list">
                {attributes.map((a) => (
                  <li key={a.id} className="attr-list-item">
                    <span>
                      {a.label} <code>{a.key}</code>
                    </span>
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => setConfirmDeleteAttr(a)}
                    >
                      {m.delete}
                    </button>
                  </li>
                ))}
              </ul>
            )}
            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={() => setShowAttrs(false)}>
                {messages.common.cancel}
              </button>
            </div>
          </div>
        </div>
      )}

      <ConfirmDialog
        open={!!confirmDelete}
        title={m.deleteTitle}
        message={m.deleteMsg}
        confirmLabel={m.delete}
        onConfirm={handleDelete}
        onCancel={() => setConfirmDelete(null)}
      />
      <ConfirmDialog
        open={!!confirmDeleteAttr}
        title={m.deleteAttrTitle}
        message={m.deleteAttrMsg}
        confirmLabel={m.delete}
        onConfirm={handleDeleteAttr}
        onCancel={() => setConfirmDeleteAttr(null)}
      />
    </div>
  );
}
