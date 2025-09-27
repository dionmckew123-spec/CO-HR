# CO HR & Support Platform

This repository contains a fully‑featured HR, support and governance platform
designed for Community Organisation. It unifies employee onboarding, leave
management, ticketing, incident reporting, appeals, performance tracking,
probations, training modules, offboarding, approvals and audit into a single
system. A clean dark‑themed frontend (React + Vite) sits on top of a
FastAPI backend with PostgreSQL.

> **Note:** this project is a proof of concept. Many advanced features
> (multi‑step approvals, full‑text search, advanced audit logging, file
> uploads, etc.) are implemented as minimal stubs or skeletons. You are
> encouraged to extend and refine them for production use.

## Features

- **Getting Started wizard** – when the system is empty, a wizard collects
  your organisation name, logo URL and initial admin credentials, seeds the
  first user and logs you in automatically.
- **Onboarding** – sign policy and confidentiality agreements; supervisor
  records compliance. Probation status (pass/extend/fail) and training
  modules are tracked.
- **Leaves** – submit annual, emergency and sick leave requests; policy
  engine enforces min/max durations and allowances (see the policy).
- **Tickets & Incidents** – raise support tickets or incident reports with
  severity levels; view and manage your submissions.
- **Appeals** – lodge appeals against incidents or decisions with cooldown
  periods.
- **BRAG** – record behaviour/relationships/attitude/growth scores for
  weekly activity tracking.
- **Probations & Training** – track probation periods, results and
  training module completion.
- **Offboarding** – record resignation notice, asset return, knowledge
  transfer and access restriction.
* **Settings & Configuration** – a single Settings page consolidates all
  editable options: company name, logo, working days, public holidays,
  leave policy, default Discord channels per module, feature flags and the
  number of years to retain data. Superusers (clearance ≥ 5) can manage
  everything from here.
* **Discord Webhooks** – within Settings you can register multiple Discord
  webhook endpoints for granular events such as `ticket.created`,
  `leave.requested` or `incident.reported`. Webhooks can be toggled on/off,
  edited or deleted. Each event emits a JSON payload to the configured URL;
  if outbound HTTP is blocked, the payload is logged instead.
- **Approvals** – manage multi‑step approvals (e.g. leave requests or
  disciplinary cases) via the **Approvals** page. Administrators see all
  pending requests and can approve or deny them; the system updates the
  corresponding entity accordingly.
- **Attachments** – associate uploaded files with entities via the
  **Attachments** page. Provide an entity type, entity ID, file name and file
  path; the backend records the metadata while you handle the actual file
  upload.
- **Search** – perform a full‑text search across tickets, incidents, appeals,
  leaves, BRAG entries, probations, training and offboarding. Results are
  grouped by entity type. A global search bar is available at the top of
  every page (press `/` to focus it) so you can quickly search the whole
  system without navigating away.

- **Superuser badge** – users with clearance level 5 (superusers) see a purple
  “Superuser” badge in the top bar and bypass all permission checks.
- **Audit logs** – listable via API (clearance ≥ 5). Routers can record
  actions to the audit log; the demo includes minimal logging.
- **Data Privacy & Retention** – export all personal data for a user
  (DSAR) via the `/dsar/{user_id}` endpoint and run a retention cleanup via
  `/retention/cleanup` to purge records older than a chosen number of years.

## Module Specifications

### 5. Support Tickets

- **Severities** – categorise tickets as `minor`, `reportable` or `major`.
- **Queue Routing** – queues auto-route based on severity to ensure the
  right responders pick up work immediately.
- **Ticket Detail** – each ticket exposes its title, description, threaded
  comments, current assignee and status for rapid triage.
- **Lockdown Mode** – major incidents include a **Lockdown** toggle that is
  available to clearance level 4 and above; this freezes edits while the
  incident is under control.
- **Email Integration** – outbound SMTP sends notifications, while inbound
  IMAP automatically converts emails into tickets so teams can work from
  their inbox.

### 6. Disciplinary & Appeals

- **Disciplinary Stages** – track the full lifecycle across:
  1. Informal warning (supervisor-led).
  2. Formal / under investigation (visible to the Incident & Appeals
     Committee – IAC).
  3. Termination with immediate access removal.
  4. Automatic removal for the most severe cases.
- **Appeals Hub** – employees submit appeals, CL4+ Decision Committee
  members review them and the system enforces cooldowns between appeals.
- **Full Audit Trail** – disciplinary and appeals processes are written to
  employee history so reviewers can see every action.

