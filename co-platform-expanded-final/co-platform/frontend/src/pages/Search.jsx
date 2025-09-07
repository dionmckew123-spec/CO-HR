import React, { useState, useEffect } from 'react';
import { searchAll } from '../lib/api.js';
import { useLocation, useNavigate } from 'react-router-dom';

/**
 * Search page.
 *
 * Provides a simple full-text search across multiple entities. Results are
 * displayed in groups by entity type. Clickable links are not implemented
 * yet; this page focuses on surfacing information quickly.
 */
function SearchPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Parse query parameter on load
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const q = params.get('q') || '';
    setQuery(q);
    if (q) {
      performSearch(q);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.search]);

  async function performSearch(q) {
    setError('');
    setLoading(true);
    try {
      const data = await searchAll(q);
      setResults(data);
    } catch (err) {
      console.error(err);
      setError(err.message || 'Search failed');
    }
    setLoading(false);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    // update URL query string for bookmarking/back navigation
    navigate(`/search?q=${encodeURIComponent(query)}`);
    if (query.trim()) {
      performSearch(query.trim());
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Search</h1>
      <form onSubmit={handleSubmit} className="flex space-x-2 max-w-md">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search..."
            className="flex-grow p-2 bg-gray-700 border border-gray-600 rounded text-gray-200"
          />
          <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
            {loading ? 'Searching...' : 'Search'}
          </button>
      </form>
      {error && <p className="text-red-500">{error}</p>}
      {results && (
        <div className="space-y-4">
          {Object.entries(results).map(([entity, items]) => (
            <div key={entity}>
              <h2 className="text-xl font-semibold capitalize mb-2">{entity}</h2>
              {items.length === 0 ? (
                <p className="text-gray-400 text-sm">No results</p>
              ) : (
                <ul className="list-disc list-inside space-y-1 text-gray-300">
                  {items.map((item) => (
                    <li key={item.id}>{item.summary}</li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default SearchPage;