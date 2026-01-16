from app import create_app
from app.models import User
from flask_jwt_extended import create_access_token
import json

app = create_app()

with app.app_context():
    # Find John
    # We saw earlier his role name is 'HR Manager', verify username in roles_list output was 'John'
    user = User.query.filter(User.username.ilike('John%')).first()
    if not user:
        print("User 'John' not found! Trying to list all users to find ID.")
        for u in User.query.all():
            print(u.username)
        exit(1)
        
    print(f"Testing API for User: {user.username} (ID: {user.id})")
    
    # Create token
    # Identity in get_jwt_identity() is usually user_id (string or int).
    token = create_access_token(identity=str(user.id))
    
    # Hit endpoint
    client = app.test_client()
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    resp = client.get('/api/attendance', headers=headers)
    
    print(f"Status Code: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json
        print(f"Record Count: {len(data)}")
        if len(data) > 0:
            print("First Record Keys:", data[0].keys())
            # print("First Record Sample:", json.dumps(data[0], indent=2))
            sample = data[0]
            print(f"ID: {sample.get('id')}")
            print(f"Employee: {sample.get('employee')}")
            print(f"Overtime: {sample.get('overtime_hours')}")
    else:
        print("Error Response:", resp.data)
