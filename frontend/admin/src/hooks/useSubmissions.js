import { useState, useEffect } from 'react';
import { fetchSubmissions } from '../api/adminApiClient';

export function useSubmissions(weekId) {
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!weekId) {
      setSubmissions([]);
      return;
    }
    let cancelled = false;
    async function load() {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchSubmissions(weekId);
        if (!cancelled) {
          setSubmissions(Array.isArray(data) ? data : data.items || []);
        }
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [weekId]);

  return { submissions, loading, error };
}
