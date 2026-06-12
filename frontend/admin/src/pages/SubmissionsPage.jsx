import { useState } from 'react';
import { useWeeks } from '../hooks/useWeeks';
import { useSubmissions } from '../hooks/useSubmissions';
import StatusGrid from '../components/StatusGrid';
import messages from '../utils/messages';

export default function SubmissionsPage() {
  const { weeks, loading: weeksLoading } = useWeeks();
  const [selectedWeek, setSelectedWeek] = useState('');
  const { submissions, detailedData, loading: subsLoading } = useSubmissions(selectedWeek, { detailed: true });

  const loading = weeksLoading || subsLoading;

  // Map each guard's user_id to their detailed submission (days + notes)
  const detailsByUser = {};
  for (const s of detailedData?.submitted || []) {
    detailsByUser[s.user_id] = s;
  }

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
        <StatusGrid submissions={submissions} detailsByUser={detailsByUser} />
      ) : (
        <p className="empty-state">{messages.submissions.selectWeekPrompt}</p>
      )}
    </div>
  );
}