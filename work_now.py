from app import create_app, db
from app.models import Employee, Payroll
from app.schemas import PayrollSchema
import traceback

app = create_app()
payroll_list_schema = PayrollSchema(many=True)

with app.app_context():
    print("--- Diagnostics for Payroll History ---")
    employees = Employee.query.all()
    for emp in employees:
        print(f"\nChecking Employee ID {emp.id} ({emp.first_name} {emp.last_name})...")
        try:
            payrolls = Payroll.query.filter_by(employee_id=emp.id).all()
            print(f"  Found {len(payrolls)} payroll records.")
            if payrolls:
                # Attempt to serialize
                try:
                    data = payroll_list_schema.dump(payrolls)
                    print(f"  Successfully serialized {len(data)} records.")
                except Exception as e:
                    print(f"  FAILED to serialize: {str(e)}")
                    # Traceback usually goes to stderr, let's capture it manually if needed but print_exc works
                    traceback.print_exc()
        except Exception as e:
            print(f"  Database error: {str(e)}")

    print("\n--- Route Verification ---")
    for rule in app.url_map.iter_rules():
        if 'history' in rule.rule:
            print(f"Route: {rule.rule} -> Endpoint: {rule.endpoint}")
