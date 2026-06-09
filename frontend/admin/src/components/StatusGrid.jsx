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
        </tr>
      </thead>
      <tbody>
        {submissions.map((s) => (
          <tr key={s.user_id}>
            <td>{s.full_name || s.user_id}</td>
            <td>
              <span className={`badge ${s.submitted_at ? 'badge-success' : 'badge-warning'}`}>
                {s.submitted_at ? messages.submissions.submitted : messages.submissions.missing}
              </span>
            </td>
            <td>{s.submitted_at ? new Date(s.submitted_at).toLocaleString('he-IL') : '—'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
