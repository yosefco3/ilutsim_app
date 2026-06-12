import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useWeeks } from '../hooks/useWeeks';
import { useSubmissions } from '../hooks/useSubmissions';
import StatusGrid from '../components/StatusGrid';
import messages from '../utils/messages';

export default function SubmissionsPage() {
  const { weeks, loading: weeksLoading } = useWeeks();
  const [selectedWeek, setSelectedWeek] = useState('');
  const { submissions, loading: subsLoading } = useSubmissions(selectedWeek);

  const loading = weeksLoading || subsLoading;

  return (
    <div className="page">
      <h2>{messages.submissions.title}</h2>
      <div className="form-group">
        <label>{messages.submissions.selectWeek}</label>
        <select value={selectedWeek} onChange={(e) => setSelectedWeek(e.target.value)}>
          <option value="">{messages.submissions.chooseWeek}</option>
          {weeks.map((w) => (
            <option key={w.id} value={w.id}>{w.week_label}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="loading">{messages.common.loading}</div>
      ) : selectedWeek ? (
        <>
          <div className="form-group">
            <Link to={`/submissions/${selectedWeek}`} className="btn btn-primary btn-sm">
              {messages.submissions.viewDetails}
            </Link>
          </div>
          <StatusGrid submissions={submissions} />
        </>
      ) : (
        <p className="empty-state">{messages.submissions.selectWeekPrompt}</p>
      )}
    </div>
  );
}