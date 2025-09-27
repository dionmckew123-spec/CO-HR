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

## Audit Logs & Integrity

Audit logs are now available under the `/audit` namespace (clearance ≥ 5
required):

- `GET /audit/logs` returns the ordered audit feed.
- `GET /audit/verify-hash-chain` validates the tamper-evident hash chain
  and reports any gaps.
- `GET /audit/export?fmt=json|csv` exports the log with a detached HMAC
  signature so the payload can be verified offline.

To record actions, add `AuditLog` creation calls in each router (e.g.
when approvals are updated or webhooks are modified). Extend the Audit
endpoints and build a frontend view to explore audit records.

Nightly jobs automatically verify the audit chain and log outcomes in
the audit trail. Failures raise alerts that surface in the System Health
widget.

## System Health & Nightly Operations

The backend exposes `/health`, `/ready` and `/metrics` endpoints. These
drive the dashboard’s System Health card and can be scraped by external
monitoring. The health report lists any degraded components rather than
failing outright so the application remains usable while services are
restored.

Nightly maintenance runs at 02:00 UTC and performs probation reminders,
retention cleanup (respecting legal holds and extensions), simulated
database backups (retaining 14 days), audit hash-chain verification and
IMAP ticket ingestion. Results are written to the audit log and any
failures trigger alerts that appear in `/health`.

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
  the `privacy.retention` permission) to purge or anonymise records older
  than the default four-year window. Extensions can be managed via
  `/retention/extensions` to respect legal holds granted by the
  Information Assurance Council. Record actions via `AuditLog` by adding
  logging statements to your endpoints.
* **DSAR exports** – call `/dsar/{user_id}` from a user account (for your
  own data) or from an account with the `privacy.dsar` permission to obtain
  a JSON document containing all data about the specified user. The
  Settings page includes a button to export the current user’s data.

## Contributing

This project is intended as a foundation for a comprehensive HR and
governance system. Contributions are welcome – please fork the
repository and submit pull requests or propose new features.