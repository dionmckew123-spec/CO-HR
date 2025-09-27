# CO HR Platform – Super Simple Guide

This guide is for anyone who just wants to see the site running without
worrying about the extra details. Follow each step in order.

## Option A: Quick start with Docker (easiest)

1. Install **Docker Desktop** (includes Docker Compose).
2. Open a terminal in the `co-platform` folder.
3. Run:
   ```bash
   docker compose up --build
   ```
4. Wait until you see messages that the web server is ready on port 5173.
5. Open your browser at <http://localhost:5173>.
6. The first screen lets you set up the organisation name and first admin user.
   Fill in the form and submit it to log in.

To stop everything press `Ctrl+C` in the terminal, then run:
```bash
docker compose down
```

## Option B: Run it yourself (for laptops without Docker)

### 1. Get the tools
- Install **Python 3.11 or newer**.
- Install **Node.js 20 or newer** (this gives you `npm`).
- Install **PostgreSQL** or be ready to use SQLite.

### 2. Back-end (API)
```bash
cd co-platform/backend
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Set the environment variables (you can paste these into the same terminal):
```bash
export DATABASE_URL="postgresql://postgres:password@localhost:5432/postgres"
export JWT_SECRET="change-me"
export ALLOWED_ORIGINS="http://localhost:5173"
```
> Tip: No database? Replace `DATABASE_URL` with `sqlite:///./dev.db` to create a
> SQLite file next to the code.

Start the API:
```bash
uvicorn app.main:app --reload --port 8000
```

### 3. Front-end (website)
Open a **second** terminal:
```bash
cd co-platform/frontend
npm install
npm run dev -- --host
```

### 4. Use the site
- Visit <http://localhost:5173>.
- Complete the Getting Started form to create the first admin.
- After you log in you can explore Tickets, Leaves, Approvals, etc.

## Need to start again?
- Delete the SQLite file (`dev.db`) or reset your Postgres database.
- Clear your browser local storage if you stay logged in.

## Common issues
- **`pip install` or `npm install` fails:** check your internet connection or
  proxy settings.
- **Cannot connect to database:** make sure the `DATABASE_URL` points to a
  running database and the credentials are correct.
- **Blocked by CORS:** confirm `ALLOWED_ORIGINS` includes the URL you load the
  site from (usually `http://localhost:5173`).

You now have the platform running! 🚀
