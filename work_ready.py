from app import create_app, db
from app.models import Employee, Payroll
from app.schemas import PayrollSchema
import traceback

app = create_app()
payroll_list_schema = PayrollSchema(many=True)

with app.app_context():
    from flask import current_app
    print(f"DEBUG: Database URI: {current_app.config.get('SQLALCHEMY_DATABASE_URI')}")
    print("--- Diagnostics for Payroll History ---")
    employees = Employee.query.all()
    if not employees:
        print("No employees found.")
    for emp in employees:
        try:
            payrolls = Payroll.query.filter_by(employee_id=emp.id).all()
            if payrolls:
                try:
                    data = payroll_list_schema.dump(payrolls)
                    print(f"SUCCESS: Employee {emp.id} serialized {len(data)} records.")
                except Exception as e:
                    print(f"FAILURE: Employee {emp.id} serialization failed: {str(e)}")
                    traceback.print_exc()
        except Exception as e:
            print(f"DB_ERROR: Employee {emp.id}: {str(e)}")

    print("\n--- Route Verification ---")
    for rule in app.url_map.iter_rules():
        if 'history' in rule.rule:
            print(f"Route: {rule.rule} -> Endpoint: {rule.endpoint}")
