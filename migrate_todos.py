import os
import sqlite3
from app import create_app

# Path to the database file
app = create_app()
db_path = os.path.join(os.getcwd(), 'productivity.db')  # Adjust this path if needed

def migrate_todos():
    """Migrate todos to the new single-list structure"""
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the 'list_id' column exists in the todo table
        cursor.execute("PRAGMA table_info(todo)")
        columns = cursor.fetchall()
        has_list_id = any(column[1] == 'list_id' for column in columns)
        
        if has_list_id:
            print("Migrating todos to new structure...")
            
            # First, ensure there's at least one todo_list for existing todos
            cursor.execute("SELECT COUNT(*) FROM todo_list")
            list_count = cursor.fetchone()[0]
            
            if list_count == 0:
                # Create a default list if none exists
                print("Creating default todo list...")
                cursor.execute("INSERT INTO todo_list (name, created_at) VALUES (?, datetime('now'))", ("My Tasks",))
                default_list_id = cursor.lastrowid
            else:
                # Get the ID of the first list
                cursor.execute("SELECT id FROM todo_list LIMIT 1")
                default_list_id = cursor.fetchone()[0]
            
            # Temporarily store all todos
            cursor.execute("SELECT id, content, created_at, completed, due_date, priority, list_id FROM todo")
            todos = cursor.fetchall()
            
            if todos:
                # Create a new todo table without list_id
                print("Restructuring todo table...")
                cursor.execute("CREATE TABLE todo_new (id INTEGER PRIMARY KEY, content TEXT NOT NULL, created_at DATETIME, completed BOOLEAN DEFAULT FALSE, due_date DATETIME, priority INTEGER DEFAULT 0)")
                
                # Insert all todos into the new table
                for todo in todos:
                    todo_id, content, created_at, completed, due_date, priority, _ = todo
                    cursor.execute(
                        "INSERT INTO todo_new (id, content, created_at, completed, due_date, priority) VALUES (?, ?, ?, ?, ?, ?)",
                        (todo_id, content, created_at, completed, due_date, priority)
                    )
                
                # Drop the old table and rename the new one
                cursor.execute("DROP TABLE todo")
                cursor.execute("ALTER TABLE todo_new RENAME TO todo")
                
                print(f"Migration completed. Moved {len(todos)} todos to the new structure.")
            else:
                print("No todos found to migrate.")
            
            conn.commit()
        else:
            print("The todo table is already using the new structure without list_id.")
            
        conn.close()
        return True
    except Exception as e:
        print(f"Error during migration: {e}")
        return False

if __name__ == "__main__":
    print(f"Migrating database at: {db_path}")
    if migrate_todos():
        print("Todo migration completed successfully!")
    else:
        print("Todo migration failed!")