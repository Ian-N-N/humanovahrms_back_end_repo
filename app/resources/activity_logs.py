from flask_restful import Resource
from flask_jwt_extended import jwt_required
from app.models.activity_log import ActivityLog
from app.schemas import ActivityLogSchema
from app.middleware.auth import admin_required

activity_log_schema = ActivityLogSchema(many=True)

class ActivityLogList(Resource):
    @jwt_required()
    @admin_required
    def get(self):
        # Fetch last 50 logs, ordered by newest first
        logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(50).all()
        return activity_log_schema.dump(logs), 200
