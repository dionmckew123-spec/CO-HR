<?php
?><!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>CO-HR Workforce Hub</title>
    <link rel="stylesheet" href="assets/style.css" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
      rel="stylesheet"
    />
  </head>
  <body>
    <header class="app-header">
      <div>
        <h1>CO-HR Workforce Hub</h1>
        <p class="subtitle">
          Lightweight human resources portal for employee records, onboarding, and team
          insights.
        </p>
      </div>
      <div class="header-actions">
        <button id="exportCsv" class="ghost">Export CSV</button>
        <button id="openCreate" class="primary">Add Employee</button>
      </div>
    </header>

    <main class="layout">
      <section class="panel stats">
        <h2>Organization Snapshot</h2>
        <div class="stat-grid">
          <article class="stat-card">
            <p>Total Employees</p>
            <h3 id="totalEmployees">0</h3>
          </article>
          <article class="stat-card">
            <p>Active Employees</p>
            <h3 id="activeEmployees">0</h3>
          </article>
          <article class="stat-card">
            <p>Departments</p>
            <h3 id="departmentCount">0</h3>
          </article>
          <article class="stat-card">
            <p>Most Recent Hire</p>
            <h3 id="latestHire">—</h3>
          </article>
        </div>
      </section>

      <section class="panel" aria-labelledby="employeeDirectory">
        <div class="panel-header">
          <div>
            <h2 id="employeeDirectory">Employee Directory</h2>
            <p class="subtitle">Search, filter, and manage your workforce in real time.</p>
          </div>
          <div class="filters">
            <input id="searchInput" type="search" placeholder="Search name, role, email" />
            <select id="departmentFilter" aria-label="Filter by department">
              <option value="">All departments</option>
            </select>
            <select id="statusFilter" aria-label="Filter by employment status">
              <option value="">All statuses</option>
              <option value="Active">Active</option>
              <option value="On Leave">On Leave</option>
              <option value="Former">Former</option>
            </select>
          </div>
        </div>

        <div class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th scope="col">Name</th>
                <th scope="col">Role</th>
                <th scope="col">Department</th>
                <th scope="col">Email</th>
                <th scope="col">Status</th>
                <th scope="col">Start Date</th>
                <th scope="col" class="sr-only">Actions</th>
              </tr>
            </thead>
            <tbody id="employeeTable"></tbody>
          </table>
          <p id="emptyState" class="empty" hidden>No employees match your filters.</p>
        </div>
      </section>
    </main>

    <dialog id="employeeDialog" class="modal">
      <form id="employeeForm" method="dialog">
        <header>
          <h2 id="modalTitle">Add a new teammate</h2>
          <button type="button" id="closeDialog" aria-label="Close" class="ghost">✕</button>
        </header>

        <div class="form-grid">
          <label>
            Full name
            <input name="name" required placeholder="Jordan Lee" />
          </label>
          <label>
            Email
            <input name="email" type="email" required placeholder="jordan.lee@example.com" />
          </label>
          <label>
            Department
            <input name="department" required placeholder="Design" />
          </label>
          <label>
            Role
            <input name="role" required placeholder="Product Designer" />
          </label>
          <label>
            Employment status
            <select name="status" required>
              <option value="Active" selected>Active</option>
              <option value="On Leave">On Leave</option>
              <option value="Former">Former</option>
            </select>
          </label>
          <label>
            Start date
            <input name="startDate" type="date" required />
          </label>
        </div>

        <footer>
          <button type="button" id="deleteEmployee" class="danger" hidden>Delete</button>
          <div class="footer-actions">
            <button type="button" class="ghost" id="cancelDialog">Cancel</button>
            <button type="submit" class="primary" id="submitButton">Save</button>
          </div>
        </footer>

        <input type="hidden" name="id" />
      </form>
    </dialog>

    <template id="rowTemplate">
      <tr>
        <th scope="row" data-field="name"></th>
        <td data-field="role"></td>
        <td data-field="department"></td>
        <td data-field="email"></td>
        <td data-field="status"></td>
        <td data-field="startDate"></td>
        <td class="row-actions">
          <button type="button" class="ghost small" data-action="edit">Edit</button>
        </td>
      </tr>
    </template>

    <script src="assets/app.js" type="module"></script>
  </body>
</html>
