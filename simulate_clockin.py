from app import create_app, db
from app.models import Employee, Attendance, User
from datetime import datetime, date, timedelta
import traceback

app = create_app()

with app.app_context():
    try:
        print("Starting Clock-In Debug...")
        
        # 1. Fetch User (John)
        user = User.query.filter(User.username.ilike('John%')).first()
        if not user:
            print("User John not found")
            exit()
            
        print(f"User found: {user.username} (ID: {user.id})")
        
        # 2. Fetch Employee
        employee = Employee.query.filter_by(user_id=user.id).first()
        if not employee:
            print("Employee record not found for user.")
        else:
            print(f"Employee found: {employee.name} (ID: {employee.id})")

        # 3. Logic Simulation
        print("Fetching Settings...")
        # Inline import as per Resource
        from app.models.setting import SystemSetting
        
        setting = SystemSetting.query.filter_by(key='shift_start_time').first()
        start_time_str = setting.value if setting else "09:00"
        print(f"Shift Start Time: {start_time_str}")
        
    except Exception as e:
        print("\nCRASH DETECTED:")
        print(e)
        traceback.print_exc()
