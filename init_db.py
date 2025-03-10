from app import create_app
from models import db, Note, Todo, TodoList, TeamMember, MemberTask, Link, UserPreference, MemberProject, MemberNote, MemberDevelopment
import os

def initialize_database():
    """Initialize the database with all models"""
    app = create_app()
    
    with app.app_context():
        print("Creating all database tables...")
        db.create_all()
        print("Database initialized successfully!")
        
        # Check if tables were created
        engine = db.engine
        inspector = db.inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\nCreated {len(tables)} tables:")
        for table in tables:
            print(f"- {table}")

if __name__ == "__main__":
    db_path = os.path.join(os.getcwd(), 'productivity.db')
    print(f"Initializing database at: {db_path}")
    initialize_database()
    
    # Verify the Link table structure after initialization
    print("\nVerifying Link table structure:")
    app = create_app()
    with app.app_context():
        engine = db.engine
        inspector = db.inspect(engine)
        columns = inspector.get_columns('link')
        for column in columns:
            print(f"- {column['name']} ({column['type']})")