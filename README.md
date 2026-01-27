# Humanova HRMS Backend

The robust, secure, and scalable backend service for the **Humanova Human Resource Management System**. Built with **Flask**, this API manages the entire employee lifecycle, from onboarding to payroll, secured by a granular **Role-Based Access Control (RBAC)** system.

## Key Features

*   **Advanced Security**: JWT-based authentication with custom middleware for role validation.
*   **Role-Based Access Control (RBAC)**: Distinct permissions for **Admin**, **HR Manager**, **Manager**, and **Employee**.
*   **Employee Lifecycle**: Comprehensive CRUD for employee profiles, supporting file uploads (Cloudinary) and automated onboarding emails (SendGrid/Brevo).
*   **Attendance Tracking**: Real-time clock-in/out logic with geolocation support and history logs.
*   **Automated Payroll**: Complex payroll engine calculating PAYE, NSSF, SHIF, and Housing Levy based on Kenyan tax laws.
*   **Leave Management**: Workflow-driven leave requests with multi-level approval steps.
*   **Analytics**: Real-time dashboard stats for HR insights.

---

## Architecture & RBAC

This project uses a layered architecture to separate concerns, specifically identifying three key layers: **Models**, **Resources (Controllers)**, and **Middleware**.

### Security Architecture (RBAC)
Security is enforced at the resource level using custom decorators defined in `app/middleware/auth.py`.

**Defined Roles:**
1.  **Admin**: Full system access. Can delete records, manage payroll, and configure system settings.
2.  **HR Manager**: Can manage employees, departments, leave requests, and run payroll. cannot delete audit logs or core system configs.
3.  **Manager**: Can view their department's data and approve leave requests for their subordinates.
4.  **Employee**: Restricted access. Can only view their own profile, payslips, and attendance history.

**Middleware Decorators:**
*   `@jwt_required()`: Verifies the presence of a valid JWT token.
*   `@admin_required`: Restricts access strictly to users with the 'Admin' role.
*   `@hr_required`: Allows access to 'Admin' and 'HR Manager'.
*   `@owner_or_hr_required`: Hybrid permission. Allows access if the user *is* the owner of the resource OR has HR privileges (e.g., viewing a specific payslip).

### Database Schema
The database (PostgreSQL/SQLite) is managed via **SQLAlchemy**. Key relationships include:
*   **User** <-> **Role** (One-to-Many): A user has one specific system role.
*   **User** <-> **Employee** (One-to-One): A login account is linked to a specific employee profile.
*   **Department** <-> **Employee** (One-to-Many): Employees belong to departments; Departments have a manager (Employee).
*   **Employee** <-> **Attendance/Leave/Payroll** (One-to-Many): Tracking historical records.

---

## Tech Stack

| Category | Technology | Purpose |
| :--- | :--- | :--- |
| **Framework** | Flask | Core Web Server & API Framework |
| **API** | Flask-RESTful | Resource-based API routing |
| **Database** | PostgreSQL / SQLite | Data persistence |
| **ORM** | SQLAlchemy | Database abstraction & modeling |
| **Auth** | Flask-JWT-Extended | Token-based authentication |
| **Serialization** | Marshmallow | Data validation & JSON formatting |
| **Migrations** | Flask-Migrate (Alembic) | Database schema versioning |
| **Email** | SendGrid / Brevo | Transactional emails (Onboarding, Leave) |
| **Storage** | Cloudinary | Cloud hosting for profile photos/docs |

---

## Setup & Installation

### Prerequisites
*   Python 3.8 or higher
*   Git
*   (Optional) PostgreSQL for production

### 1. Clone & Configure
```bash
git clone <repository-url>
cd humanovahrms_back_end_repo

# Create Virtual Environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt
```

### 2. Environment Variables (.env)
Create a `.env` file in the root directory. **CRITICAL**: The system requires these keys to function.

```env
# Flask Settings
SECRET_KEY=super_secure_secret
FLASK_ENV=development

# Database (Leave empty for local SQLite)
DATABASE_URL=postgresql://user:pass@localhost/hrms

# Authentication
JWT_SECRET_KEY=another_secure_secret

# Cloudinary (Media Uploads)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_key
CLOUDINARY_API_SECRET=your_secret

# Email Service (SMTP)
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

### 3. Database Initialization
```bash
# Initialize DB
flask db upgrade

# Seed Initial Data (Optional - creates default Admin & Roles)
python seed_employees.py
```

### 4. Run Server
```bash
python run.py
```
*   Server runs at: `http://localhost:5000`

---

## API Reference & Security

All API endpoints are prefixed with `/api`. Most require a `Bearer Token`.

### Authentication
| Method | Endpoint | Role Required | Description |
| :--- | :--- | :--- | :--- |
| POST | `/auth/login` | Public | Login and retrieve `access_token` |
| POST | `/auth/register` | Public | Register a new user account |
| GET | `/users` | Admin | List all system users |

### Employee Management
| Method | Endpoint | Role Required | Description |
| :--- | :--- | :--- | :--- |
| GET | `/employees` | HR, Admin | List all employees |
| POST | `/employees` | HR, Admin | Onboard new employee (triggers email) |
| GET | `/employees/<id>` | Owner, HR, Admin | View detailed profile |
| PUT | `/employees/<id>` | HR, Admin | Update employee details |
| DELETE | `/employees/<id>` | **Admin Only** | Hard delete employee record |

### Departments
| Method | Endpoint | Role Required | Description |
| :--- | :--- | :--- | :--- |
| GET | `/departments` | Authenticated | List all departments |
| POST | `/departments` | HR, Admin | Create new department |
| DELETE | `/departments/<id>` | **Admin Only** | Delete department |

### Attendance
| Method | Endpoint | Role Required | Description |
| :--- | :--- | :--- | :--- |
| POST | `/attendance/clock-in` | Authenticated | Clock in for the day |
| POST | `/attendance/clock-out` | Authenticated | Clock out |
| GET | `/attendance/history` | Owner | View personal attendance log |

### Payroll
| Method | Endpoint | Role Required | Description |
| :--- | :--- | :--- | :--- |
| POST | `/payroll` | HR, Admin | Run payroll for a specific cycle |
| GET | `/payroll/history` | Owner | View personal payslips |
| GET | `/payroll/reports` | HR, Admin | Generate financial reports |

---

## Testing
The project includes ad-hoc test scripts for quick validation.
*   `test_*.py` files are generally git-ignored.
*   **Run Standard Tests**: `pytest`

## License
Private and Confidential.
