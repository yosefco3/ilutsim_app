import { useWeeks } from '../hooks/useWeeks';
import WeekStatusControl from '../components/WeekStatusControl';
import messages from '../utils/messages';

export default function WeeksPage() {
  const { weeks, loading, setStatus, openForSubmission, publish, remind, reload } = useWeeks();

  const handleOpen = async (weekId) => {
    await openForSubmission(weekId);
  };

  const handleLock = async (weekId) => {
    await setStatus(weekId, 'locked');
  };

  const handlePublish = async (weekId) => {
    await publish(weekId);
  };

  const handleRemind = async (weekId) => {
    await remind(weekId);
  };

  if (loading) return <div className="loading">{messages.common.loading}</div>;

  return (
    <div className="page">
      <h2>{messages.weeks.title}</h2>
      <button className="btn btn-outline btn-sm" onClick={reload} style={{ marginBottom: '1rem' }}>
        {messages.common.refresh || 'Refresh'}
      </button>
      {!weeks.length ? (
        <p className="empty-state">{messages.weeks.empty}</p>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>{messages.weeks.weekLabel}</th>
              <th>{messages.weeks.startDate}</th>
              <th>{messages.weeks.endDate}</th>
              <th>{messages.weeks.status}</th>
              <th>{messages.common.actions}</th>
            </tr>
          </thead>
          <tbody>
            {weeks.map((w) => (
              <tr key={w.id}>
                <td>{w.week_label}</td>
                <td>{w.start_date}</td>
                <td>{w.end_date}</td>
                <td>
                  <WeekStatusControl
                    week={w}
                    onOpen={handleOpen}
                    onLock={handleLock}
                    onPublish={handlePublish}
                    loading={loading}
                  />
                </td>
                <td>
                  {w.status === 'open' && (
                    <button className="btn btn-outline btn-sm" onClick={() => handleRemind(w.id)}>
                      {messages.weeks.remind || 'Remind'}
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}