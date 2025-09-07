import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { seedAdmin, login, upsertSettings } from '../lib/api.js';

/**
 * Getting Started page for initial configuration.
 *
 * This page is displayed when no users exist in the system. It allows the
 * organisation to provide a company name and create the first administrator.
 * After successfully seeding the admin and logging in, the user will be
 * redirected to the onboarding page to sign required agreements.
 */
function GettingStartedPage() {
  const navigate = useNavigate();
  const [companyName, setCompanyName] = useState('');
  const [logoUrl, setLogoUrl] = useState('');
  const [email, setEmail] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastInitial, setLastInitial] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      // Seed the admin user. This must be done before any users exist.
      await seedAdmin({
        email,
        first_name: firstName,
        last_initial: lastInitial,
        password,
      });
      // Log in with the seeded admin credentials to obtain a JWT.
      const tokenData = await login(email, password);
      localStorage.setItem('token', tokenData.access_token);
      // Upsert organisation settings using the admin token.
      await upsertSettings({
        company_name: companyName || null,
        logo_url: logoUrl || null,
      });
      setLoading(false);
      // Redirect to onboarding page after setup.
      navigate('/onboarding');
    } catch (err) {
      console.error(err);
      setError(err.message || 'Setup failed');
      setLoading(false);
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-900 text-gray-200">
      <div className="bg-gray-800 p-8 rounded-lg shadow-md w-full max-w-lg">
        <h2 className="text-3xl font-semibold mb-6 text-center">Getting Started</h2>
        <p className="mb-6 text-gray-400 text-sm text-center">
          Welcome! Let&#39;s set up your organisation and first administrator.
        </p>
        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col">
            <label className="text-gray-400 mb-1">Organisation Name</label>
            <input
              type="text"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              placeholder="e.g. Community Org"
              className="bg-gray-700 border border-gray-600 text-gray-200 p-2 rounded"
            />
          </div>
          <div className="flex flex-col">
            <label className="text-gray-400 mb-1">Logo URL (optional)</label>
            <input
              type="url"
              value={logoUrl}
              onChange={(e) => setLogoUrl(e.target.value)}
              placeholder="https://example.com/logo.png"
              className="bg-gray-700 border border-gray-600 text-gray-200 p-2 rounded"
            />
          </div>
          <hr className="border-gray-700 my-4" />
          <h3 className="text-xl font-semibold mb-2">Administrator Details</h3>
          <div className="flex flex-col">
            <label className="text-gray-400 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="bg-gray-700 border border-gray-600 text-gray-200 p-2 rounded"
            />
          </div>
          <div className="flex flex-col">
            <label className="text-gray-400 mb-1">First Name</label>
            <input
              type="text"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              required
              className="bg-gray-700 border border-gray-600 text-gray-200 p-2 rounded"
            />
          </div>
          <div className="flex flex-col">
            <label className="text-gray-400 mb-1">Last Initial</label>
            <input
              type="text"
              value={lastInitial}
              onChange={(e) => setLastInitial(e.target.value)}
              required
              maxLength={1}
              className="bg-gray-700 border border-gray-600 text-gray-200 p-2 rounded"
            />
          </div>
          <div className="flex flex-col">
            <label className="text-gray-400 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="bg-gray-700 border border-gray-600 text-gray-200 p-2 rounded"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded w-full mt-4"
          >
            {loading ? 'Setting up...' : 'Complete Setup'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default GettingStartedPage;