import { Fragment, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import messages from '../utils/messages';
import { DAY_NAMES, SHIFT_LABELS } from '../utils/guardMessages';

export default function StatusGrid({ submissions, detailsByUser = {}, canFillConstraints = false }) {
  const [expandedUser, setExpandedUser] = useState(null);
  const navigate = useNavigate();

  // Detail row spans all columns; the actions column only exists when the
  // selected week is editable (the relevant 'open' week).
  const colCount = canFillConstraints ? 5 : 4;

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
          <th>{messages.submissions.viewDetails}</th>
          {canFillConstraints && <th>{messages.common.actions}</th>}
        </tr>
      </thead>
      <tbody>
        {submissions.map((s) => {
          const detail = detailsByUser[s.user_id];
          const expanded = expandedUser === s.user_id;
          return (
            <Fragment key={s.user_id}>
              <tr>
                <td>{s.full_name || s.user_id}</td>
                <td>
                  <span className={`badge ${s.submitted_at ? 'badge-success' : 'badge-warning'}`}>
                    {s.submitted_at ? messages.submissions.submitted : messages.submissions.missing}
                  </span>
                </td>
                <td>{s.submitted_at ? new Date(s.submitted_at).toLocaleString('he-IL') : '—'}</td>
                <td>
                  {detail ? (
                    <button
                      className="btn-sm"
                      onClick={() => setExpandedUser(expanded ? null : s.user_id)}
                    >
                      {expanded ? 'הסתר' : 'הצג'}
                    </button>
                  ) : (
                    <span className="text-muted">—</span>
                  )}
                </td>
                {canFillConstraints && (
                  <td className="actions-cell">
                    <button
                      className="btn btn-sm btn-secondary"
                      onClick={() => navigate(`/guards/${s.user_id}/constraints`)}
                    >
                      {messages.guards.fillConstraints}
                    </button>
                  </td>
                )}
              </tr>
              {expanded && detail && (
                <tr className="detail-row">
                  <td colSpan={colCount}>
                    <div className="detail-content">
                      {detail.days?.map((day, idx) => (
                        <div key={idx} className="detail-day">
                          <strong>{DAY_NAMES[idx] || `יום ${idx}`}</strong>
                          {day.shift_windows && day.shift_windows.length > 0 ? (
                            <ul>
                              {day.shift_windows.map((sw, si) => (
                                <li key={si}>
                                  {SHIFT_LABELS[sw.shift_type] || sw.shift_type}: {sw.start_time} - {sw.end_time}
                                </li>
                              ))}
                            </ul>
                          ) : (
                            <span className="text-muted"> לא זמין</span>
                          )}
                        </div>
                      ))}
                      {detail.general_notes && (
                        <div className="detail-notes">
                          <strong>הערות:</strong> {detail.general_notes}
                        </div>
                      )}
                    </div>
                  </td>
                </tr>
              )}
            </Fragment>
          );
        })}
      </tbody>
    </table>
  );
}
