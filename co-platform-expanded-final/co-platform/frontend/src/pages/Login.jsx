import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { login, checkUsersExist } from '../lib/api.js';

function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);

  // On mount, check if any users exist. If none, redirect to setup.
  useEffect(() => {
    async function checkExistence() {
      try {
        const result = await checkUsersExist();
        if (!result.exists) {
          navigate('/getting-started');
        }
      } catch (err) {
        console.error('Failed to check user existence', err);
      }
    }
    checkExistence();
  }, [navigate]);

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      const tokenData = await login(email, password);
      localStorage.setItem('token', tokenData.access_token);
      setError(null);
      navigate('/onboarding');
    } catch (err) {
      setError(err.message || 'Login failed');
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-900 text-gray-200">
      <div className="bg-gray-800 p-8 rounded-lg shadow-md w-full max-w-sm">
        <h2 className="text-2xl font-semibold mb-6 text-center">Login</h2>
        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
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
            <label className="text-gray-400 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="bg-gray-700 border border-gray-600 text-gray-200 p-2 rounded"
            />
          </div>
          <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded w-full">Login</button>
        </form>
      </div>
    </div>
  );
}

export default LoginPage;