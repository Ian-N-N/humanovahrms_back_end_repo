from flask import Flask, jsonify
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from .config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
ma = Marshmallow()
cors = CORS()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)
    cors.init_app(app)

    api = Api(app)

    # Global Error Handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'message': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'message': 'Internal server error'}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        return jsonify({'message': str(e)}), 500

    # Register Resources
    from app.resources.auth import Register, Login
    from app.resources.employees import EmployeeList, EmployeeResource
    from app.resources.departments import DepartmentList, DepartmentResource
    from app.resources.attendance import AttendanceList, ClockIn, ClockOut
    from app.resources.leave import LeaveList, LeaveResource, LeaveApprove, LeaveReject
    from app.resources.payroll import PayrollList, PayrollResource
    from app.resources.analytics import DashboardStats
    from app.resources.notifications import NotificationList, NotificationResource

    api.add_resource(Register, '/api/auth/register')
    api.add_resource(Login, '/api/auth/login')
    
    api.add_resource(EmployeeList, '/api/employees')
    api.add_resource(EmployeeResource, '/api/employees/<int:id>')
    
    api.add_resource(DepartmentList, '/api/departments')
    api.add_resource(DepartmentResource, '/api/departments/<int:id>')
    
    api.add_resource(AttendanceList, '/api/attendance')
    api.add_resource(ClockIn, '/api/attendance/clock-in')
    api.add_resource(ClockOut, '/api/attendance/clock-out')
    
    api.add_resource(LeaveList, '/api/leave')
    api.add_resource(LeaveResource, '/api/leave/<int:id>')
    api.add_resource(LeaveApprove, '/api/leave/<int:id>/approve')
    api.add_resource(LeaveReject, '/api/leave/<int:id>/reject')
    
    api.add_resource(PayrollList, '/api/payroll')
    api.add_resource(PayrollResource, '/api/payroll/<int:id>')
    
    api.add_resource(DashboardStats, '/api/analytics/dashboard')
    
    api.add_resource(NotificationList, '/api/notifications')
    api.add_resource(NotificationResource, '/api/notifications/<int:id>')

    return app
