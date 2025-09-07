import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getOnboardingStatus, signOnboarding } from '../lib/api.js';

function OnboardingPage() {
  const navigate = useNavigate();
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchStatus() {
      try {
        const data = await getOnboardingStatus();
        setStatus(data);
      } catch (err) {
        setError(err.message);
        // Redirect to login if unauthenticated
        navigate('/login');
      }
    }
    fetchStatus();
  }, [navigate]);

  async function handleUpdate(e) {
    e.preventDefault();
    try {
      const update = {
        policy_signed: e.target.policy.checked,
        confidentiality_signed: e.target.confidentiality.checked,
      };
      const updated = await signOnboarding(update);
      setStatus(updated);
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  }

  if (!status) {
    return <p className="text-gray-300">Loading...</p>;
  }

  return (
    <div className="max-w-md mx-auto">
      <h2 className="text-lg font-semibold mb-4 text-gray-200">Onboarding Agreements</h2>
      {error && <p className="text-red-500 mb-2">{error}</p>}
      <form onSubmit={handleUpdate} className="flex flex-col gap-4 bg-gray-800 p-4 rounded-lg shadow">
        <label className="flex items-center gap-2 text-gray-300">
          <input
            type="checkbox"
            name="policy"
            defaultChecked={status.policy_signed}
            className="accent-blue-500 h-4 w-4"
          />
          <span>Policy Adherence Agreement signed</span>
        </label>
        <label className="flex items-center gap-2 text-gray-300">
          <input
            type="checkbox"
            name="confidentiality"
            defaultChecked={status.confidentiality_signed}
            className="accent-blue-500 h-4 w-4"
          />
          <span>Confidentiality Agreement signed</span>
        </label>
        <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md">Update</button>
      </form>
    </div>
  );
}

export default OnboardingPage;