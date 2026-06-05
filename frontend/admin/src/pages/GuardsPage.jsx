import { useState } from 'react';
import { useGuards } from '../hooks/useGuards';
import GuardTable from '../components/GuardTable';
import GuardForm from '../components/GuardForm';
import ConfirmDialog from '../components/ConfirmDialog';
import messages from '../utils/messages';

export default function GuardsPage() {
  const { guards, loading, createGuard, updateGuard, toggleGuard, deleteGuard } = useGuards();
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [confirmDelete, setConfirmDelete] = useState(null);

  const [saving, setSaving] = useState(false);

  const handleSave = async (data) => {
    try {
      setSaving(true);
      if (editing) {
        await updateGuard(editing.id, data);
      } else {
        await createGuard(data);
      }
      setShowForm(false);
      setEditing(null);
    } catch (err) {
      alert(messages.common.error + ': ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (guard) => {
    setEditing(guard);
    setShowForm(true);
  };

  const handleToggle = async (guard) => {
    try {
      await toggleGuard(guard.id, !guard.is_active);
      alert(messages.common.success);
    } catch (err) {
      alert(messages.common.error + ': ' + err.message);
    }
  };

  const handleDelete = async () => {
    if (confirmDelete) {
      try {
        await deleteGuard(confirmDelete.id);
        setConfirmDelete(null);
        alert(messages.common.success);
      } catch (err) {
        alert(messages.common.error + ': ' + err.message);
      }
    }
  };

  if (loading) return <div className="loading">{messages.common.loading}</div>;

  return (
    <div className="page">
      <div className="page-header">
        <h2>{messages.guards.title}</h2>
        {!showForm && (
          <button className="btn btn-primary" onClick={() => { setEditing(null); setShowForm(true); }}>
            {messages.guards.addTitle}
          </button>
        )}
      </div>

      {showForm && (
        <GuardForm
          guard={editing}
          onSave={handleSave}
          onCancel={() => { setShowForm(false); setEditing(null); }}
        />
      )}

      <GuardTable
        guards={guards}
        onEdit={handleEdit}
        onToggle={handleToggle}
        onDelete={(g) => setConfirmDelete(g)}
      />

      {confirmDelete && (
        <ConfirmDialog
          message={messages.guards.confirmDelete}
          onConfirm={handleDelete}
          onCancel={() => setConfirmDelete(null)}
        />
      )}
    </div>
  );
}