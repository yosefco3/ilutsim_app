import { useState } from 'react';
import messages from '../utils/messages';

const ROLES = [
  { value: 'AHMASH', label: 'אחמ"ש' },
  { value: 'BASIC_GUARD', label: 'מאבטח בסיסי' },
  { value: 'LEVEL_B', label: "מאבטח רמה ב'" },
  { value: 'NINE_HOURS', label: 'מאבטח 9 שעות' },
  { value: 'UNARMED', label: 'לא חמוש' },
  { value: 'CHECKER', label: 'בודק' },
];

export default function GuardForm({ guard, onSave, onCancel }) {
  const [form, setForm] = useState({
    full_name: guard?.full_name || '',
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
        <label>{messages.guards.fullName}</label>
        <input name="full_name" value={form.full_name} onChange={handleChange} required />
      </div>
      <div className="form-group">
        <label>{messages.guards.phone}</label>
         <input name="phone_number" value={form.phone_number} onChange={handleChange} required />
      </div>
      <div className="form-group">
        <label>{messages.guards.role}</label>
        <select name="role" value={form.role} onChange={handleChange}>
          {ROLES.map((r) => (
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