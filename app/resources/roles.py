from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from app.models import Role
from app.schemas import RoleSchema
from app import db

role_schema = RoleSchema()
roles_schema = RoleSchema(many=True)

class RoleList(Resource):
    @jwt_required()
    def get(self):
        roles = Role.query.all()
        return roles_schema.dump(roles), 200

    @jwt_required()
    def put(self):
        data = request.get_json()
        
        # Expecting a list of roles with updated permissions, or a single role update
        # For simplicity in the matrix view, we might send a custom payload or the full list
        # Let's handle a single role update for now, or a list if needed.
        # Based on the requirement "Save Permissions", it's likely submitting the modified state.
        
        if isinstance(data, list):
            updated_roles = []
            for item in data:
                role_id = item.get('id')
                role = Role.query.get(role_id)
                if role:
                    role.permissions = item.get('permissions', {})
                    updated_roles.append(role)
            
            db.session.commit()
            return roles_schema.dump(updated_roles), 200
        
        else:
             # Single update
            role_id = data.get('id')
            role = Role.query.get(role_id)
            if not role:
                 return {'message': 'Role not found'}, 404
            
            role.permissions = data.get('permissions', {})
            db.session.commit()
            return role_schema.dump(role), 200
