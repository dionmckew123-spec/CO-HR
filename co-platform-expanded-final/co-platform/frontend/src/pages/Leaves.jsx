import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getLeaves, createLeave } from '../lib/api.js';

function LeavesPage() {
  const navigate = useNavigate();
  const [leaves, setLeaves] = useState([]);
  const [formData, setFormData] = useState({
    type: 'annual',
    start_date: '',
    end_date: '',
    reason: '',
  });
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchLeaves() {
      try {
        const data = await getLeaves();
        setLeaves(data);
      } catch (err) {
        navigate('/login');
      }
    }
    fetchLeaves();
  }, [navigate]);

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      const newLeave = await createLeave({
        type: formData.type,
        start_date: formData.start_date,
        end_date: formData.end_date,
        reason: formData.reason || undefined,
      });
      setLeaves((prev) => [...prev, newLeave]);
      setFormData({ type: 'annual', start_date: '', end_date: '', reason: '' });
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h2 className="text-lg font-semibold text-gray-200">Leave Requests</h2>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4 bg-gray-800 p-4 rounded-lg shadow">
        <div className="flex flex-col">
          <label className="text-gray-400 mb-1" htmlFor="type">Type</label>
          <select
            name="type"
            id="type"
            value={formData.type}
            onChange={handleChange}
            className="bg-gray-700 border border-gray-600 text-gray-200 p-2 rounded"
          >
            <option value="annual">Annual</option>
            <option value="emergency">Emergency</option>
            <option value="sick">Sick</option>
          </select>
        </div>
        <div className="flex flex-col">
          <label className="text-gray-400 mb-1" htmlFor="start_date">Start Date</label>
          <input
            type="date"
            name="start_date"
            id="start_date"
            value={formData.start_date}
            onChange={handleChange}
            required
            className="bg-gray-700 border border-gray-600 text-gray-200 p-2 rounded"
          />
        </div>
        <div className="flex flex-col">
          <label className="text-gray-400 mb-1" htmlFor="end_date">End Date</label>
          <input
            type="date"
            name="end_date"
            id="end_date"
            value={formData.end_date}
            onChange={handleChange}
            required
            className="bg-gray-700 border border-gray-600 text-gray-200 p-2 rounded"
          />
        </div>
        <div className="flex flex-col">
          <label className="text-gray-400 mb-1" htmlFor="reason">Reason (optional)</label>
          <input
            type="text"
            name="reason"
            id="reason"
            value={formData.reason}
            onChange={handleChange}
            className="bg-gray-700 border border-gray-600 text-gray-200 p-2 rounded"
          />
        </div>
        <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded">Submit</button>
        {error && <p className="text-red-500 text-sm">{error}</p>}
      </form>
      <div>
        <h3 className="font-semibold text-gray-300 mb-2">Your leave history</h3>
        {leaves.length === 0 ? (
          <p className="text-gray-500 text-sm">No leave requests yet.</p>
        ) : (
          <table className="min-w-full border-collapse text-sm">
            <thead>
              <tr className="bg-gray-800">
                <th className="border border-gray-700 px-3 py-2 text-left">Type</th>
                <th className="border border-gray-700 px-3 py-2 text-left">Start</th>
                <th className="border border-gray-700 px-3 py-2 text-left">End</th>
                <th className="border border-gray-700 px-3 py-2 text-left">Status</th>
              </tr>
            </thead>
            <tbody>
              {leaves.map((leave) => (
                <tr key={leave.id} className="bg-gray-800">
                  <td className="border border-gray-700 px-3 py-2 capitalize">{leave.type}</td>
                  <td className="border border-gray-700 px-3 py-2">{leave.start_date}</td>
                  <td className="border border-gray-700 px-3 py-2">{leave.end_date}</td>
                  <td className="border border-gray-700 px-3 py-2 capitalize">{leave.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default LeavesPage;