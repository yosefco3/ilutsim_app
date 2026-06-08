/**
 * Main submission form — renders day rows, events, notes, submit button.
 * Self-contained: calls useTelegram + useSubmission hooks internally.
 * Wrapped in .guard-layout for CSS scoping.
 */
import { useTelegram } from "../../hooks/useTelegram.js";
import { useSubmission } from "../../hooks/useSubmission.js";
import { messages } from "../../utils/guardMessages.js";
import LockBanner from "./LockBanner.jsx";
import DayRow from "./DayRow.jsx";
import "../../styles/guard.css";

export default function SubmissionForm() {
  const { initData } = useTelegram();
  const {
    loading,
    error,
    success,
    week,
    days,
    events,
    notes,
    setNotes,
    weekStatus,
    isLocked,
    toggleAvailable,
    setShiftType,
    setHours,
    toggleEvent,
    submit,
  } = useSubmission(initData);

  if (loading) {
    return (
      <div className="guard-layout">
        <div className="loading">{messages.LABEL_LOADING}</div>
      </div>
    );
  }

  if (error && !week) {
    return (
      <div className="guard-layout">
        <div className="error-banner">{error}</div>
      </div>
    );
  }

  return (
    <div className="guard-layout">
      {isLocked && <LockBanner status={weekStatus} />}

      {error && <div className="error-banner">{error}</div>}
      {success && <div className="success-banner">{messages.SUCCESS_SUBMITTED}</div>}

      {/* Week info */}
      {week && (
        <div className="week-info">
          <span className="week-label">
            {week.week_label || `שבוע ${week.week_id}`}
          </span>
        </div>
      )}

      {/* Day rows */}
      <div className="days-list">
        {days.map((day) => (
          <DayRow
            key={day.day_index}
            day={day}
            events={events}
            disabled={isLocked}
            onToggleAvailable={toggleAvailable}
            onSetShiftType={setShiftType}
            onSetHours={setHours}
            onToggleEvent={toggleEvent}
          />
        ))}
      </div>

      {/* Notes */}
      <div className="notes-section">
        <label className="notes-label">{messages.LABEL_NOTES}</label>
        <textarea
          className="notes-input"
          value={notes}
          placeholder={messages.LABEL_NOTES_PLACEHOLDER}
          disabled={isLocked}
          onChange={(e) => setNotes(e.target.value)}
        />
      </div>

      {/* Submit button */}
      {!isLocked && (
        <button
          type="button"
          className="submit-btn"
          onClick={submit}
        >
          {messages.LABEL_SUBMIT}
        </button>
      )}
    </div>
  );
}