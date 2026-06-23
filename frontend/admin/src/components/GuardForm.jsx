import { useState } from 'react';
import messages, { ROLE_OPTIONS } from '../utils/messages';

export default function GuardForm({ guard, onSave, onCancel }) {
  const [form, setForm] = useState({
    first_name: guard?.first_name || '',
    last_name: guard?.last_name || '',
    phone_number: guard?.phone_number || '',
    role: guard?.role || 'AHMASH',
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(form);
  };

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h3>{guard ? messages.guards.editTitle : messages.guards.addTitle}</h3>
      <div className="form-group">
        <label>{messages.guards.firstName}</label>
        <input name="first_name" value={form.first_name} onChange={handleChange} required />
      </div>
      <div className="form-group">
        <label>{messages.guards.lastName}</label>
        <input name="last_name" value={form.last_name} onChange={handleChange} required />
      </div>
      <div className="form-group">
        <label>{messages.guards.phone}</label>
         <input name="phone_number" value={form.phone_number} onChange={handleChange} required />
      </div>
      <div className="form-group">
        <label>{messages.guards.role}</label>
        <select name="role" value={form.role} onChange={handleChange}>
          {ROLE_OPTIONS.map((r) => (
            <option key={r.value} value={r.value}>{r.label}</option>
          ))}
        </select>
      </div>
      <div className="form-actions">
        <button type="submit" className="btn btn-primary">{messages.common.save}</button>
        <button type="button" className="btn btn-secondary" onClick={onCancel}>{messages.common.cancel}</button>
      </div>
    </form>
  );
}