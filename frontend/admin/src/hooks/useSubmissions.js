import { useState, useCallback } from 'react';
import { fetchSubmissions } from '../api/adminApiClient';

export default function useSubmissions() {
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadForWeek = useCallback(async (weekId) => {
    if (!weekId) { setSubmissions([]); return; }
    try {
      setLoading(true);
      setError(null);
      const data = await fetchSubmissions(weekId);
      setSubmissions(Array.isArray(data) ? data : data.items || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  return { submissions, loading, error, loadForWeek };
}