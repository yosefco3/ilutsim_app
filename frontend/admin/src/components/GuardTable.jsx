import messages from '../utils/messages';

export default function GuardTable({ guards, onEdit, onToggle, onDelete }) {
  if (!guards.length) {
    return <p className="empty-state">{messages.guards.empty}</p>;
  }

  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>{messages.guards.fullName}</th>
          <th>{messages.guards.phone}</th>
          <th>{messages.guards.telegramId}</th>
          <th>{messages.guards.active}</th>
          <th>{messages.common.actions}</th>
        </tr>
      </thead>
      <tbody>
        {guards.map((g) => (
          <tr key={g.id}>
            <td>{g.full_name}</td>
            <td>{g.phone || '—'}</td>
            <td>{g.telegram_chat_id || '—'}</td>
            <td>
              <span className={`badge ${g.is_active ? 'badge-success' : 'badge-secondary'}`}>
                {g.is_active ? messages.common.yes : messages.common.no}
              </span>
            </td>
            <td className="actions-cell">
              <button className="btn btn-sm btn-primary" onClick={() => onEdit(g)}>
                {messages.common.edit}
              </button>
              <button className="btn btn-sm btn-secondary" onClick={() => onToggle(g)}>
                {g.is_active ? messages.guards.deactivate : messages.guards.activate}
              </button>
              <button className="btn btn-sm btn-danger" onClick={() => onDelete(g)}>
                {messages.common.delete}
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}