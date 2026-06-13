import { useState } from 'react';
import { useWeeks } from '../hooks/useWeeks';
import { useSubmissions } from '../hooks/useSubmissions';
import StatusGrid from '../components/StatusGrid';
import { useToast } from '../components/Toast';
import { sendWeekReminders } from '../api/adminApiClient';
import messages from '../utils/messages';

export default function SubmissionsPage() {
  const { weeks, loading: weeksLoading } = useWeeks();
  const [selectedWeek, setSelectedWeek] = useState('');
  const { submissions, detailedData, loading: subsLoading } = useSubmissions(selectedWeek, { detailed: true });
  const toast = useToast();
  const [reminding, setReminding] = useState(false);

  const [showInactive, setShowInactive] = useState(false);

  const loading = weeksLoading || subsLoading;

  // Filling constraints is only allowed on the *relevant* week — the single
  // week still 'open' for submissions. A week that already started auto-locks
  // (start_date ≤ today → LOCKED) and a published week is final, so gating on
  // 'open' inherently excludes both "already started" and "published".
  const selectedWeekObj = weeks.find((w) => String(w.id) === String(selectedWeek));
  const canFillConstraints = selectedWeekObj?.status === 'open';

  // Map each guard's user_id to their detailed submission (days + notes)
  const detailsByUser = {};
  for (const s of detailedData?.submitted || []) {
    detailsByUser[s.user_id] = s;
  }

  // Active guards are the default view; inactive guards live in a separate,
  // collapsible list. (Older API responses without is_active count as active.)
  const activeSubmissions = submissions.filter((s) => s.is_active !== false);
  const inactiveSubmissions = submissions.filter((s) => s.is_active === false);

  // Only active guards receive reminders, so count missing among them only.
  const missingCount = activeSubmissions.filter((s) => !s.submitted_at).length;

  async function handleRemind() {
    if (!selectedWeek || reminding) return;
    setReminding(true);
    try {
      const result = await sendWeekReminders(selectedWeek);
      if (result?.reminded > 0) {
        toast.success(`${messages.submissions.reminderSent} (${result.reminded})`);
      } else {
        toast.info(messages.submissions.reminderNone);
      }
    } catch (err) {
      toast.error(messages.common.error + ': ' + err.message);
    } finally {
      setReminding(false);
    }
  }

  return (
    <div className="page">
      <h2>{messages.submissions.title}</h2>
      <div className="form-group">
        <label>{messages.submissions.selectWeek}</label>
        <select value={selectedWeek} onChange={(e) => setSelectedWeek(e.target.value)}>
          <option value="">{messages.submissions.chooseWeek}</option>
          {weeks.map((w) => (
            <option key={w.id} value={w.id}>{w.week_label}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="loading">{messages.common.loading}</div>
      ) : selectedWeek ? (
        <>
          {missingCount > 0 && (
            <div className="submissions-actions">
              <span className="submissions-missing-count">
                <strong>{missingCount}</strong> {messages.submissions.missingCount}
              </span>
              <button className="btn btn-primary" onClick={handleRemind} disabled={reminding}>
                <span aria-hidden="true">🔔</span>
                {reminding ? messages.submissions.reminding : messages.submissions.remind}
              </button>
            </div>
          )}
          <StatusGrid
            submissions={activeSubmissions}
            detailsByUser={detailsByUser}
            canFillConstraints={canFillConstraints}
          />

          {inactiveSubmissions.length > 0 && (
            <div className="inactive-section">
              <button
                type="button"
                className="btn btn-outline inactive-toggle"
                onClick={() => setShowInactive((v) => !v)}
                aria-expanded={showInactive}
              >
                <span aria-hidden="true">{showInactive ? '▾' : '▸'}</span>
                {messages.submissions.inactiveToggle} ({inactiveSubmissions.length})
              </button>
              {showInactive && (
                <StatusGrid
                  submissions={inactiveSubmissions}
                  detailsByUser={detailsByUser}
                  canFillConstraints={canFillConstraints}
                />
              )}
            </div>
          )}
        </>
      ) : (
        <p className="empty-state">{messages.submissions.selectWeekPrompt}</p>
      )}
    </div>
  );
}