import { useState } from 'react';
import messages from '../utils/messages';

export default function EventForm({ onSave, onCancel }) {
  const [form, setForm] = useState({
    title: '',
    description: '',
    event_date: '',
    event_type: 'holiday',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(form);
  };

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h3>{messages.events.addTitle}</h3>
      <div className="form-group">
        <label>{messages.events.title}</label>
        <input name="title" value={form.title} onChange={handleChange} required />
      </div>
      <div className="form-group">
        <label>{messages.events.date}</label>
        <input type="date" name="event_date" value={form.event_date} onChange={handleChange} required />
      </div>
      <div className="form-group">
        <label>{messages.events.type}</label>
        <select name="event_type" value={form.event_type} onChange={handleChange}>
          <option value="holiday">{messages.events.holiday}</option>
          <option value="training">{messages.events.training}</option>
          <option value="maintenance">{messages.events.maintenance}</option>
          <option value="other">{messages.events.other}</option>
        </select>
      </div>
      <div className="form-group">
        <label>{messages.events.description}</label>
        <textarea name="description" value={form.description} onChange={handleChange} rows={3} />
      </div>
      <div className="form-actions">
        <button type="submit" className="btn btn-primary">{messages.common.save}</button>
        <button type="button" className="btn btn-secondary" onClick={onCancel}>{messages.common.cancel}</button>
      </div>
    </form>
  );
}