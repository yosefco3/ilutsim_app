/**
 * WeekStatusControl — status badge + action buttons for a single week card.
 *
 * Props: week, onOpen, onLock, onPublish, loading, autoOpen, autoLock
 *
 * When auto-open/auto-lock is enabled the corresponding manual button is hidden
 * (the scheduler manages it) and a "will happen automatically" indicator is
 * shown instead. "Publish" is always manual.
 */
import { useState } from 'react';
import messages from '../utils/messages';
import { formatSchedule } from '../utils/automation';
import ConfirmDialog from './ConfirmDialog';

const A = messages.weeks.automation;

// 3-state model: CLOSED (reopenable) / OPEN / LOCKED (final).
const STATUS_CFG = {
  closed:    { label: messages.weeks.statusClosed,    bg: '#e2e3e5', color: '#383d41', icon: '⏳' },
  open:      { label: messages.weeks.statusOpen,      bg: '#d4edda', color: '#155724', icon: '🔓' },
  locked:    { label: messages.weeks.statusLocked,    bg: '#fff3cd', color: '#856404', icon: '🔒' },
};

export default function WeekStatusControl({
  week,
  onOpen,
  onLock,
  onPublish,
  loading,
  autoOpen = { enabled: false },
  autoLock = { enabled: false },
}) {
  const status = week.status || 'closed';
  const cfg = STATUS_CFG[status] || STATUS_CFG.closed;
  const [showPublishConfirm, setShowPublishConfirm] = useState(false);

  return (
    <>
      <div className="week-card-actions">
        {/* Status badge */}
        <span
          className="week-status-badge"
          style={{ background: cfg.bg, color: cfg.color }}
        >
          {cfg.icon} {cfg.label}
        </span>

        {/* Action buttons by status (3-state model) */}
        <div className="week-card-buttons">
          {/* CLOSED → can be opened for submission (manually, unless auto-open). */}
          {status === 'closed' && !autoOpen.enabled && (
            <button
              className="btn btn-primary btn-sm"
              disabled={loading}
              onClick={() => onOpen(week.id)}
            >
              🟢 {messages.weeks.openForSubmission}
            </button>
          )}

          {status === 'closed' && autoOpen.enabled && (
            <span className="week-auto-indicator">
              ⏰ {A.willOpenAuto} · {formatSchedule(autoOpen.weekday, autoOpen.time)}
            </span>
          )}

          {/* CLOSED → can be finalized ("publish" → LOCKED, terminal).
              HIDDEN FOR NOW: rollover covers the current need, so the manual
              "publish" button is intentionally hidden from the UI. All wiring
              (handler, confirm dialog, messages, API) is kept intact so we can
              re-enable it later by un-commenting this block. */}
          {/* {status === 'closed' && (
            <button
              className="btn btn-success btn-sm"
              disabled={loading}
              onClick={() => setShowPublishConfirm(true)}
            >
              📢 {messages.weeks.published}
            </button>
          )} */}

          {/* OPEN → can be closed (submission window ends → CLOSED, reopenable). */}
          {status === 'open' && !autoLock.enabled && (
            <button
              className="btn btn-warning btn-sm"
              disabled={loading}
              onClick={() => onLock(week.id)}
            >
              🔒 {messages.weeks.closeForSubmission}
            </button>
          )}

          {status === 'open' && autoLock.enabled && (
            <span className="week-auto-indicator">
              ⏰ {A.willLockAuto} · {formatSchedule(autoLock.weekday, autoLock.time)}
            </span>
          )}

          {/* LOCKED is terminal — no actions. */}
        </div>
      </div>

      {showPublishConfirm && (
        <ConfirmDialog
          title={messages.weeks.publishConfirmTitle}
          message={messages.weeks.publishConfirm}
          confirmLabel={messages.weeks.publishConfirmLabel}
          onConfirm={() => { setShowPublishConfirm(false); onPublish(week.id); }}
          onCancel={() => setShowPublishConfirm(false)}
        />
      )}
    </>
  );
}