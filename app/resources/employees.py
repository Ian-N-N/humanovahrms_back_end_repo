from flask import request, current_app
from flask_restful import Resource
from app.models import Employee, User, Role
from app import db
from app.schemas import EmployeeSchema
from app.middleware.auth import admin_required, hr_required
from flask_jwt_extended import jwt_required
from werkzeug.security import generate_password_hash
from app.utils.email_utils import send_onboarding_email

employee_schema = EmployeeSchema()
employees_schema = EmployeeSchema(many=True)

class EmployeeList(Resource):
    @jwt_required()
    @hr_required
    def get(self):
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        employees = Employee.query.paginate(page=page, per_page=per_page)
        
        return {
            'employees': employees_schema.dump(employees.items),
            'total': employees.total,
            'pages': employees.pages,
            'current_page': employees.page
        }, 200

    @jwt_required()
    @hr_required
    def post(self):
        # Log Content-Type for debugging
        current_app.logger.info(f"POST Employee - Content-Type: {request.content_type}")
        
        # Handle Multipart Form Data (File Uploads)
        if request.mimetype == 'multipart/form-data':
             data = request.form.to_dict()
             file_storage = request.files.get('image')
             current_app.logger.info(f"Multipart detected. Files: {list(request.files.keys())}. Form data keys: {list(data.keys())}")
        else:
             data = request.get_json() or {}
             file_storage = None
             current_app.logger.info("JSON request detected.")
        
        # --- TALENT ONBOARDING LOGIC (Create User Account) ---
        user_id = data.get('user_id')
        create_account = data.get('create_account') == 'true' or data.get('create_account') is True
        
        account_email = data.get('account_email') # Work Email
        personal_email = data.get('personal_email') # Email for notification
        account_password = data.get('account_password')
        account_role_name = data.get('account_role', 'Employee')

        if create_account and account_email and account_password:
            # Check if user already exists
            if User.query.filter_by(email=account_email).first():
                return {'message': f'Account with email {account_email} already exists'}, 400
            
            # Find Role
            role = Role.query.filter_by(name=account_role_name).first()
            if not role:
                role = Role.query.filter_by(name='Employee').first()

            # Create User
            new_user = User(
                email=account_email.lower().strip(),
                username=data.get('first_name') or 'User',
                password_hash=generate_password_hash(account_password),
                role_id=role.id if role else 1
            )
            db.session.add(new_user)
            db.session.flush() # Get user_id before commit
            user_id = new_user.id
            

        # Cast data types correctly
        from datetime import datetime
        hire_date_str = data.get('hire_date') or data.get('join_date') 
        hire_date = None
        if hire_date_str:
            try:
                # Handle YYYY-MM-DD
                hire_date = datetime.strptime(hire_date_str.split('T')[0], '%Y-%m-%d').date()
            except (ValueError, IndexError):
                pass

        try:
            basic_salary = float(data.get('basic_salary')) if data.get('basic_salary') else 0.0
        except ValueError:
            basic_salary = 0.0

        # Handle Image Upload
        profile_photo_url = data.get('profile_photo_url')
        if file_storage:
            from app.utils.cloudinary_utils import upload_image
            profile_photo_url = upload_image(file_storage)

        mapped_data = {
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'phone_number': data.get('phone_number') or data.get('phone'),
            'personal_email': personal_email or data.get('personal_email'),
            'profile_photo_url': profile_photo_url,
            'department_id': data.get('department_id'),
            'supervisor_id': data.get('supervisor_id'),
            'job_title': data.get('job_title'),
            'basic_salary': basic_salary,
            'hire_date': hire_date,
            'user_id': user_id
        }
        
        # Remove None values
        mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
        
        new_employee = Employee(**mapped_data)
        db.session.add(new_employee)
        db.session.flush()  # Get the employee ID
        
        # --- AUTO-GENERATE EMPLOYEE NUMBER ---
        dept_prefix = "GEN"  # Default if no department
        if new_employee.department_id:
            from app.models import Department
            dept = Department.query.get(new_employee.department_id)
            if dept and dept.name:
                # Create prefix from department name (first 2-3 chars uppercase)
                name = dept.name.strip().upper()
                if len(name) <= 3:
                    dept_prefix = name
                else:
                    # Use first 3 consonants or first 3 chars
                    consonants = ''.join([c for c in name if c not in 'AEIOU '])
                    if len(consonants) >= 3:
                        dept_prefix = consonants[:3]
                    else:
                        dept_prefix = name[:3]
        
        # Format: PREFIX-XXX (e.g., HR-001, ENG-042)
        new_employee.employee_number = f"{dept_prefix}-{str(new_employee.id).zfill(3)}"
        
        db.session.commit()

        # Send Notification AFTER commit so slow email doesn't block DB
        if create_account and account_email and account_password:
             try:
                 send_onboarding_email(
                    personal_email=personal_email or account_email,
                    work_email=account_email,
                    password=account_password,
                    name=f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
                )
             except Exception as e:
                 current_app.logger.error(f"Post-onboarding email failed: {str(e)}")

        return employee_schema.dump(new_employee), 201

