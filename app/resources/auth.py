from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Role
from app import db
from app.schemas import UserSchema

user_schema = UserSchema()
users_schema = UserSchema(many=True)

class UserList(Resource):
    @jwt_required()
    def get(self):
        users = User.query.all()
        return users_schema.dump(users), 200

class Register(Resource):
    def post(self):
        data = request.get_json()
        
        # Validation
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        
        import re
        # Email regex
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return {'message': 'Invalid email format'}, 400
            
        # Password complexity
        if len(password) < 8:
            return {'message': 'Password must be at least 8 characters long'}, 400
        if not re.search(r'[A-Z]', password):
            return {'message': 'Password must contain at least one uppercase letter'}, 400
        if not re.search(r'[a-z]', password):
            return {'message': 'Password must contain at least one lowercase letter'}, 400
        if not re.search(r'[0-9]', password):
            return {'message': 'Password must contain at least one number'}, 400
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return {'message': 'Password must contain at least one special character'}, 400

        if User.query.filter_by(email=email).first():
            return {'message': 'User already exists'}, 400
        
        # New Workflow: Public registration is EXCLUSIVELY for Organization Admins
        role_name = 'Admin'

        role = Role.query.filter_by(name=role_name).first()
        if not role:
            # Create role if it doesn't exist
            role = Role(name=role_name, permissions={})
            db.session.add(role)
            db.session.commit()

        new_user = User(
            email=email,
            # Map 'username' from request, fallback to 'name'
            username=data.get('username') or data.get('name', 'Admin'), 
            password_hash=generate_password_hash(password),
            role_id=role.id
        )
        db.session.add(new_user)
        db.session.commit()

        return {'message': 'Admin account created successfully'}, 201

class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, data['password']):
            access_token = create_access_token(identity=str(user.id), additional_claims={'role': user.role.name})
            refresh_token = create_refresh_token(identity=str(user.id))
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user_schema.dump(user)
            }, 200
        return {'message': 'Invalid credentials'}, 401
