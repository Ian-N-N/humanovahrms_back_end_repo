from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    users = User.query.all()
    print(f"{'Username':<20} | {'Role':<20}")
    print("-" * 45)
    for u in users:
        role_name = u.role.name if u.role else "None"
        print(f"{u.username:<20} | {role_name:<20}")
