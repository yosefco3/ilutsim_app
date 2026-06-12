import { useState, useEffect } from 'react';
import { fetchSubmissions, fetchSubmissionsDetailed } from '../api/adminApiClient';

export function useSubmissions(weekId, { detailed = false } = {}) {
  const [submissions, setSubmissions] = useState([]);
  const [detailedData, setDetailedData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!weekId) {
      setSubmissions([]);
      setDetailedData(null);
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

        if (detailed) {
          const detailedResult = await fetchSubmissionsDetailed(weekId);
          if (!cancelled) {
            setDetailedData(detailedResult);
          }
        }
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [weekId, detailed]);

  return { submissions, detailedData, loading, error };
}