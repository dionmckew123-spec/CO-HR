import { useEffect, useState } from 'react';
import {
  getTrainingStatuses,
  createTrainingStatus,
  getCurrentUser,
} from '../lib/api.js';

// Page for recording and viewing training modules for the current user.
export default function Training() {
  const [trainingList, setTrainingList] = useState([]);
  const [form, setForm] = useState({ module_name: '', completed: false, completion_date: '' });
  const [userId, setUserId] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchData() {
      try {
        const user = await getCurrentUser();
        setUserId(user.id);
        const data = await getTrainingStatuses();
        setTrainingList(data);
      } catch (err) {
        console.error(err);
        setError(err.message || 'Failed to load training records');
      }
    }
    fetchData();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userId) return;
    try {
      await createTrainingStatus({
        user_id: userId,
        module_name: form.module_name,
        completed: form.completed,
        completion_date: form.completed ? form.completion_date : null,
      });
      const updated = await getTrainingStatuses();
      setTrainingList(updated);
      setForm({ module_name: '', completed: false, completion_date: '' });
      setError('');
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to create training record');
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h2 className="text-lg font-semibold text-gray-200">Training Modules</h2>
      {error && <div className="text-red-500 text-sm">{error}</div>}
      <form onSubmit={handleSubmit} className="flex flex-col gap-4 bg-gray-800 p-4 rounded-lg shadow">
        <div className="flex flex-col">
          <label className="text-gray-400 mb-1">Module Name</label>
          <input
            type="text"
            value={form.module_name}
            onChange={(e) => setForm({ ...form, module_name: e.target.value })}
            className="bg-gray-700 border border-gray-600 text-gray-200 p-2 rounded"
            required
          />
        </div>
        <div className="flex items-center gap-4">
          <label className="flex items-center text-gray-300">
            <input
              type="checkbox"
              checked={form.completed}
              onChange={(e) => setForm({ ...form, completed: e.target.checked })}
              className="accent-blue-500 h-4 w-4"
            />
            <span className="ml-2">Completed</span>
          </label>
          {form.completed && (
            <input
              type="date"
              value={form.completion_date}
              onChange={(e) => setForm({ ...form, completion_date: e.target.value })}
              className="bg-gray-700 border border-gray-600 text-gray-200 p-2 rounded"
              required
            />
          )}
        </div>
        <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded">Record Training</button>
      </form>
      <div>
        <h3 className="font-semibold text-gray-300 mb-2">Your Training Records</h3>
        <table className="min-w-full border-collapse text-sm">
          <thead>
            <tr className="bg-gray-800">
              <th className="border border-gray-700 px-3 py-2 text-left">Module</th>
              <th className="border border-gray-700 px-3 py-2 text-left">Completed</th>
              <th className="border border-gray-700 px-3 py-2 text-left">Completion Date</th>
            </tr>
          </thead>
          <tbody>
            {trainingList.map((t) => (
              <tr key={t.id} className="bg-gray-800">
                <td className="border border-gray-700 px-3 py-2">{t.module_name}</td>
                <td className="border border-gray-700 px-3 py-2">{t.completed ? 'Yes' : 'No'}</td>
                <td className="border border-gray-700 px-3 py-2">{t.completion_date || ''}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}