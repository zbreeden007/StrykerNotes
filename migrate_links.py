import os
import sqlite3
from app import create_app

# Path to the database file
app = create_app()
db_path = os.path.join(os.getcwd(), 'productivity.db')  # Adjust this path if needed

def add_favorite_column():
    """Add is_favorite column to the link table"""
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(link)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if "is_favorite" not in column_names:
            print("Adding 'is_favorite' column to the link table...")
            cursor.execute("ALTER TABLE link ADD COLUMN is_favorite BOOLEAN DEFAULT FALSE")
            conn.commit()
            print("Column added successfully!")
        else:
            print("Column 'is_favorite' already exists. Skipping...")
            
        conn.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print(f"Migrating database at: {db_path}")
    if add_favorite_column():
        print("Migration completed successfully!")
    else:
        print("Migration failed!")