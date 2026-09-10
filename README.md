# Meridian HR — Employee Management System

A full-stack Employee Management System with secure CRUD workflows for employee
records, daily attendance, and leave requests.

- **Backend:** Django 5.2 LTS + Django REST Framework, JWT authentication (access +
  refresh with blacklist-on-logout), role-based permissions (Admin / HR / Employee).
- **Frontend:** React 18 + Vite, React Router, Axios (with automatic token refresh).

This has been built and verified end-to-end in a clean environment: dependencies
install without conflicts, migrations apply cleanly, the demo data seeds correctly,
and the full login → create employee → check in → apply for leave → approve leave
flow was tested against the live API before delivery. The React app also builds
cleanly to a production bundle.

---

## 1. Features

| Area | Admin / HR | Employee |
|---|---|---|
| Employee records | Full CRUD, search, filter by department/status | Read own profile only (`/employees/me/`) |
| Attendance | View & correct any employee's records, filter by date | Self check-in / check-out, view own history |
| Leave | View all requests, approve/reject with a comment | Apply, view own requests, cancel while pending |
| Departments & leave types | Full CRUD | Read-only |

Security highlights:
- JWT auth (`djangorestframework-simplejwt`) — short-lived access tokens (30 min),
  rotating refresh tokens (1 day) that are blacklisted on logout or rotation.
- Every endpoint requires authentication; write access to employee/attendance/leave
  data outside your own record requires the `ADMIN` or `HR` role, enforced server-side
  with DRF permission classes (never trust the frontend alone).
- Login is rate-limited (`10/min`) via DRF throttling to blunt brute-force attempts.
- Passwords go through Django's built-in validators (`MinimumLengthValidator`,
  `CommonPasswordValidator`, etc.) and are hashed with Django's default PBKDF2 hasher.
- CORS is locked to an explicit allow-list of frontend origins, not `*`.
- Production settings (`DEBUG=False`) automatically turn on HSTS, secure cookies, and
  SSL redirect.

---

## 2. Project structure

```
ems/
├── backend/                 # Django + DRF API
│   ├── ems_backend/         # settings, urls, wsgi/asgi
│   ├── accounts/            # custom User model, JWT login/logout, permissions
│   ├── employees/           # Employee & Department CRUD
│   ├── attendance/          # check-in/out + attendance history
│   ├── leaves/               # leave types + leave request workflow
│   ├── requirements.txt
│   └── .env.example
└── frontend/                 # React + Vite SPA
    ├── src/
    │   ├── api/              # axios client + typed resource calls
    │   ├── context/          # auth context (JWT storage, login/logout)
    │   ├── components/       # Layout, ProtectedRoute, StatusBadge
    │   └── pages/            # Login, Dashboard, Employees, Attendance, Leaves
    ├── package.json
    └── .env.example
```

---

## 3. Backend setup

Requires **Python 3.11–3.13**.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env             # then edit SECRET_KEY at minimum
python manage.py makemigrations
python manage.py migrate

# Optional: create demo Admin/HR/Employee accounts + sample departments/leave types
python manage.py seed_demo_data

# Or create your own superuser instead:
# python manage.py createsuperuser

python manage.py runserver
```

The API is now live at `http://127.0.0.1:8000/api/`. Django admin is at `/admin/`.

**Demo accounts** created by `seed_demo_data`:

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `AdminPass123!` |
| HR | `hr_manager` | `HrPass123!` |
| Employee | `jdoe` | `EmployeePass123!` |

Change or delete these before deploying anywhere reachable by the public.

### Key API endpoints

```
POST   /api/auth/login/              Obtain access + refresh token
POST   /api/auth/refresh/            Refresh an access token
POST   /api/auth/logout/             Blacklist a refresh token

GET    /api/employees/               List (Admin/HR)
POST   /api/employees/               Create employee + linked login (Admin/HR)
GET    /api/employees/me/            Own profile (any authenticated user)
PATCH  /api/employees/{id}/          Update (Admin/HR)
DELETE /api/employees/{id}/          Remove (Admin/HR)
GET    /api/employees/departments/   List departments

POST   /api/attendance/check-in/     Self check-in
POST   /api/attendance/check-out/    Self check-out
GET    /api/attendance/my-history/   Own attendance history
GET    /api/attendance/              All records (Admin/HR), filter by ?date=&employee=

POST   /api/leaves/                  Apply for leave
GET    /api/leaves/my-requests/      Own leave requests
POST   /api/leaves/{id}/cancel/      Cancel a pending request
POST   /api/leaves/{id}/review/      Approve/reject (Admin/HR) — body: {"action":"APPROVE"|"REJECT","comment":"..."}
GET    /api/leaves/                  All requests (Admin/HR), filter by ?status=
GET    /api/leaves/types/            List leave types
```

---

## 4. Frontend setup

Requires **Node.js 18.18+ or 20+** (Vite 5's minimum).

```bash
cd frontend
cp .env.example .env      # points VITE_API_BASE_URL at the backend above
npm install
npm run dev
```

Visit `http://localhost:5173`. Sign in with one of the demo accounts above, or a
user you created yourself. `npm run build` produces a production bundle in `dist/`.

---

## 5. Version notes

`backend/requirements.txt` and `frontend/package.json` are pinned to specific,
currently-supported releases (checked September 2026):

- **Django 5.2.6** — LTS, supported with security fixes through April 2028.
- **djangorestframework 3.16.1**, **djangorestframework-simplejwt 5.5.1** — latest
  stable releases compatible with Django 5.2.
- **React 18.3.1** + **react-router-dom 6.30.1** — the widely-adopted, stable
  lineage. React 19.2.x and React Router v8 are also current, but v8 is ESM-only,
  requires Node 22+ and React 19.2.7+, and renames the package to `react-router`
  with breaking changes — worth adopting deliberately later, not as a drop-in here.
- **Vite 5.4.11** — pairs cleanly with React 18; Vite 7 is current but targets the
  React 19 / Node 22 stack above.

Both `requirements.txt` and `package.json` installed and built without dependency
conflicts in a clean environment as part of preparing this project.

---

## 6. Production deployment notes

This ships configured for local development (`DEBUG=True`, SQLite). Before deploying:

1. Set `DEBUG=False` and a strong random `SECRET_KEY` in `.env`.
2. Switch `DB_ENGINE=postgres` and fill in the DB credentials — `psycopg2-binary` is
   already in `requirements.txt`.
3. Set `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` to your real domains.
4. Run `python manage.py collectstatic` (WhiteNoise serves static files).
5. Serve with `gunicorn ems_backend.wsgi:application` behind a reverse proxy (Nginx,
   Caddy, etc.) terminating TLS — `SECURE_SSL_REDIRECT`/HSTS turn on automatically
   once `DEBUG=False`.
6. Build the frontend (`npm run build`) and serve the static `dist/` bundle from your
   proxy or a static host, pointed at the deployed API via `VITE_API_BASE_URL`.
