import { useState, useRef } from 'react';
import { previewConstraintsImport } from '../api/adminApiClient';
import messages from '../utils/messages';

const m = messages.importConstraints;
const DAY_NAMES = ['ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת'];

/**
 * Constraints import — step 03: upload an xlsx and see a clean, merged preview
 * (dry-run, no write). The "confirm import" button is wired in step 04.
 */
export default function ImportConstraintsPage() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleFile = (e) => {
    setFile(e.target.files?.[0] || null);
    setPreview(null);
    setError('');
  };

  const handlePreview = async () => {
    if (!file) {
      setError(m.pickFileFirst);
      return;
    }
    setLoading(true);
    setError('');
    try {
      setPreview(await previewConstraintsImport(file));
    } catch (err) {
      setError(err.message || 'שגיאה בעיבוד הקובץ');
      setPreview(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page" dir="rtl">
      <h2>{m.title}</h2>
      <p className="page-subtitle">{m.subtitle}</p>

      <div className="card">
        <div className="form-group">
          <label>{m.chooseFile}</label>
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx"
            onChange={handleFile}
            data-testid="file-input"
          />
        </div>
        <button
          className="btn btn-primary"
          onClick={handlePreview}
          disabled={!file || loading}
        >
          {loading ? m.previewing : m.preview}
        </button>
      </div>

      {error && <div className="alert alert-error" role="alert">{error}</div>}

      {preview && <PreviewResult preview={preview} />}
    </div>
  );
}

function PreviewResult({ preview }) {
  const { week_start, week_end, guards, errors } = preview;
  return (
    <>
      <div className="card preview-meta">
        {week_start && week_end && (
          <span className="preview-week">
            {m.weekPrefix} {week_start} {m.weekJoin} {week_end}
          </span>
        )}
        <span className="preview-count">{guards.length} {m.guardsSuffix}</span>
      </div>

      <div className={`card ${errors.length ? 'alert-error' : ''}`}>
        <h3>{m.errorsTitle}</h3>
        {errors.length === 0 ? (
          <p>{m.noErrors}</p>
        ) : (
          <ul className="import-errors" data-testid="parse-errors">
            {errors.map((e, i) => <li key={i}>{e}</li>)}
          </ul>
        )}
      </div>

      <div className="card table-scroll">
        <table className="preview-table" dir="rtl">
          <thead>
            <tr>
              <th>{m.guard}</th>
              {DAY_NAMES.map((d) => <th key={d}>{d}</th>)}
              <th>{m.weeklyHours}</th>
              <th>{m.notes}</th>
            </tr>
          </thead>
          <tbody>
            {guards.map((g) => (
              <tr key={g.name}>
                <td className="guard-cell">
                  {g.name}{' '}
                  <span className={`badge ${g.exists ? 'badge-muted' : 'badge-new'}`}>
                    {g.exists ? m.exists : m.new}
                  </span>
                </td>
                {g.days.map((day) => (
                  <td key={day.day_index} className="day-cell">
                    {day.segments.length === 0 ? (
                      <span className="cell-empty">—</span>
                    ) : (
                      day.segments.map((s, i) => (
                        <div key={i} className="cell-window">{s}</div>
                      ))
                    )}
                  </td>
                ))}
                <td className="hours-cell">{g.weekly_hours}</td>
                <td className="notes-cell">{g.notes || ''}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <button className="btn btn-primary" disabled title="ייפעל בשלב הבא">
          {m.confirm}
        </button>
      </div>
    </>
  );
}
