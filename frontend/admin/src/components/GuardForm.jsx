import { useState } from 'react';
import messages from '../utils/messages';

export default function GuardForm({ onSave, onCancel }) {
  const [form, setForm] = useState({
    full_name: '',
    phone: '',
    telegram_chat_id: '',
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
        <input name="phone" value={form.phone} onChange={handleChange} />
      </div>
      <div className="form-group">
        <label>{messages.guards.telegramId}</label>
        <input name="telegram_chat_id" value={form.telegram_chat_id} onChange={handleChange} />
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