# Meridian HR Employee Management System

A full-stack human resources and employee management application built with Django REST Framework and React. The system supports role-based authentication, employee records, attendance tracking, and leave management.

## Features

- JWT authentication with access and refresh tokens
- Admin, HR, and employee roles
- Employee and department management
- Attendance tracking
- Leave types and leave requests
- Dashboard views
- Search, filtering, ordering, and pagination through the API
- Employee profile photo support
- SQLite for local development
- PostgreSQL support for production

## Technology Stack

### Backend

- Python
- Django
- Django REST Framework
- Simple JWT
- SQLite or PostgreSQL
- Pillow
- WhiteNoise
- Gunicorn

### Frontend

- React 18
- React Router
- Axios
- Vite

## Project Structure

```text
ems/
├── backend/
│   ├── accounts/
│   ├── attendance/
│   ├── employees/
│   ├── leaves/
│   ├── ems_backend/
│   ├── manage.py
│   └── requirements.txt
└── frontend/
    ├── src/
    ├── public/
    ├── package.json
    └── vite.config.js
```

## Requirements

- Python 3.10 or newer
- Node.js 18 or newer
- npm

## Backend Setup

From the repository root:

```bash
cd ems/backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver
```

On macOS or Linux, activate the virtual environment with:

```bash
source venv/bin/activate
```

The backend runs at `http://127.0.0.1:8000`.

## Frontend Setup

Open a second terminal:

```bash
cd ems/frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173`.

## Demo Accounts

The `seed_demo_data` command creates these local development accounts:

| Role | Username | Password |
|---|---|---|
| Administrator | `admin` | `********` |
| HR Manager | `hr_manager` | `HrPass123!` |
| Employee | `jdoe` | `EmployeePass123!` |

These credentials are for development only and must be changed before production use.

## API Routes

```text
/api/auth/login/
/api/auth/refresh/
/api/auth/logout/
/api/accounts/
/api/employees/
/api/attendance/
/api/leaves/
```

The Django admin panel is available at `http://127.0.0.1:8000/admin/`.

## Environment Configuration

The backend reads configuration from environment variables using `python-decouple`. Create `ems/backend/.env` when custom settings are required:

```env
SECRET_KEY=replace-with-a-secure-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
DB_ENGINE=sqlite
TIME_ZONE=UTC
```

For PostgreSQL, set `DB_ENGINE=postgres` and provide `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`.

The frontend uses `http://127.0.0.1:8000/api` by default. To override it, create `ems/frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

## Useful Commands

Run backend checks and tests:

```bash
cd ems/backend
python manage.py check
python manage.py test
```

Build and lint the frontend:

```bash
cd ems/frontend
npm run lint
npm run build
```

Preview the production frontend build:

```bash
npm run preview
```

## Production Notes

Before deployment:

1. Set `DEBUG=False`.
2. Use a strong, private `SECRET_KEY`.
3. Configure PostgreSQL and trusted hosts.
4. Restrict `CORS_ALLOWED_ORIGINS` to the production frontend domain.
5. Run `python manage.py migrate`.
6. Run `python manage.py collectstatic`.
7. Serve Django with Gunicorn or another production WSGI server.
8. Serve the React production build with a web server such as Nginx.
9. Do not use the demo passwords in production.

## License

This project is intended for educational and internal use.
