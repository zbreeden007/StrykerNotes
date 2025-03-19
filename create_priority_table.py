from app import create_app
from models import db, TeamPriority

app = create_app()

with app.app_context():
    # Create just the TeamPriority table
    TeamPriority.__table__.create(db.engine, checkfirst=True)
    print("TeamPriority table created successfully!")