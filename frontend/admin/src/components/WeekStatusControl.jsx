import messages from '../utils/messages';

const STATUS_FLOW = ['draft', 'open', 'closed', 'published'];

const STATUS_LABELS = {
  draft: messages.weeks.statusDraft,
  open: messages.weeks.statusOpen,
  closed: messages.weeks.statusClosed,
  published: messages.weeks.statusPublished,
};

const STATUS_BADGE = {
  draft: 'badge-secondary',
  open: 'badge-info',
  closed: 'badge-warning',
  published: 'badge-success',
};

export default function WeekStatusControl({ week, onStatusChange, onRemind }) {
  if (!week) return null;

  const idx = STATUS_FLOW.indexOf(week.status);
  const nextStatus = idx < STATUS_FLOW.length - 1 ? STATUS_FLOW[idx + 1] : null;

  return (
    <div className="week-status-control">
      <span className={`badge ${STATUS_BADGE[week.status] || 'badge-secondary'}`}>
        {STATUS_LABELS[week.status] || week.status}
      </span>
      {nextStatus && (
        <button
          className="btn btn-sm btn-primary"
          onClick={() => onStatusChange(week.id, nextStatus)}
        >
          {messages.common.moveTo} {STATUS_LABELS[nextStatus]}
        </button>
      )}
      {week.status === 'open' && (
        <button className="btn btn-sm btn-secondary" onClick={() => onRemind(week.id)}>
          {messages.weeks.sendReminder}
        </button>
      )}
    </div>
  );
}