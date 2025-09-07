import { useEffect, useState } from 'react';
import { getAppeals, createAppeal, getIncidents } from '../lib/api.js';

// Page for submitting appeals against incidents and listing existing appeals.
export default function AppealsPage() {
  const [appeals, setAppeals] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [form, setForm] = useState({ incident_id: '', reason: '' });
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchData() {
      try {
        const [appealsData, incidentsData] = await Promise.all([
          getAppeals(),
          getIncidents(),
        ]);
        setAppeals(appealsData);
        setIncidents(incidentsData);
      } catch (err) {
        console.error(err);
        setError(err.message || 'Failed to load appeals');
      }
    }
    fetchData();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.incident_id) {
      setError('Please select an incident to appeal');
      return;
    }
    try {
      await createAppeal({
        incident_id: parseInt(form.incident_id, 10),
        reason: form.reason,
      });
      const updated = await getAppeals();
      setAppeals(updated);
      setForm({ incident_id: '', reason: '' });
      setError('');
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to create appeal');
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h2 className="text-lg font-semibold text-gray-200">Appeals</h2>
      {error && <div className="text-red-500 text-sm">{error}</div>}
      <form onSubmit={handleSubmit} className="flex flex-col gap-4 bg-gray-800 p-4 rounded-lg shadow">
        <div className="flex flex-col">
          <label className="text-gray-400 mb-1">Incident</label>
          <select
            value={form.incident_id}
            onChange={(e) => setForm({ ...form, incident_id: e.target.value })}
            className="bg-gray-700 border border-gray-600 text-gray-200 p-2 rounded"
            required
          >
            <option value="">-- Select an incident --</option>
            {incidents.map((incident) => (
              <option key={incident.id} value={incident.id}>
                {incident.id}: {incident.description.slice(0, 30)}
              </option>
            ))}
          </select>
        </div>
        <div className="flex flex-col">
          <label className="text-gray-400 mb-1">Reason</label>
          <textarea
            value={form.reason}
            onChange={(e) => setForm({ ...form, reason: e.target.value })}
            className="bg-gray-700 border border-gray-600 text-gray-200 p-2 rounded"
            rows="3"
            required
          />
        </div>
        <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded">Submit Appeal</button>
      </form>
      <div>
        <h3 className="font-semibold text-gray-300 mb-2">Your Appeals</h3>
        <table className="min-w-full border-collapse text-sm">
          <thead>
            <tr className="bg-gray-800">
              <th className="border border-gray-700 px-3 py-2 text-left">ID</th>
              <th className="border border-gray-700 px-3 py-2 text-left">Incident</th>
              <th className="border border-gray-700 px-3 py-2 text-left">Reason</th>
              <th className="border border-gray-700 px-3 py-2 text-left">Status</th>
              <th className="border border-gray-700 px-3 py-2 text-left">Date</th>
            </tr>
          </thead>
          <tbody>
            {appeals.map((a) => (
              <tr key={a.id} className="bg-gray-800">
                <td className="border border-gray-700 px-3 py-2">{a.id}</td>
                <td className="border border-gray-700 px-3 py-2">{a.incident_id}</td>
                <td className="border border-gray-700 px-3 py-2">{a.reason}</td>
                <td className="border border-gray-700 px-3 py-2 capitalize">{a.status}</td>
                <td className="border border-gray-700 px-3 py-2">{a.created_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}