from flask import Flask
from app.config import Config
from app.extensions import db, migrate, jwt
from app.models import *  # noqa: F401,F403 (register models)
from app.routes import auth_bp, users_bp, departments_bp, upload_bp

def create_app(config_class: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Core foundation blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(departments_bp, url_prefix="/api/departments")
    app.register_blueprint(upload_bp, url_prefix="/api/upload")

    # Backend Dev B will later plug:
    # from app.routes.attendance import attendance_bp
    # from app.routes.leave import leave_bp
    # from app.routes.payroll import payroll_bp
    # app.register_blueprint(attendance_bp, url_prefix="/api/attendance")
    # app.register_blueprint(leave_bp, url_prefix="/api/leave")
    # app.register_blueprint(payroll_bp, url_prefix="/api/payroll")

    return app
