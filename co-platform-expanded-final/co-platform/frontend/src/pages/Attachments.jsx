import React, { useEffect, useState } from 'react';
import { listAttachments, createAttachment } from '../lib/api.js';

/**
 * Attachments management page.
 *
 * Provides a list of all uploaded attachments and a simple form for
 * creating a new attachment record. Note: this form only records
 * metadata (entity type, id, file name, path). Actual file upload
 * must be handled separately (e.g. uploading to the server's static
 * directory) and the file path should point to the stored file on
 * the server. This design keeps the demo simple and avoids dealing
 * with multipart uploads in the browser.
 */
function AttachmentsPage() {
  const [attachments, setAttachments] = useState([]);
  const [entityType, setEntityType] = useState('Ticket');
  const [entityId, setEntityId] = useState('');
  const [fileName, setFileName] = useState('');
  const [filePath, setFilePath] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  async function loadAttachments() {
    try {
      const data = await listAttachments();
      setAttachments(data || []);
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to fetch attachments');
    }
  }

  useEffect(() => {
    loadAttachments();
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setMessage('');
    setError('');
    try {
      await createAttachment({
        entity_type: entityType,
        entity_id: parseInt(entityId),
        file_name: fileName,
        file_path: filePath,
      });
      setMessage('Attachment created');
      setEntityType('Ticket');
      setEntityId('');
      setFileName('');
      setFilePath('');
      await loadAttachments();
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to create attachment');
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Attachments</h1>
      {error && <p className="text-red-400">{error}</p>}
      {message && <p className="text-green-400">{message}</p>}
      <div className="bg-gray-800 p-4 rounded-lg max-w-md">
        <h2 className="text-lg font-semibold mb-3">New Attachment</h2>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="block text-gray-400 mb-1">Entity Type</label>
            <select
              value={entityType}
              onChange={(e) => setEntityType(e.target.value)}
              className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-gray-200"
            >
              <option value="Ticket">Ticket</option>
              <option value="Incident">Incident</option>
              <option value="Appeal">Appeal</option>
              <option value="LeaveRequest">Leave</option>
              <option value="ProbationStatus">Probation</option>
              <option value="TrainingStatus">Training</option>
              <option value="Offboarding">Offboarding</option>
            </select>
          </div>
          <div>
            <label className="block text-gray-400 mb-1">Entity ID</label>
            <input
              type="number"
              value={entityId}
              onChange={(e) => setEntityId(e.target.value)}
              className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-gray-200"
              required
            />
          </div>
          <div>
            <label className="block text-gray-400 mb-1">File Name</label>
            <input
              type="text"
              value={fileName}
              onChange={(e) => setFileName(e.target.value)}
              className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-gray-200"
              required
            />
          </div>
          <div>
            <label className="block text-gray-400 mb-1">File Path</label>
            <input
              type="text"
              value={filePath}
              onChange={(e) => setFilePath(e.target.value)}
              className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-gray-200"
              required
            />
          </div>
          <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded">
            Create Attachment
          </button>
        </form>
      </div>
      {/* List attachments */}
      <div className="overflow-x-auto">
        <h2 className="text-lg font-semibold mb-2">Existing Attachments</h2>
        <table className="w-full text-sm text-left text-gray-300 border-collapse">
          <thead className="bg-gray-700 uppercase text-gray-400">
            <tr>
              <th className="p-2">ID</th>
              <th className="p-2">Entity</th>
              <th className="p-2">Entity ID</th>
              <th className="p-2">File Name</th>
              <th className="p-2">File Path</th>
              <th className="p-2">Uploaded At</th>
            </tr>
          </thead>
          <tbody>
            {attachments.map((att) => (
              <tr key={att.id} className="border-b border-gray-700">
                <td className="p-2">{att.id}</td>
                <td className="p-2">{att.entity_type}</td>
                <td className="p-2">{att.entity_id}</td>
                <td className="p-2">{att.file_name}</td>
                <td className="p-2">{att.file_path}</td>
                <td className="p-2">{att.uploaded_at}</td>
              </tr>
            ))}
            {attachments.length === 0 && (
              <tr>
                <td colSpan="6" className="p-2 text-center text-gray-500">
                  No attachments found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default AttachmentsPage;