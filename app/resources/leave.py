from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import LeaveRequest, Employee, User, Role, Notification
from app import db
from app.schemas import LeaveRequestSchema
from app.middleware.auth import hr_required
from app.utils.email_utils import send_leave_status_email, send_new_leave_request_notification
from datetime import datetime

leave_schema = LeaveRequestSchema()
leave_list_schema = LeaveRequestSchema(many=True)

class LeaveList(Resource):
    @jwt_required()
    def get(self):
        leaves = LeaveRequest.query.all()
        return leave_list_schema.dump(leaves), 200

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        employee = Employee.query.filter_by(user_id=user_id).first()
        if not employee:
             return {'message': 'Employee record not found'}, 404
             
        data = request.get_json()
        leave = LeaveRequest(
            employee_id=employee.id,
            leave_type=data['leave_type'],
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
            reason=data.get('reason')
        )
        db.session.add(leave)
        
        # Notify Admins and HR Managers in-app
        admin_hr_roles = Role.query.filter(Role.name.in_(['Admin', 'HR Manager'])).all()
        role_ids = [r.id for r in admin_hr_roles]
        admin_hr_users = User.query.filter(User.role_id.in_(role_ids)).all()
        
        for user in admin_hr_users:
            notif = Notification(
                user_id=user.id,
                title="New Leave Request",
                message=f"{employee.first_name} {employee.last_name} has submitted a {leave.leave_type} request.",
                type="info"
            )
            db.session.add(notif)
            
        db.session.commit()
        
        # Broadcast email to Admins/HR
        try:
            send_new_leave_request_notification(
                admin_hr_users,
                f"{employee.first_name} {employee.last_name}",
                leave.leave_type,
                leave.start_date,
                leave.end_date
            )
        except Exception as e:
            print(f"DEBUG: Failed to broadcast admin emails: {str(e)}")
            
        return leave_schema.dump(leave), 201

class LeaveResource(Resource):
    @jwt_required()
    def get(self, id):
        leave = LeaveRequest.query.get_or_404(id)
        return leave_schema.dump(leave), 200

class LeaveApprove(Resource):
    @jwt_required()
    @hr_required
    def put(self, id):
        leave = LeaveRequest.query.get_or_404(id)
        
        # Determine duration
        days_count = (leave.end_date - leave.start_date).days + 1
        
        employee = Employee.query.get(leave.leave_employee.id if leave.leave_employee else leave.employee_id)
        if employee and days_count > 0:
             # Subtract from balance
             current_balance = employee.leave_balance if employee.leave_balance is not None else 0
             employee.leave_balance = current_balance - days_count

        leave.status = 'approved'
        leave.approved_by = get_jwt_identity()
        leave.approval_date = datetime.utcnow()
        
        # Notify Employee in-app
        notif = Notification(
            user_id=employee.user_id,
            title="Leave Approved",
            message=f"Your leave request for {leave.start_date} to {leave.end_date} has been approved.",
            type="success"
        )
        db.session.add(notif)
        
        db.session.commit()
        
        # Target Email (Personal preferred)
        target_email = employee.personal_email or (employee.user.email if employee.user else None)
        
        # Send Email
        if target_email:
            send_leave_status_email(
                target_email,
                f"{employee.first_name}",
                "approved",
                leave.start_date,
                leave.end_date
            )
            
        return leave_schema.dump(leave), 200

class LeaveReject(Resource):
    @jwt_required()
    @hr_required
    def put(self, id):
        leave = LeaveRequest.query.get_or_404(id)
        leave.status = 'rejected'
        leave.approved_by = get_jwt_identity()
        leave.approval_date = datetime.utcnow()
        
        employee = Employee.query.get(leave.leave_employee.id if leave.leave_employee else leave.employee_id)
        
        # Notify Employee in-app
        notif = Notification(
            user_id=employee.user_id,
            title="Leave Rejected",
            message=f"Your leave request for {leave.start_date} to {leave.end_date} has been rejected.",
            type="warning"
        )
        db.session.add(notif)
        
        db.session.commit()
        
        # Target Email (Personal preferred)
        target_email = employee.personal_email or (employee.user.email if employee.user else None)
        
        # Send Email
        if target_email:
            send_leave_status_email(
                target_email,
                f"{employee.first_name}",
                "rejected",
                leave.start_date,
                leave.end_date
            )
            
        return leave_schema.dump(leave), 200

class LeaveHistory(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        employee = Employee.query.filter_by(user_id=user_id).first()
        if not employee:
            return {'message': 'Employee record not found'}, 404
            
        leaves = LeaveRequest.query.filter_by(employee_id=employee.id).order_by(LeaveRequest.created_at.desc()).all()
        return leave_list_schema.dump(leaves), 200
