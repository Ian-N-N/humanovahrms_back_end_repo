from app import create_app, db
from app.models import Payroll, PayrollCycle

def cleanup_duplicate_payrolls():
    app = create_app()
    with app.app_context():
        # Find the March cycle
        march_cycle = PayrollCycle.query.filter_by(name='March').first()
        
        if not march_cycle:
            print("March cycle not found.")
            return
        
        print(f"Found March cycle (ID: {march_cycle.id})")
        
        # Get all March payrolls
        march_payrolls = Payroll.query.filter_by(cycle_id=march_cycle.id).all()
        
        if not march_payrolls:
            print("No March payroll records found.")
            return
        
        print(f"\nFound {len(march_payrolls)} March payroll records:")
        for p in march_payrolls:
            print(f"  - Payroll ID {p.id}: Employee {p.employee_id}, Gross: {p.gross_salary}")
        
        confirm = input("\nDo you want to DELETE all these March payroll records? (yes/no): ")
        
        if confirm.lower() == 'yes':
            for p in march_payrolls:
                db.session.delete(p)
            db.session.commit()
            print(f"\n✅ Successfully deleted {len(march_payrolls)} March payroll records!")
        else:
            print("\n❌ Deletion cancelled.")

if __name__ == "__main__":
    cleanup_duplicate_payrolls()
