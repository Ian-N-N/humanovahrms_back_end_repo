from app import create_app, db
from app.models import Payroll, PayrollCycle

def fix_payment_dates():
    app = create_app()
    with app.app_context():
        payrolls = Payroll.query.all()
        
        for p in payrolls:
            cycle = PayrollCycle.query.get(p.cycle_id)
            if cycle and p.payment_date != cycle.end_date:
                print(f"Updating Payroll {p.id}: {p.payment_date} -> {cycle.end_date}")
                p.payment_date = cycle.end_date
        
        db.session.commit()
        print("Done! All payment dates updated.")

if __name__ == "__main__":
    fix_payment_dates()
