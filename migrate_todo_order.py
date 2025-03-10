import os
import sqlite3
from app import create_app

# Path to the database file
app = create_app()
db_path = os.path.join(os.getcwd(), 'productivity.db')  # Adjust this path if needed

def inspect_and_migrate_todo_order():
    """First inspect the database then add order column to the todo table"""
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check what tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"Found {len(tables)} tables in the database:")
        for table in tables:
            table_name = table[0]
            print(f"- {table_name}")
        
        # Look for the todos table (could be 'todo', 'todos', 'Todo', etc.)
        todo_table_name = None
        for table in tables:
            if 'todo' in table[0].lower() and 'list' not in table[0].lower():
                todo_table_name = table[0]
                break
                
        if not todo_table_name:
            print("Could not find a todo table in the database. Please run the app first to initialize the database.")
            conn.close()
            return False
            
        print(f"Found todo table: {todo_table_name}")
        
        # Check if the column already exists
        cursor.execute(f"PRAGMA table_info({todo_table_name})")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        print(f"Existing columns: {', '.join(column_names)}")
        
        if "order" not in column_names:
            print(f"Adding 'order' column to the {todo_table_name} table...")
            cursor.execute(f"ALTER TABLE {todo_table_name} ADD COLUMN \"order\" INTEGER DEFAULT 0")
            
            # Initialize the order values based on existing IDs to maintain current order
            cursor.execute(f"SELECT id FROM {todo_table_name} ORDER BY id")
            todos = cursor.fetchall()
            
            for idx, todo_id in enumerate(todos):
                cursor.execute(f"UPDATE {todo_table_name} SET \"order\" = ? WHERE id = ?", (idx, todo_id[0]))
            
            conn.commit()
            print("Column added and order values initialized successfully!")
        else:
            print("Column 'order' already exists. Skipping...")
            
        conn.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print(f"Inspecting and migrating database at: {db_path}")
    if inspect_and_migrate_todo_order():
        print("Migration completed successfully!")
    else:
        print("Migration failed!")