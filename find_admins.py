from app import create_app
from app.models import User, Role

app = create_app()

with app.app_context():
    admin_role = Role.query.filter(Role.name.ilike('%admin%')).first()
    if admin_role:
        print(f"Admin Role found: {admin_role.name}")
        admins = User.query.filter_by(role_id=admin_role.id).all()
        for u in admins:
            print(f"Admin User: {u.username} (ID: {u.id})")
    else:
        print("No Admin role found via query!")
        
    # Also check string roles if any (legacy?)
    all_users = User.query.all()
    for u in all_users:
        # Assuming role relationship is set, but just in case
        pass
