import React, { useEffect, useState } from 'react';
import {
  listWebhooks,
  createWebhook,
  updateWebhook,
  deleteWebhook,
} from '../lib/api.js';

/**
 * Webhook configuration page.
 *
 * Allows administrators to create, edit and delete webhook subscriptions for
 * specific event types. Each webhook will receive a JSON payload when its
 * corresponding event is emitted by the backend.
 */
function WebhooksPage() {
  const [webhooks, setWebhooks] = useState([]);
  const [form, setForm] = useState({ event_type: '', url: '', active: true, description: '' });
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    refresh();
  }, []);

  async function refresh() {
    try {
      const data = await listWebhooks();
      setWebhooks(data);
    } catch (err) {
      console.error(err);
      setError('Failed to load webhooks');
    }
  }

  function handleChange(e) {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setMessage('');
    try {
      if (editingId) {
        await updateWebhook(editingId, form);
        setMessage('Webhook updated');
      } else {
        await createWebhook(form);
        setMessage('Webhook created');
      }
      setForm({ event_type: '', url: '', active: true, description: '' });
      setEditingId(null);
      refresh();
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to save webhook');
    }
  }

  function handleEdit(w) {
    setEditingId(w.id);
    setForm({ event_type: w.event_type, url: w.url, active: w.active, description: w.description || '' });
    setMessage('');
    setError('');
  }

  async function handleDelete(id) {
    if (!confirm('Are you sure you want to delete this webhook?')) return;
    try {
      await deleteWebhook(id);
      refresh();
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to delete webhook');
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold mb-4">Webhooks</h1>
      {error && <p className="text-red-500">{error}</p>}
      {message && <p className="text-green-400">{message}</p>}
      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-gray-800 p-4 rounded">
        <div>
          <label className="block text-gray-400 mb-1">Event Type</label>
          <input
            type="text"
            name="event_type"
            value={form.event_type}
            onChange={handleChange}
            required
            placeholder="e.g. ticket.created"
            className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-gray-200"
          />
        </div>
        <div>
          <label className="block text-gray-400 mb-1">Webhook URL</label>
          <input
            type="url"
            name="url"
            value={form.url}
            onChange={handleChange}
            required
            placeholder="https://discord.com/api/webhooks/..."
            className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-gray-200"
          />
        </div>
        <div className="flex items-center">
          <input
            type="checkbox"
            name="active"
            checked={form.active}
            onChange={handleChange}
            className="mr-2"
          />
          <label className="text-gray-400">Active</label>
        </div>
        <div>
          <label className="block text-gray-400 mb-1">Description (optional)</label>
          <input
            type="text"
            name="description"
            value={form.description}
            onChange={handleChange}
            className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-gray-200"
          />
        </div>
        <div className="col-span-full">
          <button type="submit" className="bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded">
            {editingId ? 'Update Webhook' : 'Create Webhook'}
          </button>
        </div>
      </form>
      {/* Webhooks list */}
      <h2 className="text-xl font-semibold mt-6 mb-2">Existing Webhooks</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-700">
          <thead className="bg-gray-800">
            <tr>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-400">Event</th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-400">URL</th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-400">Active</th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-400">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-gray-800 divide-y divide-gray-700">
            {webhooks.map((w) => (
              <tr key={w.id}>
                <td className="px-4 py-2 text-gray-300">{w.event_type}</td>
                <td className="px-4 py-2 text-blue-400 max-w-xs truncate">{w.url}</td>
                <td className="px-4 py-2 text-gray-300">{w.active ? 'Yes' : 'No'}</td>
                <td className="px-4 py-2 text-gray-300 space-x-2">
                  <button
                    onClick={() => handleEdit(w)}
                    className="text-yellow-400 hover:text-yellow-500"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(w.id)}
                    className="text-red-400 hover:text-red-500"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default WebhooksPage;