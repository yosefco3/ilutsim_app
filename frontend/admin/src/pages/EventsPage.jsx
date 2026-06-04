import { useState, useEffect } from 'react';
import { getEvents, createEvent, deleteEvent } from '../api/adminApiClient';
import EventForm from '../components/EventForm';
import ConfirmDialog from '../components/ConfirmDialog';
import messages from '../utils/messages';

export default function EventsPage() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(null);

  const load = async () => {
    setLoading(true);
    try {
      const data = await getEvents();
      setEvents(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleSave = async (data) => {
    await createEvent(data);
    setShowForm(false);
    load();
  };

  const handleDelete = async () => {
    if (confirmDelete) {
      await deleteEvent(confirmDelete.id);
      setConfirmDelete(null);
      load();
    }
  };

  if (loading) return <div className="loading">{messages.common.loading}</div>;

  return (
    <div className="page">
      <div className="page-header">
        <h2>{messages.events.title}</h2>
        {!showForm && (
          <button className="btn btn-primary" onClick={() => setShowForm(true)}>
            {messages.events.addTitle}
          </button>
        )}
      </div>

      {showForm && (
        <EventForm onSave={handleSave} onCancel={() => setShowForm(false)} />
      )}

      {!events.length ? (
        <p className="empty-state">{messages.events.empty}</p>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>{messages.events.title}</th>
              <th>{messages.events.date}</th>
              <th>{messages.events.type}</th>
              <th>{messages.common.actions}</th>
            </tr>
          </thead>
          <tbody>
            {events.map((ev) => (
              <tr key={ev.id}>
                <td>{ev.title}</td>
                <td>{ev.event_date}</td>
                <td>{ev.event_type}</td>
                <td>
                  <button className="btn btn-danger btn-sm" onClick={() => setConfirmDelete(ev)}>
                    {messages.common.delete}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {confirmDelete && (
        <ConfirmDialog
          message={messages.events.confirmDelete}
          onConfirm={handleDelete}
          onCancel={() => setConfirmDelete(null)}
        />
      )}
    </div>
  );
}