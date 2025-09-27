# CO-HR Workforce Hub

This is a compact human resources portal implemented with **PHP**, **HTML**, **CSS**, and **JavaScript**. It is designed as a lightweight alternative to the larger CO Platform backend, offering a simple employee directory that can be hosted on any PHP-ready web server.

## Features

- 📊 Interactive dashboard cards that highlight total headcount, active employees, department coverage, and most recent hire
- 🔍 Real-time search, status, and department filtering without page reloads
- ➕ Modal-based employee creation and editing with validation
- 🗑️ Employee removal with confirmation safeguards
- 📄 CSV export of the current filtered view for easy sharing
- ☁️ API-first PHP backend that persists data in a JSON file (no database required)

## Project structure

```
hr-system/
├── api.php              # REST-style PHP endpoint for CRUD operations
├── data/
│   └── employees.json   # Lightweight data store for employee records
├── index.php            # Application shell and layout
└── assets/
    ├── app.js           # Front-end logic for fetching, filtering, and forms
    └── style.css        # Responsive styling with light/dark support
```

## Getting started

1. Ensure you have PHP 8.1+ installed.
2. From the repository root, start a local PHP development server:

   ```bash
   php -S localhost:8000 -t hr-system
   ```

3. Visit [http://localhost:8000](http://localhost:8000) in your browser.

All employee data is stored in `data/employees.json`. The API stores IDs sequentially; you can seed additional employees by editing the file before starting the server.

## API overview

| Method | Path    | Description                         |
| ------ | ------- | ----------------------------------- |
| GET    | api.php | Retrieve all employee records       |
| POST   | api.php | Create a new employee               |
| PATCH  | api.php | Update an existing employee by `id` |
| DELETE | api.php | Remove an employee by `id`          |

Requests should send JSON payloads and will receive JSON responses. Validation errors return HTTP 422 with a descriptive message.

## Notes

- The API enables CORS and handles preflight requests, which allows the bundle to be embedded into other platforms.
- Because the JSON file is the system of record, make sure the server has write permissions on the `data/` directory.
- For production deployments consider integrating the API with an SQL database, authentication, and audit logging.
