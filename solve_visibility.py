from app import create_app, db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    if 'leave_requests' in inspector.get_table_names():
        columns = [c['name'] for c in inspector.get_columns('leave_requests')]
        print("COLUMNS_START")
        for c in columns:
            print(c)
        print("COLUMNS_END")
    else:
        print("TABLE_NOT_FOUND")
