from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        # Try to select both nhif and shif to see which one fails
        result_nhif = db.session.execute(text("SELECT nhif FROM payroll LIMIT 1")).fetchone()
        print("SUCCESS: 'nhif' column exists.")
    except Exception as e:
        print(f"FAILURE: 'nhif' column check failed")

    try:
        result_shif = db.session.execute(text("SELECT shif FROM payroll LIMIT 1")).fetchone()
        print("SUCCESS: 'shif' column exists.")
    except Exception as e:
        print(f"FAILURE: 'shif' column check failed")
