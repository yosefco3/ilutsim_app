import { useState } from 'react';
import { useSettings } from '../hooks/useSettings';
import ChangePasswordForm from '../components/ChangePasswordForm';
import messages from '../utils/messages';

// Weekday options for the auto open/lock selects — value matches the backend
// (English lowercase), label is Hebrew.
const WEEKDAYS = [
  ['sunday', 'ראשון'],
  ['monday', 'שני'],
  ['tuesday', 'שלישי'],
  ['wednesday', 'רביעי'],
  ['thursday', 'חמישי'],
  ['friday', 'שישי'],
  ['saturday', 'שבת'],
];

// Maps each setting key to the control used to edit it. Keys not listed here
// (e.g. the shift_default_* ranges) fall back to a plain text input.
const FIELD_TYPES = {
  notifications_enabled: 'bool',
  auto_open_enabled: 'bool',
  auto_lock_enabled: 'bool',
  auto_open_weekday: 'weekday',
  auto_lock_weekday: 'weekday',
  auto_open_time: 'time',
  auto_lock_time: 'time',
  min_shifts_per_guard: 'number',
  min_nights: 'number',
  min_evenings: 'number',
  max_consecutive_days: 'number',
};

// Logical grouping for the page — each section renders only the keys that the
// API actually returned, so unknown keys never vanish (see fallback below).
const GROUPS = [
  { title: 'התראות', keys: ['notifications_enabled'] },
  {
    title: 'ברירות מחדל למשמרות',
    keys: ['shift_default_morning', 'shift_default_afternoon', 'shift_default_night'],
  },
  {
    title: 'כללי שיבוץ',
    keys: ['min_shifts_per_guard', 'min_nights', 'min_evenings', 'max_consecutive_days'],
  },
  {
    title: 'פתיחה אוטומטית של שבוע',
    keys: ['auto_open_enabled', 'auto_open_weekday', 'auto_open_time'],
  },
  {
    title: 'נעילה אוטומטית של שבוע',
    keys: ['auto_lock_enabled', 'auto_lock_weekday', 'auto_lock_time'],
  },
];

const isOn = (value) => String(value).toLowerCase() === 'true';

function SettingControl({ item, value, onChange }) {
  const type = FIELD_TYPES[item.key] || 'text';

  if (type === 'bool') {
    const on = isOn(value);
    return (
      <button
        type="button"
        role="switch"
        aria-checked={on}
        className={`switch ${on ? 'on' : 'off'}`}
        onClick={() => onChange(item.key, on ? 'false' : 'true')}
      >
        <span className="switch-track"><span className="switch-thumb" /></span>
        <span className="switch-label">{on ? messages.common.yes : messages.common.no}</span>
      </button>
    );
  }

  if (type === 'weekday') {
    return (
      <select
        className="settings-input"
        value={value ?? ''}
        onChange={(e) => onChange(item.key, e.target.value)}
      >
        {WEEKDAYS.map(([val, label]) => (
          <option key={val} value={val}>{label}</option>
        ))}
      </select>
    );
  }

  return (
    <input
      type={type === 'number' ? 'number' : type === 'time' ? 'time' : 'text'}
      value={value ?? ''}
      onChange={(e) => onChange(item.key, e.target.value)}
      className="settings-input"
    />
  );
}

export default function SettingsPage() {
  const { settings, draft, loading, saving, error, dirty, setValue, save } = useSettings();
  const [saved, setSaved] = useState(false);

  if (loading) return <div className="loading">{messages.common.loading}</div>;

  const handleSave = async () => {
    const ok = await save();
    if (ok) {
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    }
  };

  const byKey = Object.fromEntries(settings.map((s) => [s.key, s]));
  const grouped = new Set(GROUPS.flatMap((g) => g.keys));
  const sections = GROUPS
    .map((g) => ({ title: g.title, items: g.keys.map((k) => byKey[k]).filter(Boolean) }))
    .filter((g) => g.items.length);
  // Anything the backend returns that we didn't place in a group still shows up.
  const leftovers = settings.filter((s) => !grouped.has(s.key));
  if (leftovers.length) sections.push({ title: 'נוספות', items: leftovers });

  const renderItem = (s) => (
    <div key={s.key} className="settings-item">
      <div className="settings-info">
        <strong>{messages.settings.labels[s.key] || s.key}</strong>
        {s.description && <p className="text-muted">{s.description}</p>}
      </div>
      <div className="settings-value">
        <SettingControl item={s} value={draft[s.key]} onChange={setValue} />
      </div>
    </div>
  );

  return (
    <div className="page">
      <h2>{messages.settings.title}</h2>
      {error && <div className="error-banner">{error}</div>}
      {saved && <div className="success-banner">{messages.settings.saved}</div>}

      {!settings.length ? (
        <p className="empty-state">{messages.settings.empty}</p>
      ) : (
        <>
          <div className="settings-groups">
            {sections.map((section) => (
              <div key={section.title} className="card settings-group">
                <h3 className="settings-group-title">{section.title}</h3>
                <div className="settings-list">
                  {section.items.map(renderItem)}
                </div>
              </div>
            ))}
          </div>
          <div className="settings-actions">
            <button
              type="button"
              className="btn btn-primary"
              disabled={!dirty || saving}
              onClick={handleSave}
            >
              {saving ? messages.common.loading : messages.settings.save}
            </button>
          </div>
        </>
      )}

      <ChangePasswordForm />
    </div>
  );
}
