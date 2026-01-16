from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Try to select the new column to see if it exists
        print("Checking for 'overtime_hours' column...")
        db.session.execute(text("SELECT overtime_hours FROM attendance LIMIT 1"))
        print("Column 'overtime_hours' already exists.")
    except Exception as e:
        print(f"Column missing (Expected). Error: {e}")
        try:
            # SQLite syntax to add column
            print("Attempting to add 'overtime_hours' column...")
            db.session.execute(text("ALTER TABLE attendance ADD COLUMN overtime_hours FLOAT DEFAULT 0.0"))
            db.session.commit()
            print("Column 'overtime_hours' added successfully.")
        except Exception as migration_error:
            print(f"Failed to add column: {migration_error}")
