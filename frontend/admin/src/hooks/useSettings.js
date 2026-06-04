import { useState, useEffect, useCallback } from 'react';
import { fetchSettings, updateSettings } from '../api/adminApiClient';

export default function useSettings() {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchSettings();
      setSettings(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const save = async (newSettings) => {
    const updated = await updateSettings(newSettings);
    setSettings(updated);
    return updated;
  };

  return { settings, loading, error, reload: load, save };
}