class EmployeeResource(Resource):
    @jwt_required()
    def get(self, id):
        employee = Employee.query.get_or_404(id)
        return employee_schema.dump(employee), 200

    @jwt_required()
    @hr_required
    def put(self, id):
        try:
            employee = Employee.query.get_or_404(id)
            
            # Log for debugging
            current_app.logger.info(f"PUT Employee {id} - Content-Type: {request.content_type}")

            # Handle Multipart Form Data (File Uploads) or JSON
            if request.mimetype == 'multipart/form-data' or request.files:
                 data = request.form.to_dict()
                 file_storage = request.files.get('image')
                 current_app.logger.info(f"Multipart/Files detected. Files: {list(request.files.keys())}")
            else:
                 data = request.get_json(silent=True) or {}
                 file_storage = None
                 current_app.logger.info("JSON or other request detected.")

            # Explicit Mapping
            if 'first_name' in data:
                employee.first_name = data['first_name']
            if 'last_name' in data:
                employee.last_name = data['last_name']
            
            # Fallback for old 'name' field
            if 'name' in data and not ('first_name' in data or 'last_name' in data):
                parts = data['name'].strip().split(' ', 1)
                employee.first_name = parts[0]
                if len(parts) > 1:
                    employee.last_name = parts[1]
            
            if 'phone' in data:
                employee.phone_number = data['phone']
            elif 'phone_number' in data:
                employee.phone_number = data['phone_number']
                
            if 'personal_email' in data:
                employee.personal_email = data['personal_email']
                
            if 'status' in data:
                employee.status = data['status']
                
            if 'job_title' in data:
                employee.job_title = data['job_title']

            if 'basic_salary' in data:
                try:
                    employee.basic_salary = float(data['basic_salary'])
                except (ValueError, TypeError):
                    pass
            
            # Handle Image Upload for Update
            if file_storage:
                 from app.utils.cloudinary_utils import upload_image
                 new_url = upload_image(file_storage)
                 current_app.logger.info(f"Cloudinary upload result: {new_url}")
                 employee.profile_photo_url = new_url
            elif 'profile_photo_url' in data:
                 employee.profile_photo_url = data['profile_photo_url']

            # Handle Department (Lookup by name if string provided)
            if 'department' in data:
                 from app.models import Department
                 dept_name = data['department']
                 dept = Department.query.filter_by(name=dept_name).first()
                 if dept:
                     employee.department_id = dept.id
            elif 'department_id' in data:
                employee.department_id = data['department_id']

            # Pass through any other matching keys that are safe
            if 'hire_date' in data:
                employee.hire_date = data['hire_date']
            if 'leave_balance' in data:
                employee.leave_balance = data['leave_balance']

            # NOTE: Email and Role are on User model, not Employee. 
            if employee.user_id and ('email' in data or 'role' in data):
                from app.models import User, Role
                user = User.query.get(employee.user_id)
                if user:
                    if 'email' in data:
                        user.email = data['email']
                    if 'role' in data:
                        role_val = data['role']
                        role_obj = Role.query.filter_by(name=role_val).first()
                        if role_obj:
                            user.role_id = role_obj.id

            current_app.logger.info(f"Saving employee {id}. Final Photo URL: {employee.profile_photo_url}")
            db.session.commit()
            
            # Refresh to get updated fields after commit
            db.session.refresh(employee)
            return employee_schema.dump(employee), 200
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating employee {id}: {str(e)}")
            return {"error": str(e)}, 500

    @jwt_required()
    @hr_required
    def patch(self, id):
        """Handle status updates (activate/deactivate)"""
        employee = Employee.query.get_or_404(id)
        data = request.get_json()
        
        if 'status' in data:
            employee.status = data['status']
            db.session.commit()
            return employee_schema.dump(employee), 200
        
        return {'message': 'No valid fields to update'}, 400

    @jwt_required()
    @admin_required
    def delete(self, id):
        """Delete an employee (Admin only)"""
        employee = Employee.query.get_or_404(id)
        
        # Also delete associated user account if exists
        user_id = employee.user_id
        
        db.session.delete(employee)
        
        if user_id:
            from app.models import User
            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
        
        db.session.commit()
        return {'message': 'Employee deleted successfully'}, 200
