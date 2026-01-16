from app import db
from app.models.activity_log import ActivityLog

def log_activity(action, details, user_id=None):
    """
    Logs a system activity to the database.
    
    Args:
        action (str): Short description of the action (e.g. 'Clock In', 'User Created')
        details (str): Detailed description
        user_id (int, optional): ID of the user performing the action
    """
    try:
        log = ActivityLog(
            action=action,
            details=details,
            user_id=user_id
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Failed to log activity: {str(e)}")
        db.session.rollback() # Don't crash the main request if logging fails
