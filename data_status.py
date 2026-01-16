from app import create_app, db
from app.models import Attendance, User

app = create_app()

with app.app_context():
    count = Attendance.query.count()
    print(f"Total Attendance Records in DB: {count}")
    
    if count > 0:
        # Show last 5 records
        recs = Attendance.query.order_by(Attendance.id.desc()).limit(5).all()
        for r in recs:
            print(f"ID: {r.id} | Date: {r.date} | EmpID: {r.employee_id} | In: {r.clock_in} | OT: {getattr(r, 'overtime_hours', 'N/A')}")
