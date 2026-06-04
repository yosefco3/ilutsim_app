import { useWeeks } from '../hooks/useWeeks';
import WeekStatusControl from '../components/WeekStatusControl';
import { sendReminder } from '../api/adminApiClient';
import messages from '../utils/messages';

export default function WeeksPage() {
  const { weeks, loading, changeStatus, refresh } = useWeeks();

  const handleRemind = async (weekId) => {
    await sendReminder(weekId);
    refresh();
  };

  if (loading) return <div className="loading">{messages.common.loading}</div>;

  return (
    <div className="page">
      <h2>{messages.weeks.title}</h2>
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
                    onStatusChange={changeStatus}
                    onRemind={handleRemind}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}