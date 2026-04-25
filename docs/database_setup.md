# Database Setup

This backend is Django-only and expects an external SQL database.

## Required Environment Variable

Set `DATABASE_URL` before running any Django command:

```env
DATABASE_URL=postgresql://user:password@host:5432/humanova_hrms
```

The application intentionally does not fall back to a local file database. Create the database first, then run:

```bash
python manage.py makemigrations hrms
python manage.py migrate
python manage.py createsuperuser
```

Use PostgreSQL for production.
