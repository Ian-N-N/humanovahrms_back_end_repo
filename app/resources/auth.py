from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Role
from app import db
from app.schemas import UserSchema

user_schema = UserSchema()

class Register(Resource):
    def post(self):
        data = request.get_json()
        if User.query.filter_by(email=data['email']).first():
            return {'message': 'User already exists'}, 400
        
        # Default role assignment logic (simplistic)
        role = Role.query.filter_by(name='Employee').first()
        if not role:
            # Create default roles if not exist (quick fix for dev)
            role = Role(name='Employee', permissions={})
            db.session.add(role)
            db.session.commit()

        new_user = User(
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            role_id=role.id
        )
        db.session.add(new_user)
        db.session.commit()

        return {'message': 'User created successfully'}, 201

class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()

        if user and check_password_hash(user.password_hash, data['password']):
            access_token = create_access_token(identity=user.id, additional_claims={'role': user.role.name})
            refresh_token = create_refresh_token(identity=user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user_schema.dump(user)
            }, 200
        return {'message': 'Invalid credentials'}, 401
