from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from app.models import SystemSetting
from app import db

class SettingsResource(Resource):
    @jwt_required()
    def get(self):
        settings = SystemSetting.query.all()
        # Return as a simple dictionary: { 'company_name': 'ecoHRMS', 'shift_start': '09:00' }
        return {s.key: s.value for s in settings}, 200

    @jwt_required()
    def put(self):
        data = request.get_json()
        
        updated_settings = []
        for key, value in data.items():
            setting = SystemSetting.query.filter_by(key=key).first()
            if setting:
                setting.value = str(value) # Ensure string storage
            else:
                # Create if doesn't exist (auto-provisioning settings)
                setting = SystemSetting(key=key, value=str(value))
                db.session.add(setting)
            updated_settings.append(key)
        
        db.session.commit()
        return {'message': 'Settings updated successfully', 'updated': updated_settings}, 200
