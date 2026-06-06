/**
 * WeekStatusControl — status-aware action buttons for a schedule week.
 *
 * Allowed transitions:
 *   draft   → open   (Open for Submission)
 *   open    → locked (Close Submissions / Lock)
 *   locked  → open   (Reopen)
 *   locked  → published (Publish Schedule)
 */
import messages from '../utils/messages';

const STATUS_LABELS = {
  draft: messages.weeks.statusDraft,
  open: messages.weeks.statusOpen,
  locked: messages.weeks.statusLocked,
  published: messages.weeks.publishedLabel,
};

export default function WeekStatusControl({ week, onOpen, onLock, onPublish, loading }) {
  const status = week.status || 'draft';

  return (
    <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
      <span
        className={`badge badge-${status}`}
        style={{
          padding: '0.25rem 0.6rem',
          borderRadius: '12px',
          fontSize: '0.8rem',
          fontWeight: 600,
          background: status === 'open' ? '#d4edda' : status === 'locked' ? '#fff3cd' : status === 'published' ? '#cce5ff' : '#e2e3e5',
          color: status === 'open' ? '#155724' : status === 'locked' ? '#856404' : status === 'published' ? '#004085' : '#383d41',
        }}
      >
        {STATUS_LABELS[status] || status}
      </span>

      {status === 'draft' && (
        <button
          className="btn btn-primary btn-sm"
          disabled={loading}
          onClick={() => onOpen(week.id)}
        >
          {messages.weeks.openForSubmission}
        </button>
      )}

      {status === 'open' && (
        <button
          className="btn btn-warning btn-sm"
          disabled={loading}
          onClick={() => onLock(week.id)}
        >
          {messages.weeks.lock}
        </button>
      )}

      {status === 'locked' && (
        <>
          <button
            className="btn btn-outline btn-sm"
            disabled={loading}
            onClick={() => onOpen(week.id)}
          >
            {messages.weeks.unlock}
          </button>
          <button
            className="btn btn-success btn-sm"
            disabled={loading}
            onClick={() => onPublish(week.id)}
          >
            {messages.weeks.published}
          </button>
        </>
      )}
    </div>
  );
}