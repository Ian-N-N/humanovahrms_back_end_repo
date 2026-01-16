from app import create_app, db
from app.models.activity_log import ActivityLog

app = create_app()

with app.app_context():
    # Check if table exists
    engine = db.engine
    from sqlalchemy import inspect
    inspector = inspect(engine)
    if 'activity_logs' not in inspector.get_table_names():
        print("Creating activity_logs table...")
        ActivityLog.__table__.create(engine)
        print("Table created successfully!")
    else:
        print("activity_logs table already exists.")
