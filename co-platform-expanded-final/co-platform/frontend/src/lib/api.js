// API helper functions for interacting with the backend.

const API_BASE = import.meta.env.VITE_API || 'http://localhost:8000';

function getAuthHeaders() {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function login(email, password) {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData,
  });
  if (!response.ok) {
    throw new Error('Login failed');
  }
  return response.json();
}

// User endpoints
export async function getCurrentUser() {
  const res = await fetch(`${API_BASE}/users/me`, {
    headers: {
      'Accept': 'application/json',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    throw new Error('Not authenticated');
  }
  return res.json();
}

// Onboarding endpoints
export async function getOnboardingStatus() {
  const res = await fetch(`${API_BASE}/onboarding/status`, {
    headers: {
      'Accept': 'application/json',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    throw new Error('Failed to fetch onboarding status');
  }
  return res.json();
}

export async function signOnboarding(data) {
  const res = await fetch(`${API_BASE}/onboarding/sign`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    throw new Error('Failed to update onboarding');
  }
  return res.json();
}

// Leave endpoints
export async function getLeaves() {
  const res = await fetch(`${API_BASE}/leaves/`, {
    headers: {
      'Accept': 'application/json',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    throw new Error('Failed to fetch leaves');
  }
  return res.json();
}

export async function createLeave(leave) {
  const res = await fetch(`${API_BASE}/leaves/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify(leave),
  });
  if (!res.ok) {
    const error = await res.text();
    throw new Error(error || 'Failed to create leave');
  }
  return res.json();
}

// Ticket endpoints
export async function getTickets() {
  const res = await fetch(`${API_BASE}/tickets/`, {
    headers: {
      'Accept': 'application/json',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    throw new Error('Failed to fetch tickets');
  }
  return res.json();
}

export async function createTicket(ticket) {
  const res = await fetch(`${API_BASE}/tickets/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify(ticket),
  });
  if (!res.ok) {
    throw new Error('Failed to create ticket');
  }
  return res.json();
}

// Incidents endpoints
export async function getIncidents() {
  const res = await fetch(`${API_BASE}/incidents/`, {
    headers: {
      'Accept': 'application/json',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    throw new Error('Failed to fetch incidents');
  }
  return res.json();
}

export async function createIncident(incident) {
  const res = await fetch(`${API_BASE}/incidents/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify(incident),
  });
  if (!res.ok) {
    throw new Error('Failed to create incident');
  }
  return res.json();
}

// Appeals endpoints
export async function getAppeals() {
  const res = await fetch(`${API_BASE}/appeals/`, {
    headers: {
      'Accept': 'application/json',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    throw new Error('Failed to fetch appeals');
  }
  return res.json();
}

export async function createAppeal(appeal) {
  const res = await fetch(`${API_BASE}/appeals/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify(appeal),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || 'Failed to create appeal');
  }
  return res.json();
}

// BRAG endpoints
export async function getBragEntries() {
  const res = await fetch(`${API_BASE}/brag/`, {
    headers: {
      'Accept': 'application/json',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    throw new Error('Failed to fetch BRAG entries');
  }
  return res.json();
}

export async function createBragEntry(entry) {
  const res = await fetch(`${API_BASE}/brag/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify(entry),
  });
  if (!res.ok) {
    throw new Error('Failed to create BRAG entry');
  }
  return res.json();
}

// Offboarding endpoints
export async function getOffboardings() {
  const res = await fetch(`${API_BASE}/offboarding/`, {
    headers: {
      'Accept': 'application/json',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    throw new Error('Failed to fetch offboarding records');
  }
  return res.json();
}

export async function createOffboarding(record) {
  const res = await fetch(`${API_BASE}/offboarding/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify(record),
  });
  if (!res.ok) {
    throw new Error('Failed to create offboarding record');
  }
  return res.json();
}

// Probation endpoints
export async function getProbations() {
  const res = await fetch(`${API_BASE}/probations/`, {
    headers: {
      'Accept': 'application/json',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    throw new Error('Failed to fetch probations');
  }
  return res.json();
}

export async function createProbation(probation) {
  const res = await fetch(`${API_BASE}/probations/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify(probation),
  });
  if (!res.ok) {
    const error = await res.text();
    throw new Error(error || 'Failed to create probation');
  }
  return res.json();
}

// Training endpoints
export async function getTrainingStatuses() {
  const res = await fetch(`${API_BASE}/training/`, {
    headers: {
      'Accept': 'application/json',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    throw new Error('Failed to fetch training status');
  }
  return res.json();
}

export async function createTrainingStatus(training) {
  const res = await fetch(`${API_BASE}/training/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify(training),
  });
  if (!res.ok) {
    const error = await res.text();
    throw new Error(error || 'Failed to create training status');
  }
  return res.json();
}

// -----------------------------------------------------------------------------
// System setup and settings endpoints

/**
 * Check whether any users exist in the system. Used to determine whether to
 * display the Getting Started page or the Login page.
 *
 * Returns an object of the form {exists: boolean}.
 */
export async function checkUsersExist() {
  const res = await fetch(`${API_BASE}/users/exists`, {
    headers: {
      'Accept': 'application/json',
    },
  });
  if (!res.ok) {
    throw new Error('Failed to check user existence');
  }
  return res.json();
}

/**
 * Seed the initial admin user. Only allowed if no users exist.
 *
 * @param {Object} userData - { email, first_name, last_initial, password }
 * @param {string} roleName - optional role name, defaults to "President".
 */
export async function seedAdmin(userData, roleName = 'President') {
  const res = await fetch(`${API_BASE}/users/seed-admin?role_name=${encodeURIComponent(roleName)}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || 'Failed to seed admin');
  }
  return res.json();
}

/**
 * Create or update organisation settings. Requires authentication with admin
 * privileges.
 *
 * @param {Object} settings - { company_name, logo_url }
 */
export async function upsertSettings(settings) {
  const res = await fetch(`${API_BASE}/settings/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify(settings),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || 'Failed to update settings');
  }
  return res.json();
}

/**
 * Retrieve the current organisation settings. Returns null if no settings exist.
 */
export async function getSettings() {
  const res = await fetch(`${API_BASE}/settings/`, {
    headers: {
      'Accept': 'application/json',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || 'Failed to fetch settings');
  }
  return res.json();
}

// -----------------------------------------------------------------------------
// Webhooks
//

export async function listWebhooks() {
  const res = await fetch(`${API_BASE}/webhooks/`, {
    headers: {
      'Accept': 'application/json',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    throw new Error('Failed to fetch webhooks');
  }
  return res.json();
}

export async function createWebhook(webhook) {
  const res = await fetch(`${API_BASE}/webhooks/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify(webhook),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || 'Failed to create webhook');
  }
  return res.json();
}

export async function updateWebhook(id, webhook) {
  const res = await fetch(`${API_BASE}/webhooks/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify(webhook),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || 'Failed to update webhook');
  }
  return res.json();
}

export async function deleteWebhook(id) {
  const res = await fetch(`${API_BASE}/webhooks/${id}`, {
    method: 'DELETE',
    headers: {
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || 'Failed to delete webhook');
  }
  return true;
}

// -----------------------------------------------------------------------------
// Approvals
//

export async function listApprovals() {
  const res = await fetch(`${API_BASE}/approvals/`, {
    headers: {
      'Accept': 'application/json',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    throw new Error('Failed to fetch approvals');
  }
  return res.json();
}

export async function createApproval(approval) {
  const res = await fetch(`${API_BASE}/approvals/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify(approval),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || 'Failed to create approval');
  }
  return res.json();
}

export async function updateApproval(id, approval) {
  const res = await fetch(`${API_BASE}/approvals/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify(approval),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || 'Failed to update approval');
  }
  return res.json();
}

// -----------------------------------------------------------------------------
// Attachments
//

export async function listAttachments() {
  const res = await fetch(`${API_BASE}/attachments/`, {
    headers: {
      'Accept': 'application/json',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    throw new Error('Failed to fetch attachments');
  }
  return res.json();
}

export async function createAttachment(att) {
  const res = await fetch(`${API_BASE}/attachments/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify(att),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || 'Failed to create attachment');
  }
  return res.json();
}

// -----------------------------------------------------------------------------
// Audit logs
//

export async function listAuditLogs() {
  const res = await fetch(`${API_BASE}/audit/logs`, {
    headers: {
      'Accept': 'application/json',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    throw new Error('Failed to fetch audit logs');
  }
  return res.json();
}

export async function verifyAuditHashChain() {
  const res = await fetch(`${API_BASE}/audit/verify-hash-chain`, {
    headers: {
      'Accept': 'application/json',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    throw new Error('Failed to verify audit chain');
  }
  return res.json();
}

export async function exportAuditLogs(format = 'json') {
  const res = await fetch(`${API_BASE}/audit/export?fmt=${format}`, {
    headers: {
      'Accept': 'application/json',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    throw new Error('Failed to export audit logs');
  }
  return res.json();
}

export async function getHealthStatus() {
  const res = await fetch(`${API_BASE}/health`, {
    headers: {
      'Accept': 'application/json',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    throw new Error('Failed to fetch health status');
  }
  return res.json();
}

// -----------------------------------------------------------------------------
// Search
//

export async function searchAll(query) {
  const res = await fetch(`${API_BASE}/search/?query=${encodeURIComponent(query)}`, {
    headers: {
      'Accept': 'application/json',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || 'Failed to search');
  }
  return res.json();
}

// -----------------------------------------------------------------------------
// Data Subject Access Request (DSAR) and Retention
//

/**
 * Export all data associated with the given user ID.
 * Only the user themselves or an admin may perform this operation.
 *
 * @param {number} userId
 */
export async function exportUserData(userId) {
  const res = await fetch(`${API_BASE}/dsar/${userId}`, {
    headers: {
      'Accept': 'application/json',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || 'Failed to export user data');
  }
  return res.json();
}

/**
 * Trigger a cleanup job to delete records older than the specified number of years.
 * Only administrators may call this.
 *
 * @param {number} retentionYears - number of years to retain data (default 4)
 */
export async function cleanupRetention(retentionYears = 4) {
  const res = await fetch(`${API_BASE}/retention/cleanup?retention_years=${retentionYears}`, {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || 'Failed to run retention cleanup');
  }
  return res.json();
}