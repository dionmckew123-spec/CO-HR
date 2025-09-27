const API_URL = 'api.php';

const state = {
  employees: [],
  filtered: [],
  editingId: null,
};

const tableBody = document.getElementById('employeeTable');
const emptyState = document.getElementById('emptyState');
const searchInput = document.getElementById('searchInput');
const departmentFilter = document.getElementById('departmentFilter');
const statusFilter = document.getElementById('statusFilter');
const totalEmployees = document.getElementById('totalEmployees');
const activeEmployees = document.getElementById('activeEmployees');
const departmentCount = document.getElementById('departmentCount');
const latestHire = document.getElementById('latestHire');
const dialog = document.getElementById('employeeDialog');
const form = document.getElementById('employeeForm');
const modalTitle = document.getElementById('modalTitle');
const submitButton = document.getElementById('submitButton');
const deleteButton = document.getElementById('deleteEmployee');
const openCreate = document.getElementById('openCreate');
const cancelDialog = document.getElementById('cancelDialog');
const closeDialog = document.getElementById('closeDialog');
const exportCsv = document.getElementById('exportCsv');
const rowTemplate = document.getElementById('rowTemplate');

async function request(url, options = {}) {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.error || 'Request failed');
  }

  return response.json();
}

function normalizeText(value) {
  return value?.toString().toLowerCase() ?? '';
}

function renderRows() {
  tableBody.innerHTML = '';
  if (!state.filtered.length) {
    emptyState.hidden = false;
    return;
  }
  emptyState.hidden = true;

  state.filtered.forEach((employee) => {
    const row = rowTemplate.content.firstElementChild.cloneNode(true);
    row.querySelector('[data-field="name"]').textContent = employee.name;
    row.querySelector('[data-field="role"]').textContent = employee.role;
    row.querySelector('[data-field="department"]').textContent = employee.department;
    row.querySelector('[data-field="email"]').textContent = employee.email;
    row.querySelector('[data-field="status"]').textContent = employee.status;
    row.querySelector('[data-field="startDate"]').textContent = employee.startDate;
    row.querySelector('[data-action="edit"]').addEventListener('click', () => openEdit(employee));
    tableBody.appendChild(row);
  });
}

function refreshFilters() {
  const departments = [...new Set(state.employees.map((emp) => emp.department))]
    .filter(Boolean)
    .sort((a, b) => a.localeCompare(b));

  departmentFilter.innerHTML = '<option value="">All departments</option>';
  departments.forEach((dept) => {
    const option = document.createElement('option');
    option.value = dept;
    option.textContent = dept;
    departmentFilter.appendChild(option);
  });
}

function refreshStats() {
  totalEmployees.textContent = state.employees.length;
  activeEmployees.textContent = state.employees.filter((emp) => emp.status === 'Active').length;
  departmentCount.textContent = new Set(state.employees.map((emp) => emp.department)).size;

  if (state.employees.length) {
    const sorted = [...state.employees].sort((a, b) => (a.startDate > b.startDate ? -1 : 1));
    const newest = sorted[0];
    latestHire.textContent = `${newest.name} (${newest.startDate})`;
  } else {
    latestHire.textContent = '—';
  }
}

function applyFilters() {
  const search = normalizeText(searchInput.value);
  const departmentValue = departmentFilter.value;
  const statusValue = statusFilter.value;

  state.filtered = state.employees.filter((emp) => {
    const matchesSearch = [emp.name, emp.role, emp.email]
      .map(normalizeText)
      .some((value) => value.includes(search));
    const matchesDepartment = !departmentValue || emp.department === departmentValue;
    const matchesStatus = !statusValue || emp.status === statusValue;
    return matchesSearch && matchesDepartment && matchesStatus;
  });

  renderRows();
}

async function loadEmployees() {
  try {
    const { data } = await request(API_URL);
    state.employees = data;
    applyFilters();
    refreshFilters();
    refreshStats();
  } catch (error) {
    console.error(error);
    alert(`Unable to load employees: ${error.message}`);
  }
}

function resetForm() {
  form.reset();
  form.id.value = '';
  state.editingId = null;
  deleteButton.hidden = true;
  modalTitle.textContent = 'Add a new teammate';
  submitButton.textContent = 'Save';
}

function openCreateModal() {
  resetForm();
  dialog.showModal();
}

function openEdit(employee) {
  resetForm();
  state.editingId = employee.id;
  modalTitle.textContent = 'Update employee';
  submitButton.textContent = 'Update';
  deleteButton.hidden = false;

  Object.entries(employee).forEach(([key, value]) => {
    if (form[key]) {
      form[key].value = value;
    }
  });

  dialog.showModal();
}

async function handleSubmit(event) {
  event.preventDefault();
  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());

  try {
    if (state.editingId) {
      payload.id = Number(state.editingId);
      await request(API_URL, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      });
    } else {
      await request(API_URL, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    }

    await loadEmployees();
    dialog.close();
  } catch (error) {
    console.error(error);
    alert(`Unable to save employee: ${error.message}`);
  }
}

async function handleDelete() {
  if (!state.editingId) return;
  if (!confirm('Remove this employee?')) return;

  try {
    await request(API_URL, {
      method: 'DELETE',
      body: JSON.stringify({ id: Number(state.editingId) }),
    });
    await loadEmployees();
    dialog.close();
  } catch (error) {
    console.error(error);
    alert(`Unable to delete employee: ${error.message}`);
  }
}

function downloadCsv() {
  if (!state.filtered.length) {
    alert('There are no employees to export.');
    return;
  }

  const headers = ['Name', 'Role', 'Department', 'Email', 'Status', 'Start Date'];
  const rows = state.filtered.map((emp) => [
    emp.name,
    emp.role,
    emp.department,
    emp.email,
    emp.status,
    emp.startDate,
  ]);

  const csvContent = [headers, ...rows]
    .map((cols) =>
      cols
        .map((value) => {
          const safe = String(value).replace(/"/g, '""');
          return /[",\n]/.test(safe) ? `"${safe}"` : safe;
        })
        .join(',')
    )
    .join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'employees.csv';
  link.click();
  URL.revokeObjectURL(url);
}

searchInput.addEventListener('input', applyFilters);
departmentFilter.addEventListener('change', applyFilters);
statusFilter.addEventListener('change', applyFilters);
form.addEventListener('submit', handleSubmit);
deleteButton.addEventListener('click', handleDelete);
openCreate.addEventListener('click', openCreateModal);
cancelDialog.addEventListener('click', () => dialog.close());
closeDialog.addEventListener('click', () => dialog.close());
exportCsv.addEventListener('click', downloadCsv);

dialog.addEventListener('close', resetForm);

document.addEventListener('DOMContentLoaded', loadEmployees);
