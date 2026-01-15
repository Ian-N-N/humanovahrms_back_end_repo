from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Notification
from app import db
from app.middleware.auth import hr_required
from app.schemas import NotificationSchema

notification_list_schema = NotificationSchema(many=True)
notification_schema = NotificationSchema()

class NotificationList(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
        return notification_list_schema.dump(notifications), 200

    @jwt_required()
    @hr_required
    def post(self):
        """Allow HR/Admin to send notifications to employees"""
        from flask import request
        data = request.get_json()
        
        target_user_id = data.get('user_id')
        msg = data.get('message')
        ntype = data.get('type', 'system')

        if not target_user_id or not msg:
            return {'error': 'user_id and message are required'}, 400

        new_notification = Notification(
            user_id=target_user_id,
            type=ntype,
            message=msg,
            is_read=False
        )
        
        db.session.add(new_notification)
        db.session.commit()
        
        return notification_schema.dump(new_notification), 201

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
