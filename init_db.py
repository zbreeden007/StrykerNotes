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
        
        # Ensure default todo list exists
        default_list = TodoList.query.filter_by(name="My Tasks").first()
        if not default_list:
            print("Creating default Todo list...")
            default_list = TodoList(name="My Tasks")
            db.session.add(default_list)
            db.session.commit()
            print("Default Todo list created.")

if __name__ == "__main__":
    db_path = os.path.join(os.getcwd(), 'productivity.db')
    print(f"Initializing database at: {db_path}")
    initialize_database()
    
    # Verify the table structures after initialization
    print("\nVerifying database structure:")
    app = create_app()
    with app.app_context():
        engine = db.engine
        inspector = db.inspect(engine)
        todo_columns = inspector.get_columns('todo')
        print("Todo table columns:")
        for column in todo_columns:
            print(f"- {column['name']} ({column['type']})")