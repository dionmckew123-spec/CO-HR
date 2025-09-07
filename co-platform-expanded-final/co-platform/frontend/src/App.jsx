import React from 'react';
import { Routes, Route } from 'react-router-dom';

// Pages
import LoginPage from './pages/Login.jsx';
import GettingStartedPage from './pages/GettingStarted.jsx';
import OnboardingPage from './pages/Onboarding.jsx';
import LeavesPage from './pages/Leaves.jsx';
import TicketsPage from './pages/Tickets.jsx';
import IncidentsPage from './pages/Incidents.jsx';
import AppealsPage from './pages/Appeals.jsx';
import BragPage from './pages/Brag.jsx';
import OffboardingPage from './pages/Offboarding.jsx';
import ProbationsPage from './pages/Probations.jsx';
import TrainingPage from './pages/Training.jsx';
import DashboardPage from './pages/Dashboard.jsx';
import SettingsPage from './pages/Settings.jsx';
import WebhooksPage from './pages/Webhooks.jsx';
import SearchPage from './pages/Search.jsx';
import ApprovalsPage from './pages/Approvals.jsx';
import AttachmentsPage from './pages/Attachments.jsx';

// Layout
import Layout from './Layout.jsx';

function App() {
  return (
    <Routes>
      {/* Public route for login */}
      <Route path="/login" element={<LoginPage />} />
      {/* Public route for initial setup */}
      <Route path="/getting-started" element={<GettingStartedPage />} />
      {/* Protected routes under the layout */}
      <Route path="/" element={<Layout />}>
        <Route index element={<DashboardPage />} />
        <Route path="onboarding" element={<OnboardingPage />} />
        <Route path="leaves" element={<LeavesPage />} />
        <Route path="tickets" element={<TicketsPage />} />
        <Route path="incidents" element={<IncidentsPage />} />
        <Route path="appeals" element={<AppealsPage />} />
        <Route path="brag" element={<BragPage />} />
        <Route path="offboarding" element={<OffboardingPage />} />
        <Route path="probations" element={<ProbationsPage />} />
        <Route path="training" element={<TrainingPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="webhooks" element={<WebhooksPage />} />
        <Route path="search" element={<SearchPage />} />
        <Route path="approvals" element={<ApprovalsPage />} />
        <Route path="attachments" element={<AttachmentsPage />} />
      </Route>
      {/* Fallback to login for any unknown routes */}
      <Route path="*" element={<LoginPage />} />
    </Routes>
  );
}

export default App;