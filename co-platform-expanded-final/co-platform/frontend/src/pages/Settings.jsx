import React, { useEffect, useState } from 'react';
import {
  getSettings,
  upsertSettings,
  getCurrentUser,
  exportUserData,
  cleanupRetention,
  listWebhooks,
  createWebhook,
  updateWebhook,
  deleteWebhook,
} from '../lib/api.js';
import { useNavigate } from 'react-router-dom';

/**
 * Settings page for configuring organisation-wide options.
 *
 * Currently allows editing the organisation name and logo URL. More advanced
 * settings (e.g. working week, leave allowances, default channels) can be
 * added later. A link to the Webhooks configuration page is provided.
 */
function SettingsPage() {
  const navigate = useNavigate();
  const [companyName, setCompanyName] = useState('');
  const [logoUrl, setLogoUrl] = useState('');
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  // Additional settings fields
  const [workingDays, setWorkingDays] = useState('');
  const [holidaysJson, setHolidaysJson] = useState('');
  const [leavePolicyJson, setLeavePolicyJson] = useState('');
  const [defaultChannelsJson, setDefaultChannelsJson] = useState('');
  const [featureFlagsJson, setFeatureFlagsJson] = useState('');
  const [retentionYears, setRetentionYears] = useState(4);

  // DSAR and retention messages
  const [dsarData, setDsarData] = useState(null);

  // Webhooks management state
  const [webhooks, setWebhooks] = useState([]);
  const [webhookForm, setWebhookForm] = useState({ event_type: '', url: '', active: true, description: '' });
  const [editingWebhookId, setEditingWebhookId] = useState(null);
  const [webhookError, setWebhookError] = useState('');
  const [webhookMessage, setWebhookMessage] = useState('');

  useEffect(() => {
    async function fetchSettings() {
      try {
        const settings = await getSettings();
        if (settings) {
          setCompanyName(settings.company_name || '');
          setLogoUrl(settings.logo_url || '');
          setWorkingDays(settings.working_days || '');
          setHolidaysJson(settings.holidays_json || '');
          setLeavePolicyJson(settings.leave_policy_json || '');
          setDefaultChannelsJson(settings.default_channels_json || '');
          setFeatureFlagsJson(settings.feature_flags_json || '');
          setRetentionYears(settings.retention_years || 4);
        }
        setLoading(false);
      } catch (err) {
        console.error(err);
        setLoading(false);
      }
    }
    async function fetchWebhooks() {
      try {
        const data = await listWebhooks();
        setWebhooks(data);
      } catch (err) {
        console.error(err);
        setWebhookError('Failed to load webhooks');
      }
    }
    fetchSettings();
    fetchWebhooks();
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setMessage('');
    try {
      await upsertSettings({
        company_name: companyName,
        logo_url: logoUrl,
        working_days: workingDays,
        holidays_json: holidaysJson,
        leave_policy_json: leavePolicyJson,
        default_channels_json: defaultChannelsJson,
        feature_flags_json: featureFlagsJson,
        retention_years: retentionYears,
      });
      setMessage('Settings saved successfully');
    } catch (err) {
      console.error(err);
      setMessage(err.message || 'Failed to save settings');
    }
  }

  async function handleExportData() {
    setMessage('');
    setDsarData(null);
    try {
      const user = await getCurrentUser();
      const data = await exportUserData(user.id);
      setDsarData(data);
      setMessage('Your data has been exported below. Copy/paste or save as JSON.');
    } catch (err) {
      console.error(err);
      setMessage(err.message || 'Failed to export data');
    }
  }

  async function handleRetentionCleanup(e) {
    e.preventDefault();
    setMessage('');
    try {
      const result = await cleanupRetention(retentionYears);
      setMessage(`Cleanup complete: ${JSON.stringify(result)}`);
    } catch (err) {
      console.error(err);
      setMessage(err.message || 'Failed to perform cleanup');
    }
  }

  // Webhook management functions
  function handleWebhookChange(e) {
    const { name, value, type, checked } = e.target;
    setWebhookForm((prev) => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  }

  async function handleWebhookSubmit(e) {
    e.preventDefault();
    setWebhookError('');
    setWebhookMessage('');
    try {
      if (editingWebhookId) {
        await updateWebhook(editingWebhookId, webhookForm);
        setWebhookMessage('Webhook updated');
      } else {
        await createWebhook(webhookForm);
        setWebhookMessage('Webhook created');
      }
      setWebhookForm({ event_type: '', url: '', active: true, description: '' });
      setEditingWebhookId(null);
      const data = await listWebhooks();
      setWebhooks(data);
    } catch (err) {
      console.error(err);
      setWebhookError(err.message || 'Failed to save webhook');
    }
  }

  function handleWebhookEdit(w) {
    setEditingWebhookId(w.id);
    setWebhookForm({ event_type: w.event_type, url: w.url, active: w.active, description: w.description || '' });
    setWebhookMessage('');
    setWebhookError('');
  }

  async function handleWebhookDelete(id) {
    if (!confirm('Are you sure you want to delete this webhook?')) return;
    try {
      await deleteWebhook(id);
      const data = await listWebhooks();
      setWebhooks(data);
    } catch (err) {
      console.error(err);
      setWebhookError(err.message || 'Failed to delete webhook');
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold mb-4">Settings</h1>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4 max-w-3xl bg-gray-800 p-4 rounded">
          <h2 className="text-xl font-semibold mb-2">Organisation Info</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-400 mb-1">Organisation Name</label>
              <input
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-gray-200"
              />
            </div>
            <div>
              <label className="block text-gray-400 mb-1">Logo URL</label>
              <input
                type="url"
                value={logoUrl}
                onChange={(e) => setLogoUrl(e.target.value)}
                className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-gray-200"
              />
            </div>
            <div>
              <label className="block text-gray-400 mb-1">Working Days (comma-separated)</label>
              <input
                type="text"
                value={workingDays}
                onChange={(e) => setWorkingDays(e.target.value)}
                placeholder="Mon,Tue,Wed,Thu,Fri"
                className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-gray-200"
              />
            </div>
            <div>
              <label className="block text-gray-400 mb-1">Holidays JSON</label>
              <input
                type="text"
                value={holidaysJson}
                onChange={(e) => setHolidaysJson(e.target.value)}
                placeholder='["2025-12-25","2025-12-26"]'
                className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-gray-200"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-gray-400 mb-1">Leave Policy JSON</label>
              <textarea
                value={leavePolicyJson}
                onChange={(e) => setLeavePolicyJson(e.target.value)}
                rows="3"
                placeholder='{"annual_min":1,"annual_max":14,"carry_over":0}'
                className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-gray-200"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-gray-400 mb-1">Default Channels JSON (module→channel)</label>
              <textarea
                value={defaultChannelsJson}
                onChange={(e) => setDefaultChannelsJson(e.target.value)}
                rows="2"
                placeholder='{"tickets":"#support","incidents":"#incidents"}'
                className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-gray-200"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-gray-400 mb-1">Feature Flags JSON</label>
              <textarea
                value={featureFlagsJson}
                onChange={(e) => setFeatureFlagsJson(e.target.value)}
                rows="2"
                placeholder='{"training_enabled":true,"probations_enabled":true}'
                className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-gray-200"
              />
            </div>
          </div>
          <div className="mt-4">
            <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded">
              Save Settings
            </button>
            {message && <p className="text-green-400 mt-2">{message}</p>}
          </div>
        </form>
      )}
      {/* Data Privacy & Retention */}
      <div className="bg-gray-800 p-4 rounded">
        <h2 className="text-xl font-semibold mb-2">Data Privacy & Retention</h2>
        <p className="text-gray-400 text-sm mb-2">Export your personal data or perform retention cleanup.</p>
        <div className="space-y-2">
          <button
            onClick={handleExportData}
            className="bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded mr-3"
          >
            Export My Data
          </button>
          <form onSubmit={handleRetentionCleanup} className="inline-flex items-center space-x-2">
            <label className="text-gray-400 text-sm">Retention Years:</label>
            <input
              type="number"
              min="1"
              value={retentionYears}
              onChange={(e) => setRetentionYears(parseInt(e.target.value) || 1)}
              className="w-20 p-1 bg-gray-700 border border-gray-600 rounded text-gray-200 text-sm"
            />
            <button type="submit" className="bg-red-600 hover:bg-red-700 text-white py-2 px-3 rounded text-sm">
              Run Cleanup
            </button>
          </form>
        </div>
        {dsarData && (
          <div className="mt-4 bg-gray-900 p-4 rounded-lg text-xs overflow-auto" style={{ maxHeight: '300px' }}>
            <pre>{JSON.stringify(dsarData, null, 2)}</pre>
          </div>
        )}
      </div>
      {/* Webhook Management */}
      <div className="bg-gray-800 p-4 rounded">
        <h2 className="text-xl font-semibold mb-2">Webhook Notifications</h2>
        <p className="text-gray-400 text-sm mb-2">Configure Discord webhooks for system events.</p>
        {webhookError && <p className="text-red-500 mb-2">{webhookError}</p>}
        {webhookMessage && <p className="text-green-400 mb-2">{webhookMessage}</p>}
        <form onSubmit={handleWebhookSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-gray-900 p-4 rounded">
          <div>
            <label className="block text-gray-400 mb-1">Event Type</label>
            <input
              type="text"
              name="event_type"
              value={webhookForm.event_type}
              onChange={handleWebhookChange}
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
              value={webhookForm.url}
              onChange={handleWebhookChange}
              required
              placeholder="https://discord.com/api/webhooks/..."
              className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-gray-200"
            />
          </div>
          <div className="flex items-center">
            <input
              type="checkbox"
              name="active"
              checked={webhookForm.active}
              onChange={handleWebhookChange}
              className="mr-2"
            />
            <label className="text-gray-400">Active</label>
          </div>
          <div>
            <label className="block text-gray-400 mb-1">Description (optional)</label>
            <input
              type="text"
              name="description"
              value={webhookForm.description}
              onChange={handleWebhookChange}
              className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-gray-200"
            />
          </div>
          <div className="md:col-span-2">
            <button type="submit" className="bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded">
              {editingWebhookId ? 'Update Webhook' : 'Create Webhook'}
            </button>
          </div>
        </form>
        {/* Existing webhooks */}
        <h3 className="text-lg font-semibold mt-6 mb-2">Existing Webhooks</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-700 text-sm">
            <thead className="bg-gray-900">
              <tr>
                <th className="px-4 py-2 text-left text-gray-400 font-medium">Event</th>
                <th className="px-4 py-2 text-left text-gray-400 font-medium">URL</th>
                <th className="px-4 py-2 text-left text-gray-400 font-medium">Active</th>
                <th className="px-4 py-2 text-left text-gray-400 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-gray-900 divide-y divide-gray-700">
              {webhooks.map((w) => (
                <tr key={w.id}>
                  <td className="px-4 py-2 text-gray-300">{w.event_type}</td>
                  <td className="px-4 py-2 text-blue-400 max-w-xs truncate">{w.url}</td>
                  <td className="px-4 py-2 text-gray-300">{w.active ? 'Yes' : 'No'}</td>
                  <td className="px-4 py-2 text-gray-300 space-x-2">
                    <button
                      onClick={() => handleWebhookEdit(w)}
                      className="text-yellow-400 hover:text-yellow-500"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleWebhookDelete(w.id)}
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
    </div>
  );
}

export default SettingsPage;