from app import create_app, db
from app.models import Employee

def fix():
    app = create_app()
    with app.app_context():
        # Austine is likely ID 2 based on previous output
        emp = Employee.query.filter(Employee.first_name.ilike('Austine%')).first()
        if emp:
            print(f"Updating {emp.first_name} from {emp.basic_salary} to 50000.00")
            emp.basic_salary = 50000.00
            db.session.commit()
            print("Done.")
        else:
            print("Austine not found.")

if __name__ == "__main__":
    fix()
