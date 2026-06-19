import { useState, useEffect, useRef } from 'react';
import { useWeeks } from '../hooks/useWeeks';
import { useSubmissions } from '../hooks/useSubmissions';
import StatusGrid from '../components/StatusGrid';
import { useToast } from '../components/Toast';
import { sendWeekReminders, fetchConstraintRules } from '../api/adminApiClient';
import messages from '../utils/messages';

export default function SubmissionsPage() {
  const { weeks, loading: weeksLoading } = useWeeks();
  const [selectedWeek, setSelectedWeek] = useState('');
  const { submissions, detailedData, loading: subsLoading } = useSubmissions(selectedWeek, { detailed: true });
  const toast = useToast();
  const [reminding, setReminding] = useState(false);

  const [showInactive, setShowInactive] = useState(false);

  // Constraint-rule thresholds — drive the soft warnings shown per submission.
  // Fetched once; failure is silent (warnings simply won't appear).
  const [rules, setRules] = useState(null);
  useEffect(() => {
    fetchConstraintRules().then(setRules).catch(() => {});
  }, []);

  // Default the week selector to the relevant week (the single 'open' one) once
  // weeks load — that's the week the admin almost always wants, and it makes the
  // "מילוי אילוצים" button show immediately. Runs once; the admin can still pick
  // another week. If no week is open, stay on the "choose week" prompt.
  const didInitWeek = useRef(false);
  useEffect(() => {
    if (didInitWeek.current || !weeks.length) return;
    didInitWeek.current = true;
    const open = weeks.find((w) => w.status === 'open');
    if (open) setSelectedWeek(String(open.id));
  }, [weeks]);

  const loading = weeksLoading || subsLoading;

  // Admins may fill and edit constraints while a week is 'closed' / 'open' /
  // 'locked' — only a 'published' week is final and locks editing for everyone
  // (matches the backend: create_submission(override_lock=True) rejects only
  // PUBLISHED, and AdminConstraintsPage which gates solely on 'published').
  // Regular guards are still blocked once the week is locked; that gate lives
  // on the guard side, not here.
  const selectedWeekObj = weeks.find((w) => String(w.id) === String(selectedWeek));
  const canFillConstraints = !!selectedWeekObj && selectedWeekObj.status !== 'published';

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
      } else if (result?.skipped_no_telegram > 0) {
        // Someone still hasn't submitted but has no Telegram linked, so no
        // reminder could be delivered — say so instead of "everyone submitted".
        toast.info(`${messages.submissions.reminderNoTelegram} (${result.skipped_no_telegram})`);
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
            rules={rules}
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
                  rules={rules}
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