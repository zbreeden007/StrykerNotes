from app import create_app
from models import db

def add_priority_column():
    """Add priority column to member_project table"""
    app = create_app()
    
    with app.app_context():
        # Execute the raw SQL to add the column
        db.session.execute('ALTER TABLE member_project ADD COLUMN priority INTEGER DEFAULT 0')
        db.session.commit()
        
        print("Successfully added priority column to member_project table")

if __name__ == "__main__":
    add_priority_column()