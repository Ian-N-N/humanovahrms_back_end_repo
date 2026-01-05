from app import create_app, db
from app.models import *  # Import models to ensure they are registered with SQLAlchemy

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
