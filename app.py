from app import create_app
from app.models.db import db

app = create_app()

with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Database initialization notice: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
