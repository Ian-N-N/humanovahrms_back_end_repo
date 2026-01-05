from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Notification
from app import db
from app.schemas import NotificationSchema

notification_list_schema = NotificationSchema(many=True)
notification_schema = NotificationSchema()

class NotificationList(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
        return notification_list_schema.dump(notifications), 200

class NotificationResource(Resource):
    @jwt_required()
    def put(self, id):
        # Mark as read
        notification = Notification.query.get_or_404(id)
        notification.is_read = True
        db.session.commit()
        return notification_schema.dump(notification), 200

    @jwt_required()
    def delete(self, id):
        notification = Notification.query.get_or_404(id)
        db.session.delete(notification)
        db.session.commit()
        return {'message': 'Notification deleted'}, 200