### 7. Security Levels (SL1–SL5)

- **Global Banner** – a persistent banner shows the current security level
  (SL1 Normal through SL5 Crisis) across the app.
- **Dual Control Escalation** – raising the level demands approval from two
  CL4+/CL5 approvers to prevent unilateral escalation.
- **Immutable Record** – every change is logged to `SecurityLevelLog` and
  the audit trail for compliance.

### 8. Global Settings

- **Organisation & Branding** – configure organisation name, logo, support
  email and timezone.
- **Leave & Absence** – manage allowance, cycle, pro-rating and leave types
  in one view.
- **Email Integration** – review connection status and trigger a test email
  at any time.
- **Employee Numbering** – customise numbering patterns and the current
  counter.
- **Security & Retention** – toggle two-factor requirements, configure data
  retention in years and set file upload limits.
- **Permissions Editor** – edit permissions via a matrix combining clearance
  levels and role overrides.
- **Audited Changes** – every update captures before/after diffs for future
  review.

### 9. Audit & Compliance

- **Comprehensive Auditing** – record every action and sensitive read with
  the following schema: `ts_utc`, `actor_id`, `role_snapshot`, `ip`, `ua`,
  `session_id`, `action`, `entity`, `entity_id`, `before_json`,
  `after_json`, `meta`, `request_id`, `success`, `error`, `hash_prev`,
  `hash_curr`.
- **Tamper Evident** – a cryptographic hash chain provides tamper-evidence
  across the log.
- **Verification & Export** – expose `/audit/verify-hash-chain` to confirm
  integrity and offer signed CSV/JSON exports with detached signatures.
- **Retention Policy** – default retention is four years, with extensions
  granted by the IAC. A nightly job anonymises or deletes expired data.

### 10. Nightly Jobs (Scheduled Tasks)

- **02:00 UTC Run** – scheduled tasks trigger nightly and cover probation
  reminders, retention clean-up (excluding legal holds), database backups
  (rolling 14-day window), audit chain verification and IMAP ticket fetches.
- **Result Logging** – every job logs to the audit trail and raises alerts
  on failure so operators can respond quickly.

### 11. Dashboard (Dark Theme)

- **Headline Cards** – display total employees, pending leave, open tickets
  and upcoming probation endings.
- **Actionable Widgets** – quick actions for creating leave, opening new
  tickets, uploading employee files and adding employees.
- **Operational Insights** – visualise tickets by severity, show probation
  endings, pending leave approvals and outstanding onboarding items.
- **Oversight Feeds** – CL4+ users see recent audit events and the system
  health panel covering database, email, audit chain and nightly job status.
- **Role Awareness** – widget visibility adapts to the viewer’s clearance
  and permissions.

### 12. System Health

- **Endpoints** – `/health`, `/ready` and `/metrics` power health checks and
  infrastructure probes.
- **Metrics Suite** – track request counts, p95 latency, job durations,
  IMAP/SMTP success or failure rates and live open ticket counts for
  capacity planning.

## Prerequisites

- **Docker and Docker Compose** (simplest way to run the stack), or
  alternatively Python 3.11+ and Node.js 20+ if running services manually.

## Quick Start (Docker)

1. Clone or download this repository and extract it on your machine.
2. Navigate into the `co-platform` directory.
3. Run:

   ```bash
   docker compose up --build
   ```

   This will launch three containers:
   - `db`: PostgreSQL on port 5432
   - `api`: FastAPI backend on port 8000
   - `web`: Vite dev server on port 5173

4. Open your browser to `http://localhost:5173`. Since no users exist,
   you will be redirected to the **Getting Started** page.
5. Fill in your organisation name, optional logo URL and admin details.
   On submit the system seeds the admin, logs you in and sets your
   organisation settings. You’ll land on the Onboarding page to sign
   agreements.

6. Use the sidebar to navigate between features. The **Dashboard**
   summarises pending probations, leave approvals, tickets by severity and
   system health. To configure your organisation (name, logo, policies,
   webhooks, etc.), visit **Settings**.

## Running Without Docker

To run services manually:

1. Install dependencies:

   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt

   # Frontend
   cd ../frontend
   npm install
   ```

2. Create a PostgreSQL database (or use SQLite) and set the `DATABASE_URL`
   environment variable accordingly. Copy `.env.example` to `.env` and
   configure `JWT_SECRET` and `ALLOWED_ORIGINS`.

3. Start the backend:

   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

4. In a separate terminal, start the frontend:

   ```bash
   cd frontend
   npm run dev
   ```

5. Access `http://localhost:5173` in your browser and complete the
   Getting Started wizard as above.

