import React, { useEffect, useState } from 'react';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { getCurrentUser, getSettings } from './lib/api.js';

/**
 * Layout component that provides a dark-themed navigation shell similar to
 * the example dashboard. It renders a sidebar, a top bar with security level
 * and user information, and a content area for nested pages. All pages
 * wrapped by this layout inherit the dark background and shared UI.
 */
export default function Layout() {
  const [currentUser, setCurrentUser] = useState(null);
  const [settings, setSettings] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  // Global search query state
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    // Add keyboard shortcut: focus search bar when '/' is pressed
    function handleKeyDown(e) {
      // Ignore if modifier keys pressed
      if (e.key === '/' && !e.metaKey && !e.ctrlKey && !e.altKey) {
        e.preventDefault();
        const input = document.getElementById('global-search-input');
        if (input) input.focus();
      }
    }
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  useEffect(() => {
    async function fetchUser() {
      try {
        const user = await getCurrentUser();
        setCurrentUser(user);
        // Fetch organisation settings after successful authentication
        try {
          const s = await getSettings();
          setSettings(s);
        } catch (err) {
          // It is fine if no settings exist yet
          console.warn('Failed to fetch settings', err);
        }
      } catch (err) {
        // Not authenticated; redirect to login
        navigate('/login');
      }
    }
    fetchUser();
  }, [navigate]);

  function handleLogout() {
    localStorage.removeItem('token');
    navigate('/login');
  }

  // Define navigation items with labels and routes. Configuration and editing
  // are consolidated under Settings. Webhooks are no longer listed separately.
  const navItems = [
    { label: 'Dashboard', path: '/' },
    { label: 'Onboarding', path: '/onboarding' },
    { label: 'Leaves', path: '/leaves' },
    { label: 'Tickets', path: '/tickets' },
    { label: 'Incidents', path: '/incidents' },
    { label: 'Appeals', path: '/appeals' },
    { label: 'BRAG', path: '/brag' },
    { label: 'Probations', path: '/probations' },
    { label: 'Training', path: '/training' },
    { label: 'Offboarding', path: '/offboarding' },
    { label: 'Settings', path: '/settings' },
    { label: 'Search', path: '/search' },
    { label: 'Approvals', path: '/approvals' },
    { label: 'Attachments', path: '/attachments' },
  ];

  return (
    <div className="flex h-screen bg-gray-900 text-gray-200 font-sans">
      {/* Sidebar */}
      <aside className="w-60 bg-gray-800 flex flex-col p-4 space-y-4">
        <div className="flex items-center space-x-2 mb-4">
          {/* Placeholder for organisation logo or icon */}
          {settings?.logo_url ? (
            <img src={settings.logo_url} alt="Logo" className="h-8 w-8 rounded-full object-cover" />
          ) : (
            <div className="bg-blue-600 rounded-full h-8 w-8 flex items-center justify-center text-sm font-bold">
              {settings?.company_name ? settings.company_name.charAt(0).toUpperCase() : 'CO'}
            </div>
          )}
          <div>
            <h2 className="text-lg font-semibold">
              {settings?.company_name || 'Community Org'}
            </h2>
            <p className="text-xs text-gray-400">HR System v3</p>
          </div>
        </div>
        <nav className="flex-1 space-y-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`block px-3 py-2 rounded-md hover:bg-gray-700 transition-colors ${
                  isActive ? 'bg-gray-700 text-white' : 'text-gray-300'
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
        <button
          onClick={handleLogout}
          className="mt-auto bg-red-600 hover:bg-red-700 text-white py-2 px-3 rounded-md text-sm"
        >
          Logout
        </button>
      </aside>
      {/* Main area */}
      <div className="flex-1 flex flex-col">
      {/* Top bar */}
      <header className="bg-gray-800 border-b border-gray-700 p-3 flex items-center justify-between space-x-4">
        {/* Left side: security banner and last update */}
        <div className="flex items-center space-x-2">
          <span className="bg-yellow-600 text-black text-xs font-semibold px-2 py-1 rounded-sm">
            Security Level: SL2 - ELEVATED
          </span>
          {/* Superuser badge */}
          {currentUser && currentUser.role && currentUser.role.clearance >= 5 && (
            <span className="bg-purple-700 text-white text-xs font-semibold px-2 py-1 rounded-sm">
              Superuser
            </span>
          )}
          <span className="text-sm text-gray-400">
            Last updated: {new Date().toISOString().split('T')[0]}
          </span>
        </div>
        {/* Centre: global search bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (searchQuery.trim()) {
              navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
            }
          }}
          className="flex flex-1 mx-4 max-w-xl"
        >
          <input
            id="global-search-input"
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search (press / to focus)…"
            className="flex-1 p-2 bg-gray-700 border border-gray-600 rounded text-gray-200 text-sm focus:outline-none"
          />
        </form>
        {/* Right side: user welcome and quick actions */}
        <div className="flex items-center space-x-3">
          {currentUser && (
            <span className="text-sm text-gray-300">
              Welcome, {currentUser.first_name}
            </span>
          )}
          {/* Quick Actions menu placeholder, could be expanded later */}
          <button
            onClick={() => {}}
            className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-md text-sm"
          >
            Quick Actions
          </button>
        </div>
      </header>
        {/* Content area */}
        <main className="flex-1 overflow-y-auto p-6 bg-gray-900">
          <Outlet />
        </main>
      </div>
    </div>
  );
}