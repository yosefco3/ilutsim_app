/**
 * Single day row in the submission form.
 * Shows availability toggle, shift type selector, custom hours, and event toggles.
 */
import {
  messages,
  DAY_NAMES,
  SHIFT_LABELS,
  EVENT_LABELS,
} from "../utils/messages.js";

/**
 * @param {object} props
 * @param {object} props.day - Day state { day_index, available, shift_type, from_hour, to_hour, blocked }
 * @param {Array} props.events - Active events for this day [{ day_index, event_type }]
 * @param {boolean} props.disabled - Whether the form is locked
 * @param {Function} props.onToggleAvailable
 * @param {Function} props.onSetShiftType
 * @param {Function} props.onSetHours
 * @param {Function} props.onToggleEvent
 */
export default function DayRow({
  day,
  events,
  disabled,
  onToggleAvailable,
  onSetShiftType,
  onSetHours,
  onToggleEvent,
}) {
  const dayName = DAY_NAMES[day.day_index] || `יום ${day.day_index}`;
  const dayEvents = events.filter((e) => e.day_index === day.day_index);
  const isBlocked = day.blocked;
  const isDisabled = disabled || isBlocked;

  return (
    <div className={`day-row ${day.available ? "available" : "unavailable"} ${isBlocked ? "blocked" : ""}`}>
      {/* Day header */}
      <div className="day-header">
        <span className="day-name">{dayName}</span>
        {isBlocked && <span className="blocked-badge">{messages.LABEL_BLOCKED}</span>}
        {!isBlocked && (
          <button
            type="button"
            className={`toggle-btn ${day.available ? "on" : "off"}`}
            disabled={disabled}
            onClick={() => onToggleAvailable(day.day_index)}
          >
            {day.available ? messages.LABEL_AVAILABLE : messages.LABEL_UNAVAILABLE}
          </button>
        )}
      </div>

      {/* Shift type (only if available and not blocked) */}
      {day.available && !isBlocked && (
        <div className="day-shifts">
          {Object.entries(SHIFT_LABELS).map(([key, label]) => (
            <button
              key={key}
              type="button"
              className={`shift-btn ${day.shift_type === key ? "active" : ""}`}
              disabled={isDisabled}
              onClick={() => onSetShiftType(day.day_index, key)}
            >
              {label}
            </button>
          ))}

          {/* Custom hours inputs */}
          <div className="custom-hours">
            <label>
              {messages.LABEL_FROM}
              <input
                type="time"
                value={day.from_hour}
                disabled={isDisabled}
                onChange={(e) =>
                  onSetHours(day.day_index, e.target.value, day.to_hour)
                }
              />
            </label>
            <label>
              {messages.LABEL_TO}
              <input
                type="time"
                value={day.to_hour}
                disabled={isDisabled}
                onChange={(e) =>
                  onSetHours(day.day_index, day.from_hour, e.target.value)
                }
              />
            </label>
          </div>
        </div>
      )}

      {/* Event toggles */}
      {!isBlocked && (
        <div className="day-events">
          {Object.entries(EVENT_LABELS).map(([key, label]) => (
            <button
              key={key}
              type="button"
              className={`event-btn ${dayEvents.some((e) => e.event_type === key) ? "active" : ""}`}
              disabled={isDisabled}
              onClick={() => onToggleEvent(day.day_index, key)}
            >
              {label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}