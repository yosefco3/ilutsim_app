import { useSettings } from '../hooks/useSettings';
import messages from '../utils/messages';

export default function SettingsPage() {
  const { settings, loading, updateSetting } = useSettings();

  if (loading) return <div className="loading">{messages.common.loading}</div>;

  return (
    <div className="page">
      <h2>{messages.settings.title}</h2>
      {!settings.length ? (
        <p className="empty-state">{messages.settings.empty}</p>
      ) : (
        <div className="settings-list">
          {settings.map((s) => (
            <div key={s.key} className="card settings-item">
              <div className="settings-info">
                <strong>{s.key}</strong>
                {s.description && <p className="text-muted">{s.description}</p>}
              </div>
              <div className="settings-value">
                <input
                  type="text"
                  value={s.value}
                  onChange={(e) => updateSetting(s.key, e.target.value)}
                  className="settings-input"
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}