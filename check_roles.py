from app import create_app, db
from app.models import Role

app = create_app()

with app.app_context():
    roles = Role.query.all()
    print("Existing Roles:")
    for r in roles:
        print(f"- {r.name}")
