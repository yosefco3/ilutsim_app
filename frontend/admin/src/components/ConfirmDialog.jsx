import messages from '../utils/messages';

export default function ConfirmDialog({ open = true, message, onConfirm, onCancel }) {
  if (!open) return null;

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <p>{message}</p>
        <div className="modal-actions">
          <button className="btn btn-danger" onClick={onConfirm}>{messages.common.confirm}</button>
          <button className="btn btn-secondary" onClick={onCancel}>{messages.common.cancel}</button>
        </div>
      </div>
    </div>
  );
}