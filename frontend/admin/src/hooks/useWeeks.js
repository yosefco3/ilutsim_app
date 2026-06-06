import { useState, useEffect, useCallback } from 'react';
import { fetchWeeks, createWeek, updateWeekStatus, sendWeekReminders, openNewWeek, publishWeek } from '../api/adminApiClient';

export function useWeeks() {
  const [weeks, setWeeks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchWeeks();
      setWeeks(Array.isArray(data) ? data : data.items || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const add = async (weekData) => {
    const created = await createWeek(weekData);
    setWeeks((prev) => [...prev, created]);
    return created;
  };

  const setStatus = async (id, status) => {
    const updated = await updateWeekStatus(id, status);
    setWeeks((prev) => prev.map((w) => (w.id === id ? { ...w, ...updated } : w)));
    return updated;
  };

  const remind = async (id) => {
    return sendWeekReminders(id);
  };

  const openForSubmission = async (id) => {
    const updated = await openNewWeek(id);
    setWeeks((prev) => prev.map((w) => (w.id === id ? { ...w, ...updated } : w)));
    return updated;
  };

  const publish = async (id) => {
    const updated = await publishWeek(id);
    setWeeks((prev) => prev.map((w) => (w.id === id ? { ...w, ...updated } : w)));
    return updated;
  };

  return { weeks, loading, error, reload: load, addWeek: add, setStatus, remind, openForSubmission, publish };
}