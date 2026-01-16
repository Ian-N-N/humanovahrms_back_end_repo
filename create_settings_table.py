from app import create_app, db
from app.models.setting import SystemSetting

app = create_app()

with app.app_context():
    # Create the system_settings table
    db.create_all()
    print("All tables created/ensured.")
    
    # Check if default settings exist, if not, add them
    existing = SystemSetting.query.filter_by(key='shift_start_time').first()
    if not existing:
        setting = SystemSetting(key='shift_start_time', value='09:00', description='Standard shift start time')
        db.session.add(setting)
        print("Added shift_start_time setting")
    
    existing2 = SystemSetting.query.filter_by(key='shift_end_time').first()
    if not existing2:
        setting2 = SystemSetting(key='shift_end_time', value='17:00', description='Standard shift end time')
        db.session.add(setting2)
        print("Added shift_end_time setting")
        
    db.session.commit()
    print("Done. Settings table is ready.")
