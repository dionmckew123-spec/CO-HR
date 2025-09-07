import { useEffect, useState } from 'react';
import {
  getProbations,
  getLeaves,
  getTickets,
  getOnboardingStatus,
  getIncidents,
} from '../lib/api.js';

import { Link } from 'react-router-dom';

/**
 * Dashboard page summarising HR metrics and offering quick actions. The layout
 * mirrors the example dark-themed dashboard: quick action buttons, summary cards
 * for probations, leave requests, tickets by severity, onboarding tasks,
 * recent audit events and system health.
 */
export default function DashboardPage() {
  const [probations, setProbations] = useState([]);
  const [leaves, setLeaves] = useState([]);
  const [tickets, setTickets] = useState([]);
  const [onboarding, setOnboarding] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchData() {
      try {
        const [probationData, leaveData, ticketData, onboardingData, incidentData] = await Promise.all([
          getProbations(),
          getLeaves(),
          getTickets(),
          getOnboardingStatus(),
          getIncidents(),
        ]);
        setProbations(probationData || []);
        setLeaves(leaveData || []);
        setTickets(ticketData || []);
        setOnboarding(onboardingData || null);
        setIncidents(incidentData || []);
      } catch (err) {
        console.error(err);
        setError('Failed to load dashboard data');
      }
    }
    fetchData();
  }, []);

  // Compute derived metrics
  const probationsEndingSoon = probations.filter((p) => {
    const end = new Date(p.end_date);
    const now = new Date();
    const diffDays = (end - now) / (1000 * 60 * 60 * 24);
    return diffDays >= 0 && diffDays <= 7;
  });

  const pendingLeaves = leaves.filter((l) => l.status === 'pending');

  const openTickets = tickets.filter((t) => t.status === 'open');
  const ticketCounts = openTickets.reduce(
    (acc, t) => {
      // Map to human-friendly categories similar to the example: Minor, Reportable, Major
      let category;
      switch (t.severity) {
        case 'low':
          category = 'Minor';
          break;
        case 'minor':
          category = 'Reportable';
          break;
        case 'major':
          category = 'Major';
          break;
        case 'critical':
        default:
          category = 'Critical';
      }
      acc[category] = (acc[category] || 0) + 1;
      return acc;
    },
    {}
  );

  // Determine outstanding onboarding tasks
  let outstandingOnboarding = [];
  if (onboarding) {
    if (!onboarding.policy_signed) outstandingOnboarding.push('Policy Agreement');
    if (!onboarding.confidentiality_signed) outstandingOnboarding.push('Confidentiality Agreement');
  }

  // Recent events: combine recent leaves, tickets, incidents by date (descending)
  const recentEvents = [];
  leaves.slice().forEach((leave) => {
    recentEvents.push({
      type: 'Leave',
      date: leave.start_date,
      description: `${leave.type.charAt(0).toUpperCase() + leave.type.slice(1)} leave ${leave.status}`,
    });
  });
  tickets.slice().forEach((ticket) => {
    recentEvents.push({
      type: 'Ticket',
      date: ticket.id ? new Date().toISOString().split('T')[0] : '',
      description: `${ticket.title} (${ticket.severity})`,
    });
  });
  incidents.slice().forEach((inc) => {
    recentEvents.push({
      type: 'Incident',
      date: inc.date,
      description: inc.description,
    });
  });
  recentEvents.sort((a, b) => new Date(b.date) - new Date(a.date));
  const latestEvents = recentEvents.slice(0, 5);

  // Static system health status
  const systemHealth = [
    { name: 'Database', status: 'Healthy', color: 'text-green-400' },
    { name: 'Email Service', status: 'N/A', color: 'text-gray-400' },
    { name: 'Audit Chain', status: 'Healthy', color: 'text-green-400' },
    { name: 'Next Check', status: 'Jan 15, 02:00', color: 'text-gray-400' },
  ];

  return (
    <div className="space-y-6">
      {error && <div className="text-red-500">{error}</div>}
      {/* Quick actions */}
      <div className="flex flex-wrap gap-4 mb-4">
          <Link
            to="/leaves"
            className="flex-1 min-w-[150px] bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-lg text-center"
          >
            Create Leave Request
          </Link>
          <Link
            to="/tickets"
            className="flex-1 min-w-[150px] bg-indigo-600 hover:bg-indigo-700 text-white p-3 rounded-lg text-center"
          >
            New Support Ticket
          </Link>
          <Link
            to="/probations"
            className="flex-1 min-w-[150px] bg-purple-600 hover:bg-purple-700 text-white p-3 rounded-lg text-center"
          >
            Upload Employee File
          </Link>
          <Link
            to="/training"
            className="flex-1 min-w-[150px] bg-teal-600 hover:bg-teal-700 text-white p-3 rounded-lg text-center"
          >
            Add Employee
          </Link>
      </div>
      {/* Summary cards grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Probations ending soon */}
        <div className="bg-gray-800 p-4 rounded-lg shadow">
          <h3 className="text-sm uppercase text-gray-400 mb-3">Probation Ending Soon</h3>
          {probationsEndingSoon.length === 0 ? (
            <p className="text-gray-500 text-sm">No probations ending soon.</p>
          ) : (
            <ul className="space-y-2 text-sm">
              {probationsEndingSoon.map((p) => (
                <li key={p.id} className="flex justify-between">
                  <span>Probation #{p.id}</span>
                  <span>{p.end_date}</span>
                </li>
              ))}
              <li>
                <a href="/probations" className="text-blue-400 hover:underline text-xs">
                  View All Probations →
                </a>
              </li>
            </ul>
          )}
        </div>
        {/* Pending leave approvals */}
        <div className="bg-gray-800 p-4 rounded-lg shadow">
          <h3 className="text-sm uppercase text-gray-400 mb-3">Pending Leave Approvals</h3>
          {pendingLeaves.length === 0 ? (
            <p className="text-gray-500 text-sm">No pending leave requests.</p>
          ) : (
            <ul className="space-y-2 text-sm">
              {pendingLeaves.map((l) => (
                <li key={l.id} className="flex justify-between">
                  <span>{l.type.charAt(0).toUpperCase() + l.type.slice(1)} leave</span>
                  <span>
                    {l.start_date} - {l.end_date}
                  </span>
                </li>
              ))}
              <li>
                <a href="/leaves" className="text-blue-400 hover:underline text-xs">
                  View All Requests →
                </a>
              </li>
            </ul>
          )}
        </div>
        {/* Open tickets by severity */}
        <div className="bg-gray-800 p-4 rounded-lg shadow">
          <h3 className="text-sm uppercase text-gray-400 mb-3">Open Tickets by Severity</h3>
          {Object.keys(ticketCounts).length === 0 ? (
            <p className="text-gray-500 text-sm">No open tickets.</p>
          ) : (
            <ul className="space-y-1 text-sm">
              {Object.entries(ticketCounts).map(([severity, count]) => (
                <li key={severity} className="flex justify-between">
                  <span>{severity}</span>
                  <span className="font-semibold text-white">{count}</span>
                </li>
              ))}
              <li>
                <a href="/tickets" className="text-blue-400 hover:underline text-xs">
                  View All Tickets →
                </a>
              </li>
            </ul>
          )}
        </div>
        {/* Outstanding onboarding */}
        <div className="bg-gray-800 p-4 rounded-lg shadow">
          <h3 className="text-sm uppercase text-gray-400 mb-3">Outstanding Onboarding</h3>
          {outstandingOnboarding.length === 0 ? (
            <p className="text-gray-500 text-sm">No outstanding onboarding tasks.</p>
          ) : (
            <ul className="space-y-1 text-sm">
              {outstandingOnboarding.map((task, idx) => (
                <li key={idx}>{task}</li>
              ))}
              <li>
                <a href="/onboarding" className="text-blue-400 hover:underline text-xs">
                  Complete Onboarding →
                </a>
              </li>
            </ul>
          )}
        </div>
        {/* Recent audit events */}
        <div className="bg-gray-800 p-4 rounded-lg shadow">
          <h3 className="text-sm uppercase text-gray-400 mb-3">Recent Audit Events</h3>
          {latestEvents.length === 0 ? (
            <p className="text-gray-500 text-sm">No recent events.</p>
          ) : (
            <ul className="space-y-1 text-sm">
              {latestEvents.map((ev, idx) => (
                <li key={idx} className="flex justify-between">
                  <span>{ev.type}</span>
                  <span className="text-right">{ev.description}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
        {/* System health */}
        <div className="bg-gray-800 p-4 rounded-lg shadow">
          <h3 className="text-sm uppercase text-gray-400 mb-3">System Health</h3>
          <ul className="space-y-1 text-sm">
            {systemHealth.map((item) => (
              <li key={item.name} className="flex justify-between">
                <span>{item.name}</span>
                <span className={item.color}>{item.status}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}