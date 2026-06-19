import { useState } from 'react';
import { useSettings } from '../hooks/useSettings';
import ChangePasswordForm from '../components/ChangePasswordForm';
import messages from '../utils/messages';

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

  return (
    <div className="page">
      <h2>{messages.settings.title}</h2>
      {error && <div className="error-banner">{error}</div>}
      {saved && <div className="success-banner">{messages.settings.saved}</div>}

      {!settings.length ? (
        <p className="empty-state">{messages.settings.empty}</p>
      ) : (
        <>
          <div className="settings-list">
            {settings.map((s) => (
              <div key={s.key} className="card settings-item">
                <div className="settings-info">
                  <strong>{messages.settings.labels[s.key] || s.key}</strong>
                  {s.description && <p className="text-muted">{s.description}</p>}
                </div>
                <div className="settings-value">
                  <input
                    type="text"
                    value={draft[s.key] ?? ''}
                    onChange={(e) => setValue(s.key, e.target.value)}
                    className="settings-input"
                  />
                </div>
              </div>
            ))}
          </div>
          <button
            type="button"
            className="btn-primary"
            disabled={!dirty || saving}
            onClick={handleSave}
          >
            {saving ? messages.common.loading : messages.settings.save}
          </button>
        </>
      )}

      <ChangePasswordForm />
    </div>
  );
}