## Configuring Webhooks

1. Navigate to **Settings** and scroll down to the **Webhook Notifications** section.
2. Add a new webhook by specifying the event type (e.g.
   `ticket.created`, `leave.requested`) and the Discord webhook URL.
   Optionally provide a description and toggle the active flag.
3. The system will deliver a JSON payload to the URL whenever the
   corresponding event occurs. Payloads include relevant IDs and
   attributes (see `services/discord.py` for details). If your
   environment blocks outbound requests, the payload will be logged
   instead.
4. Edit or delete webhooks via the table on this page. Only users with
   the `webhook.manage` permission (typically superusers) may manage
   webhooks.

## Approvals

Navigate to **Approvals** in the sidebar to view all outstanding approval
requests. Each entry shows the entity type, entity ID, stage and status.
Only users with the `approvals.manage` permission (e.g. superusers) can
approve or deny a request directly from the table. When an action is taken,
the approval record is updated and the requesting process (e.g. a leave
request) can proceed.

Approvals can be created via the API by posting to `/approvals/` with
`{ "entity_type": ..., "entity_id": ... }`. To integrate approvals with
your workflows, modify the relevant routers (e.g. leave requests or
incidents) to create an approval record and wait for approval before
changing the entity’s status.

## Attachments

Open the **Attachments** page to view all uploaded files and create new
attachment records. The form requires an entity type (e.g. `Ticket`),
entity ID, file name and file path. The file itself must be uploaded to
a location accessible by the backend (for example, `backend/app/static/uploads/`).
Only users with the `attachments.manage` permission can create or list
attachments. Once recorded, attachments appear in the table and can be
used as evidence in incident investigations or appeals.

## Search

Use the **Search** page to perform a simple full‑text search across
tickets, incidents, appeals, leaves, BRAG entries, probations,
training and offboarding. Enter a keyword and results are grouped by
entity type. You can extend the search page to link each result to its
detail page. The current implementation is naive; integrate a proper
search engine (e.g. PostgreSQL full‑text search or Elasticsearch) for
production use.

## Audit Logs

Audit logs are available via the API at `/audit-logs/` (clearance ≥ 5
required). The UI does not yet expose them. To record actions, add
`AuditLog` creation calls in each router (e.g. when approvals are updated
or webhooks are modified). Extend the Audit endpoints and build a
frontend view to explore audit records.

## Security & Permissions

- **Authentication** uses JWT tokens. Log in to the system to obtain a
  token; it is stored in `localStorage` and included in API requests.
* **Roles, Clearance & Permissions** – roles have clearance levels (1–5)
  and are associated with named permissions (e.g. `settings.edit`,
  `webhook.manage`, `audit.view`). Users with clearance level 5 are
  superusers and bypass permission checks entirely. Other roles must
  possess the appropriate permission to access management functions.
- **Password storage** uses bcrypt hashing.
- **Two‑factor authentication** is not yet implemented; it is recommended
  to enforce 2FA for staff logins.

## Customisation

- **Company name, logo & working week** – set these via the Settings page. The
  logo URL should be a publicly accessible link (e.g. hosted on your CDN).
  Extend the `Settings` model and UI to capture your organisation’s working
  days, public holidays and leave allowances per role.
- **Colour theme** – the frontend uses Tailwind CSS. Modify Tailwind
  classes or customise `src/index.css` to change colours and spacing.
- **New event types** – add new strings to your event catalogue and
  register webhooks accordingly. In the backend, trigger events by
  calling `send_webhook_event(event_type, payload, db)` wherever
  appropriate.
- **Approval flows** – integrate approvals into your leave and incident
  routers: create an approval record when a request is made and require an
  approval before changing the request status.
* **Retention & audit** – use the `/retention/cleanup` endpoint (requires
  the `privacy.retention` permission) to purge records older than a
  specified number of years. Schedule this operation periodically (e.g.
  via cron). Record actions via `AuditLog` by adding logging statements to
  your endpoints.
* **DSAR exports** – call `/dsar/{user_id}` from a user account (for your
  own data) or from an account with the `privacy.dsar` permission to obtain
  a JSON document containing all data about the specified user. The
  Settings page includes a button to export the current user’s data.

## Contributing

This project is intended as a foundation for a comprehensive HR and
governance system. Contributions are welcome – please fork the
repository and submit pull requests or propose new features.