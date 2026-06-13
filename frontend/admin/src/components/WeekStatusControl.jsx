/**
 * WeekStatusControl — status badge + action buttons for a single week card.
 *
 * Props: week, onOpen, onLock, onPublish, onDelete, loading
 */
import { useState } from 'react';
import messages from '../utils/messages';
import ConfirmDialog from './ConfirmDialog';

const STATUS_CFG = {
  closed:    { label: messages.weeks.statusClosed,    bg: '#e2e3e5', color: '#383d41', icon: '⏳' },
  open:      { label: messages.weeks.statusOpen,      bg: '#d4edda', color: '#155724', icon: '🔓' },
  locked:    { label: messages.weeks.statusLocked,    bg: '#fff3cd', color: '#856404', icon: '🔒' },
  published: { label: messages.weeks.publishedLabel,   bg: '#cce5ff', color: '#004085', icon: '📢' },
};

export default function WeekStatusControl({ week, onOpen, onLock, onPublish, onDelete, loading }) {
  const status = week.status || 'closed';
  const cfg = STATUS_CFG[status] || STATUS_CFG.closed;
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
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

        {/* Action buttons by status */}
        <div className="week-card-buttons">
          {(status === 'locked' || status === 'closed') && (
            <button
              className="btn btn-primary btn-sm"
              disabled={loading}
              onClick={() => onOpen(week.id)}
            >
              🟢 {messages.weeks.openForSubmission}
            </button>
          )}

          {status === 'open' && (
            <button
              className="btn btn-warning btn-sm"
              disabled={loading}
              onClick={() => onLock(week.id)}
            >
              🔒 {messages.weeks.lock}
            </button>
          )}

          {status === 'locked' && (
            <button
              className="btn btn-success btn-sm"
              disabled={loading}
              onClick={() => setShowPublishConfirm(true)}
            >
              📢 {messages.weeks.published}
            </button>
          )}

          {/* Delete — not allowed for published weeks (kept for history) */}
          {status !== 'published' && (
            <button
              className="btn btn-danger btn-sm"
              disabled={loading}
              onClick={() => setShowDeleteConfirm(true)}
            >
              🗑️ {messages.weeks.delete}
            </button>
          )}
        </div>
      </div>

      {showDeleteConfirm && (
        <ConfirmDialog
          title={messages.weeks.delete}
          message={messages.weeks.deleteConfirm}
          confirmLabel={messages.common.delete}
          onConfirm={() => { setShowDeleteConfirm(false); onDelete(week.id); }}
          onCancel={() => setShowDeleteConfirm(false)}
        />
      )}

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