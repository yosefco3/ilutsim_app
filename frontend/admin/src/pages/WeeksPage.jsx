import { useWeeks } from '../hooks/useWeeks';
import WeekStatusControl from '../components/WeekStatusControl';
import messages from '../utils/messages';

export default function WeeksPage() {
  const { weeks, loading, setStatus, openForSubmission, publish, deleteWeek, reload } = useWeeks();

  const handleOpen = async (weekId) => {
    await openForSubmission(weekId);
  };

  const handleLock = async (weekId) => {
    await setStatus(weekId, 'locked');
  };

  const handlePublish = async (weekId) => {
    await publish(weekId);
  };

  const handleDelete = async (weekId) => {
    await deleteWeek(weekId);
  };

  if (loading) return <div className="loading">{messages.common.loading}</div>;

  return (
    <div className="page">
      <div className="page-header">
        <h2>{messages.weeks.title}</h2>
        <button className="btn btn-outline btn-sm" onClick={reload}>
          {messages.common.refresh || 'Refresh'}
        </button>
      </div>

      {!weeks.length ? (
        <p className="empty-state">{messages.weeks.empty}</p>
      ) : (
        <div className="week-cards">
          {weeks.map((w) => (
            <div key={w.id} className="week-card">
              <div className="week-card-header">
                <span className="week-card-date">📅 {w.start_date} — {w.end_date}</span>
                <span className="week-card-label">{w.week_label}</span>
              </div>
              <div className="week-card-body">
                <span className="week-card-submissions">
                  {messages.weeks.submissionCount ? `${w.submission_count ?? 0} ${messages.weeks.submissionCount}` : `${w.submission_count ?? 0} הגשות`}
                </span>
              </div>
              <WeekStatusControl
                week={w}
                onOpen={handleOpen}
                onLock={handleLock}
                onPublish={handlePublish}
                onDelete={handleDelete}
                loading={loading}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}