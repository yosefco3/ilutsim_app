import messages from '../utils/messages';

export default function StatusGrid({ submissions }) {
  if (!submissions.length) {
    return <p className="empty-state">{messages.submissions.empty}</p>;
  }

  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>{messages.guards.fullName}</th>
          <th>{messages.submissions.status}</th>
          <th>{messages.submissions.submittedAt}</th>
          <th>{messages.submissions.deviations}</th>
        </tr>
      </thead>
      <tbody>
        {submissions.map((s) => (
          <tr key={s.id}>
            <td>{s.user_name || s.user_id}</td>
            <td>
              <span className={`badge ${s.status === 'submitted' ? 'badge-success' : 'badge-warning'}`}>
                {s.status === 'submitted' ? messages.submissions.submitted : messages.submissions.missing}
              </span>
            </td>
            <td>{s.submitted_at ? new Date(s.submitted_at).toLocaleString('he-IL') : '—'}</td>
            <td>{s.has_deviations ? messages.common.yes : messages.common.no}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}