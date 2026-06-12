import { useState } from 'react';
import { useWeeks } from '../hooks/useWeeks';
import { exportExcel } from '../api/adminApiClient';
import messages from '../utils/messages';

export default function ExportPage() {
  const { weeks, loading } = useWeeks();
  const [selectedWeek, setSelectedWeek] = useState('');
  const [exporting, setExporting] = useState(false);

  const handleExport = async () => {
    if (!selectedWeek) return;
    setExporting(true);
    try {
      const blob = await exportExcel(selectedWeek);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `constraints_${selectedWeek}.xlsx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } finally {
      setExporting(false);
    }
  };

  if (loading) return <div className="loading">{messages.common.loading}</div>;

  return (
    <div className="page">
      <h2>{messages.export.title}</h2>
      <div className="card">
        <div className="form-group">
          <label>{messages.export.selectWeek}</label>
          <select value={selectedWeek} onChange={(e) => setSelectedWeek(e.target.value)}>
            <option value="">{messages.export.chooseWeek}</option>
            {weeks.map((w) => (
              <option key={w.id} value={w.id}>{w.week_label}</option>
            ))}
          </select>
        </div>
        <button
          className="btn btn-primary"
          onClick={handleExport}
          disabled={!selectedWeek || exporting}
        >
          {exporting ? messages.export.exporting : messages.export.download}
        </button>
      </div>
    </div>
  );
}