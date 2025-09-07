import { useEffect, useState } from 'react';
import { getBragEntries, createBragEntry } from '../lib/api.js';

// Page for submitting BRAG entries and viewing existing ones.
export default function BragPage() {
  const [entries, setEntries] = useState([]);
  const [form, setForm] = useState({
    date: '',
    behaviour: 1,
    relationships: 1,
    attitude: 1,
    growth: 1,
    notes: '',
  });
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchEntries() {
      try {
        const data = await getBragEntries();
        setEntries(data);
      } catch (err) {
        console.error(err);
        setError(err.message || 'Failed to load BRAG entries');
      }
    }
    fetchEntries();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await createBragEntry({
        date: form.date,
        behaviour: parseInt(form.behaviour, 10),
        relationships: parseInt(form.relationships, 10),
        attitude: parseInt(form.attitude, 10),
        growth: parseInt(form.growth, 10),
        notes: form.notes || null,
      });
      const updated = await getBragEntries();
      setEntries(updated);
      setForm({ date: '', behaviour: 1, relationships: 1, attitude: 1, growth: 1, notes: '' });
      setError('');
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to create BRAG entry');
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h2 className="text-lg font-semibold text-gray-200">BRAG Entries</h2>
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
        {['behaviour', 'relationships', 'attitude', 'growth'].map((field) => (
          <div key={field} className="flex flex-col">
            <label className="text-gray-400 mb-1 capitalize">{field}</label>
            <select
              name={field}
              value={form[field]}
              onChange={handleChange}
              className="bg-gray-700 border border-gray-600 text-gray-200 p-2 rounded"
            >
              {[1, 2, 3, 4, 5].map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </div>
        ))}
        <div className="flex flex-col">
          <label className="text-gray-400 mb-1">Notes</label>
          <textarea
            name="notes"
            value={form.notes}
            onChange={handleChange}
            className="bg-gray-700 border border-gray-600 text-gray-200 p-2 rounded"
            rows="3"
          />
        </div>
        <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded">Add Entry</button>
      </form>
      <div>
        <h3 className="font-semibold text-gray-300 mb-2">Your BRAG History</h3>
        <table className="min-w-full border-collapse text-sm">
          <thead>
            <tr className="bg-gray-800">
              <th className="border border-gray-700 px-3 py-2 text-left">Date</th>
              <th className="border border-gray-700 px-3 py-2 text-left">Behaviour</th>
              <th className="border border-gray-700 px-3 py-2 text-left">Relationships</th>
              <th className="border border-gray-700 px-3 py-2 text-left">Attitude</th>
              <th className="border border-gray-700 px-3 py-2 text-left">Growth</th>
              <th className="border border-gray-700 px-3 py-2 text-left">Notes</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((entry) => (
              <tr key={entry.id} className="bg-gray-800">
                <td className="border border-gray-700 px-3 py-2">{entry.date}</td>
                <td className="border border-gray-700 px-3 py-2">{entry.behaviour}</td>
                <td className="border border-gray-700 px-3 py-2">{entry.relationships}</td>
                <td className="border border-gray-700 px-3 py-2">{entry.attitude}</td>
                <td className="border border-gray-700 px-3 py-2">{entry.growth}</td>
                <td className="border border-gray-700 px-3 py-2">{entry.notes || ''}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}