import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getIncidents, createIncident } from '../lib/api.js';

function IncidentsPage() {
  const navigate = useNavigate();
  const [incidents, setIncidents] = useState([]);
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    description: '',
    severity: 'low',
  });
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchIncidents() {
      try {
        const data = await getIncidents();
        setIncidents(data);
      } catch (err) {
        // Redirect to login if unauthenticated
        navigate('/login');
      }
    }
    fetchIncidents();
  }, [navigate]);

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      const newIncident = await createIncident({
        date: formData.date,
        description: formData.description,
        severity: formData.severity,
      });
      setIncidents((prev) => [...prev, newIncident]);
      setFormData({ date: new Date().toISOString().split('T')[0], description: '', severity: 'low' });
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h2 className="text-lg font-semibold text-gray-200">Incidents</h2>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4 bg-gray-800 p-4 rounded-lg shadow">
        <div className="flex flex-col">
          <label htmlFor="date" className="text-gray-400 mb-1">Date</label>
          <input
            type="date"
            name="date"
            id="date"
            value={formData.date}
            onChange={handleChange}
            required
            className="bg-gray-700 border border-gray-600 text-gray-200 p-2 rounded"
          />
        </div>
        <div className="flex flex-col">
          <label htmlFor="description" className="text-gray-400 mb-1">Description</label>
          <textarea
            name="description"
            id="description"
            value={formData.description}
            onChange={handleChange}
            required
            className="bg-gray-700 border border-gray-600 text-gray-200 p-2 rounded"
          />
        </div>
        <div className="flex flex-col">
          <label htmlFor="severity" className="text-gray-400 mb-1">Severity</label>
          <select
            name="severity"
            id="severity"
            value={formData.severity}
            onChange={handleChange}
            className="bg-gray-700 border border-gray-600 text-gray-200 p-2 rounded"
          >
            <option value="low">Low</option>
            <option value="minor">Minor</option>
            <option value="major">Major</option>
            <option value="critical">Critical</option>
          </select>
        </div>
        <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded">Submit Incident</button>
        {error && <p className="text-red-500 text-sm">{error}</p>}
      </form>
      <div>
        <h3 className="font-semibold text-gray-300 mb-2">Your Incidents</h3>
        {incidents.length === 0 ? (
          <p className="text-gray-500 text-sm">No incidents yet.</p>
        ) : (
          <table className="min-w-full border-collapse text-sm">
            <thead>
              <tr className="bg-gray-800">
                <th className="border border-gray-700 px-3 py-2 text-left">Date</th>
                <th className="border border-gray-700 px-3 py-2 text-left">Description</th>
                <th className="border border-gray-700 px-3 py-2 text-left">Severity</th>
                <th className="border border-gray-700 px-3 py-2 text-left">Status</th>
              </tr>
            </thead>
            <tbody>
              {incidents.map((inc) => (
                <tr key={inc.id} className="bg-gray-800">
                  <td className="border border-gray-700 px-3 py-2">{inc.date}</td>
                  <td className="border border-gray-700 px-3 py-2">{inc.description}</td>
                  <td className="border border-gray-700 px-3 py-2 capitalize">{inc.severity}</td>
                  <td className="border border-gray-700 px-3 py-2 capitalize">{inc.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default IncidentsPage;