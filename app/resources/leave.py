from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import LeaveRequest, Employee
from app import db
from app.schemas import LeaveRequestSchema
from app.middleware.auth import hr_required

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
            start_date=data['start_date'],
            end_date=data['end_date'],
            reason=data.get('reason')
        )
        db.session.add(leave)
        db.session.commit()
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
        leave.status = 'approved'
        leave.approved_by = get_jwt_identity()
        # leave.approval_date = datetime.utcnow() # Add import if needed
        db.session.commit()
        return leave_schema.dump(leave), 200

class LeaveReject(Resource):
    @jwt_required()
    @hr_required
    def put(self, id):
        leave = LeaveRequest.query.get_or_404(id)
        leave.status = 'rejected'
        leave.approved_by = get_jwt_identity()
        db.session.commit()
        return leave_schema.dump(leave), 200
