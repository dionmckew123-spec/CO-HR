import { useEffect, useState } from 'react';
import { getProbations, createProbation, getCurrentUser } from '../lib/api.js';

// Page for viewing and recording probation periods for the current user.
export default function Probations() {
  const [probations, setProbations] = useState([]);
  const [form, setForm] = useState({ start_date: '', end_date: '', result: '', notes: '' });
  const [userId, setUserId] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchData() {
      try {
        const user = await getCurrentUser();
        setUserId(user.id);
        const data = await getProbations();
        setProbations(data);
      } catch (err) {
        console.error(err);
        setError(err.message || 'Failed to load probations');
      }
    }
    fetchData();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userId) return;
    try {
      await createProbation({
        user_id: userId,
        start_date: form.start_date,
        end_date: form.end_date,
        result: form.result || null,
        notes: form.notes || null,
      });
      const updated = await getProbations();
      setProbations(updated);
      setForm({ start_date: '', end_date: '', result: '', notes: '' });
      setError('');
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to create probation');
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h2 className="text-lg font-semibold text-gray-200">Probations</h2>
      {error && <div className="text-red-500 text-sm">{error}</div>}
      <form onSubmit={handleSubmit} className="flex flex-col gap-4 bg-gray-800 p-4 rounded-lg shadow">
        <div className="flex flex-col">
          <label className="text-gray-400 mb-1">Start Date</label>
          <input
            type="date"
            value={form.start_date}
            onChange={(e) => setForm({ ...form, start_date: e.target.value })}
            className="bg-gray-700 border border-gray-600 text-gray-200 p-2 rounded"
            required
          />
        </div>
        <div className="flex flex-col">
          <label className="text-gray-400 mb-1">End Date</label>
          <input
            type="date"
            value={form.end_date}
            onChange={(e) => setForm({ ...form, end_date: e.target.value })}
            className="bg-gray-700 border border-gray-600 text-gray-200 p-2 rounded"
            required
          />
        </div>
        <div className="flex flex-col">
          <label className="text-gray-400 mb-1">Result</label>
          <select
            value={form.result}
            onChange={(e) => setForm({ ...form, result: e.target.value })}
            className="bg-gray-700 border border-gray-600 text-gray-200 p-2 rounded"
          >
            <option value="">-- Select result (optional) --</option>
            <option value="pass">Pass</option>
            <option value="extend">Extend</option>
            <option value="fail">Fail</option>
          </select>
        </div>
        <div className="flex flex-col">
          <label className="text-gray-400 mb-1">Notes</label>
          <textarea
            value={form.notes}
            onChange={(e) => setForm({ ...form, notes: e.target.value })}
            className="bg-gray-700 border border-gray-600 text-gray-200 p-2 rounded"
            rows="3"
          />
        </div>
        <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded">Record Probation</button>
      </form>
      <div>
        <h3 className="font-semibold text-gray-300 mb-2">Your Probation Records</h3>
        <table className="min-w-full border-collapse text-sm">
          <thead>
            <tr className="bg-gray-800">
              <th className="border border-gray-700 px-3 py-2 text-left">Start</th>
              <th className="border border-gray-700 px-3 py-2 text-left">End</th>
              <th className="border border-gray-700 px-3 py-2 text-left">Result</th>
              <th className="border border-gray-700 px-3 py-2 text-left">Notes</th>
            </tr>
          </thead>
          <tbody>
            {probations.map((p) => (
              <tr key={p.id} className="bg-gray-800">
                <td className="border border-gray-700 px-3 py-2">{p.start_date}</td>
                <td className="border border-gray-700 px-3 py-2">{p.end_date}</td>
                <td className="border border-gray-700 px-3 py-2">{p.result || ''}</td>
                <td className="border border-gray-700 px-3 py-2">{p.notes || ''}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}