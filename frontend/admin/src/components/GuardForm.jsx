import { useState } from 'react';
import messages from '../utils/messages';

export default function GuardForm({ onSave, onCancel }) {
  const ROLES = [
    { value: 'ahmash', label: messages.guards.roleAhmash },
    { value: 'basic_course', label: messages.guards.roleBasicCourse },
    { value: 'level_b', label: messages.guards.roleLevelB },
    { value: '9_hours', label: messages.guards.role9Hours },
    { value: 'unarmed', label: messages.guards.roleUnarmed },
    { value: 'checker', label: messages.guards.roleChecker },
  ];

  const [form, setForm] = useState({
    full_name: '',
    phone_number: '',
    role: 'ahmash',
    is_active: true,
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
      <h3>{messages.guards.addTitle}</h3>
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
      <div className="form-group checkbox">
        <label>
          <input type="checkbox" name="is_active" checked={form.is_active} onChange={handleChange} />
          {messages.guards.active}
        </label>
      </div>
      <div className="form-actions">
        <button type="submit" className="btn btn-primary">{messages.common.save}</button>
        <button type="button" className="btn btn-secondary" onClick={onCancel}>{messages.common.cancel}</button>
      </div>
    </form>
  );
}