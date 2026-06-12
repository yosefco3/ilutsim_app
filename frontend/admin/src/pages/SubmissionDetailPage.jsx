import { useParams, Link } from 'react-router-dom';
import { useSubmissions } from '../hooks/useSubmissions';
import SubmissionsTable from '../components/SubmissionsTable';

export default function SubmissionDetailPage() {
  const { weekId } = useParams();
  const { submissions, detailedData, loading, error } = useSubmissions(weekId, { detailed: true });

  if (loading) return <div className="loading">טוען...</div>;
  if (error) return <div className="error-banner">שגיאה: {error}</div>;
  if (!detailedData) return <div className="loading">אין נתונים</div>;

  const { submitted, missing, week_label } = detailedData;

  // Build user name map from missing + submitted (both have full_name)
  const userNames = {};
  for (const m of missing) {
    userNames[m.user_id] = m.full_name;
  }
  for (const s of submitted) {
    userNames[s.user_id] = s.full_name;
  }

  return (
    <div className="page">
      <Link to="/submissions" className="back-link">← חזרה לרשימת השבועות</Link>
      <h2>פירוט אילוצים — {week_label}</h2>

      {/* Submitted guards */}
      <section className="section">
        <h3>✅ מאבטחים ששלחו אילוצים ({submitted.length})</h3>
        <SubmissionsTable submissions={submitted} userNames={userNames} />
      </section>

      {/* Missing guards */}
      <section className="section">
        <h3>❌ מאבטחים שלא שלחו אילוצים ({missing.length})</h3>
        {missing.length > 0 ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>שם מלא</th>
                <th>טלפון</th>
                <th>סטטוס</th>
              </tr>
            </thead>
            <tbody>
              {missing.map((m) => (
                <tr key={m.user_id}>
                  <td>{m.full_name}</td>
                  <td>{m.phone_number}</td>
                  <td><span className="badge badge-warning">לא הגיש</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="empty-state">כל המאבטחים הגישו אילוצים! 🎉</p>
        )}
      </section>
    </div>
  );
}