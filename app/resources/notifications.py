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
        from app.models import User, Role
        
        data = request.get_json()
        
        title = data.get('title')
        message = data.get('message')
        ntype = data.get('type', 'info')
        recipient_type = data.get('recipientType', 'all')
        recipient_id = data.get('recipientId')

        if not title or not message:
            return {'error': 'title and message are required'}, 400

        # Determine target users
        target_users = []
        
        if recipient_type == 'all':
            # Send to all users
            target_users = User.query.all()
        elif recipient_type == 'role':
            # Send to users with specific role
            if not recipient_id:
                return {'error': 'recipientId required for role targeting'}, 400
            role = Role.query.filter_by(name=recipient_id.capitalize()).first()
            if not role:
                # Try common role names
                role_map = {'hr': 'HR Manager', 'employee': 'Employee', 'admin': 'Admin'}
                role_name = role_map.get(recipient_id.lower(), recipient_id)
                role = Role.query.filter_by(name=role_name).first()
            if role:
                target_users = User.query.filter_by(role_id=role.id).all()
        elif recipient_type == 'specific':
            # Send to specific user
            if not recipient_id:
                return {'error': 'recipientId required for specific targeting'}, 400
            # recipient_id might be employee_id, need to find user_id
            from app.models import Employee
            employee = Employee.query.get(recipient_id)
            if employee and employee.user_id:
                user = User.query.get(employee.user_id)
                if user:
                    target_users = [user]

        if not target_users:
            return {'error': 'No valid recipients found'}, 400

        # Create notifications for all target users
        created_count = 0
        for user in target_users:
            new_notification = Notification(
                user_id=user.id,
                title=title,
                message=message,
                type=ntype,
                is_read=False
            )
            db.session.add(new_notification)
            created_count += 1
        
        db.session.commit()
        
        return {'message': f'Notification sent to {created_count} user(s)'}, 201

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
