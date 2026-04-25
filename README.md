<<<<<<< Updated upstream
=======
# Humanova HRMS Backend

Django REST API for the Humanova Human Resource Management System.

## Stack

| Category | Technology |
| :--- | :--- |
| Framework | Django |
| API | Django REST Framework |
| Auth | SimpleJWT |
| Database | PostgreSQL or another SQL database configured by `DATABASE_URL` |
| Storage | Cloudinary |
| Email | Brevo / SendGrid-compatible dependencies |

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `.env` in the repository root:

```env
SECRET_KEY=change-me
DEBUG=false
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://user:password@localhost:5432/humanova_hrms
CORS_ALLOWED_ORIGINS=http://localhost:5173

CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
MAIL_DEFAULT_SENDER=
BREVO_API_KEY=
```

Create the database yourself, then run:

```bash
python manage.py makemigrations hrms
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The app requires `DATABASE_URL`; it does not create or use a local fallback database.

## API

All endpoints are prefixed with `/api`.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| POST | `/api/auth/login` | Login and receive JWT tokens |
| POST | `/api/auth/refresh` | Refresh access token |
| GET | `/api/users` | Admin user list |
| GET/POST | `/api/employees` | Employee list/create |
| GET/PUT/PATCH/DELETE | `/api/employees/<id>` | Employee detail |
| GET/POST | `/api/departments` | Department list/create |
| POST | `/api/attendance/clock-in` | Clock in |
| POST | `/api/attendance/clock-out` | Clock out |
| GET | `/api/attendance/history` | Personal attendance history |
| GET/POST | `/api/leave` | Leave list/create |
| PUT | `/api/leave/<id>/approve` | Approve leave |
| PUT | `/api/leave/<id>/reject` | Reject leave |
| GET/POST | `/api/payroll/cycles` | Payroll cycle list/create |
| GET/POST | `/api/payroll` | Payroll list/run |
| GET | `/api/payroll/history` | Personal payroll history |
| GET | `/api/notifications` | User notifications |
| GET/PUT | `/api/settings` | System settings |

## Development Checks

```bash
python manage.py check
python -m compileall config hrms manage.py
```
>>>>>>> Stashed changes
