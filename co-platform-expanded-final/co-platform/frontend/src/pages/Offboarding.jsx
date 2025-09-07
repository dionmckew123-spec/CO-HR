import { useEffect, useState } from 'react';
import { getOffboardings, createOffboarding } from '../lib/api.js';

// Page for recording offboarding tasks and viewing existing records.
export default function OffboardingPage() {
  const [records, setRecords] = useState([]);
  const [form, setForm] = useState({
    date: '',
    assets_returned: false,
    knowledge_transferred: false,
    access_restricted: false,
    completed: false,
  });
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchRecords() {
      try {
        const data = await getOffboardings();
        setRecords(data);
      } catch (err) {
        console.error(err);
        setError(err.message || 'Failed to load offboarding records');
      }
    }
    fetchRecords();
  }, []);

  const handleChange = (e) => {
    const { name, type, checked, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await createOffboarding({
        date: form.date,
        assets_returned: form.assets_returned,
        knowledge_transferred: form.knowledge_transferred,
        access_restricted: form.access_restricted,
        completed: form.completed,
      });
      const updated = await getOffboardings();
      setRecords(updated);
      setForm({ date: '', assets_returned: false, knowledge_transferred: false, access_restricted: false, completed: false });
      setError('');
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to create offboarding record');
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h2 className="text-lg font-semibold text-gray-200">Offboarding</h2>
      {error && <div className="text-red-500 text-sm">{error}</div>}
      <form onSubmit={handleSubmit} className="flex flex-col gap-4 bg-gray-800 p-4 rounded-lg shadow">
        <div className="flex flex-col">
          <label className="text-gray-400 mb-1">Date</label>
          <input
            type="date"
            name="date"
            value={form.date}
            onChange={handleChange}
            className="bg-gray-700 border border-gray-600 text-gray-200 p-2 rounded"
            required
          />
        </div>
        <div className="flex flex-wrap gap-4">
          <label className="flex items-center text-gray-300">
            <input
              type="checkbox"
              name="assets_returned"
              checked={form.assets_returned}
              onChange={handleChange}
              className="accent-blue-500 h-4 w-4"
            />
            <span className="ml-2">Assets Returned</span>
          </label>
          <label className="flex items-center text-gray-300">
            <input
              type="checkbox"
              name="knowledge_transferred"
              checked={form.knowledge_transferred}
              onChange={handleChange}
              className="accent-blue-500 h-4 w-4"
            />
            <span className="ml-2">Knowledge Transferred</span>
          </label>
          <label className="flex items-center text-gray-300">
            <input
              type="checkbox"
              name="access_restricted"
              checked={form.access_restricted}
              onChange={handleChange}
              className="accent-blue-500 h-4 w-4"
            />
            <span className="ml-2">Access Restricted</span>
          </label>
          <label className="flex items-center text-gray-300">
            <input
              type="checkbox"
              name="completed"
              checked={form.completed}
              onChange={handleChange}
              className="accent-blue-500 h-4 w-4"
            />
            <span className="ml-2">Completed</span>
          </label>
        </div>
        <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded">Record Offboarding</button>
      </form>
      <div>
        <h3 className="font-semibold text-gray-300 mb-2">Your Offboarding Records</h3>
        <table className="min-w-full border-collapse text-sm">
          <thead>
            <tr className="bg-gray-800">
              <th className="border border-gray-700 px-3 py-2 text-left">Date</th>
              <th className="border border-gray-700 px-3 py-2 text-left">Assets Returned</th>
              <th className="border border-gray-700 px-3 py-2 text-left">Knowledge Transferred</th>
              <th className="border border-gray-700 px-3 py-2 text-left">Access Restricted</th>
              <th className="border border-gray-700 px-3 py-2 text-left">Completed</th>
            </tr>
          </thead>
          <tbody>
            {records.map((r) => (
              <tr key={r.id} className="bg-gray-800">
                <td className="border border-gray-700 px-3 py-2">{r.date}</td>
                <td className="border border-gray-700 px-3 py-2">{r.assets_returned ? 'Yes' : 'No'}</td>
                <td className="border border-gray-700 px-3 py-2">{r.knowledge_transferred ? 'Yes' : 'No'}</td>
                <td className="border border-gray-700 px-3 py-2">{r.access_restricted ? 'Yes' : 'No'}</td>
                <td className="border border-gray-700 px-3 py-2">{r.completed ? 'Yes' : 'No'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}