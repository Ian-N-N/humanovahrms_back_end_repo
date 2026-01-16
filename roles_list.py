from app import create_app
from app.models import User, Role

app = create_app()

with app.app_context():
    # Find role with name like 'HR%'
    hr_roles = Role.query.filter(Role.name.ilike('%HR%')).all()
    print(f"Found {len(hr_roles)} HR-like roles:")
    for r in hr_roles:
        print(f" - ID: {r.id}, Name: '{r.name}'")
        users = User.query.filter_by(role_id=r.id).all()
        for u in users:
             print(f"   -> User: '{u.username}', Email: '{u.email}'")

    # Also list all roles to be safe
    print("\nALL ROLES:")
    for r in Role.query.all():
        print(f"'{r.name}'")
