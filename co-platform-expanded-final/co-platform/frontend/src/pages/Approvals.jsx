import React, { useEffect, useState } from 'react';
import { listApprovals, updateApproval } from '../lib/api.js';

/**
 * Approvals management page.
 *
 * Displays a list of approval requests (e.g. leave or incident approvals) and
 * allows users with sufficient clearance to approve or deny them. The page
 * retrieves all approval records via the API and renders a simple table. For
 * pending approvals, action buttons are provided. After an action is taken,
 * the list is refreshed.
 */
function ApprovalsPage() {
  const [approvals, setApprovals] = useState([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  async function loadApprovals() {
    try {
      const data = await listApprovals();
      setApprovals(data || []);
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to load approvals');
    }
  }

  useEffect(() => {
    loadApprovals();
  }, []);

  async function handleAction(id, status) {
    setMessage('');
    setError('');
    try {
      await updateApproval(id, { status });
      setMessage(`Approval ${status}`);
      await loadApprovals();
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to update approval');
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Approvals</h1>
      {error && <p className="text-red-400">{error}</p>}
      {message && <p className="text-green-400">{message}</p>}
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left text-gray-300 border-collapse">
          <thead className="bg-gray-700 uppercase text-gray-400">
            <tr>
              <th className="p-2">ID</th>
              <th className="p-2">Entity</th>
              <th className="p-2">Entity ID</th>
              <th className="p-2">Stage</th>
              <th className="p-2">Status</th>
              <th className="p-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {approvals.map((ap) => (
              <tr key={ap.id} className="border-b border-gray-700">
                <td className="p-2">{ap.id}</td>
                <td className="p-2">{ap.entity_type}</td>
                <td className="p-2">{ap.entity_id}</td>
                <td className="p-2">{ap.stage}</td>
                <td className="p-2">{ap.status}</td>
                <td className="p-2 space-x-2">
                  {ap.status === 'pending' ? (
                    <>
                      <button
                        onClick={() => handleAction(ap.id, 'approved')}
                        className="bg-green-600 hover:bg-green-700 text-white px-2 py-1 rounded"
                      >
                        Approve
                      </button>
                      <button
                        onClick={() => handleAction(ap.id, 'denied')}
                        className="bg-red-600 hover:bg-red-700 text-white px-2 py-1 rounded"
                      >
                        Deny
                      </button>
                    </>
                  ) : (
                    <span className="text-gray-400">No action</span>
                  )}
                </td>
              </tr>
            ))}
            {approvals.length === 0 && (
              <tr>
                <td colSpan="6" className="p-2 text-center text-gray-500">
                  No approvals found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ApprovalsPage;