import os
import sqlite3

# Path to the database file
db_path = 'productivity.db'  # Adjust this path if needed

def inspect_db():
    """Inspect the database to see what tables exist"""
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"Found {len(tables)} tables in the database:")
        for table in tables:
            table_name = table[0]
            print(f"\n- Table: {table_name}")
            
            # Get table structure
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"  Columns:")
            for col in columns:
                print(f"    - {col[1]} ({col[2]})")
            
            # Get row count
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  Row count: {count}")
            except:
                print(f"  Row count: Unable to determine")
                
        conn.close()
    except Exception as e:
        print(f"Error inspecting database: {e}")

if __name__ == "__main__":
    print(f"Inspecting database at: {os.path.abspath(db_path)}")
    inspect_db()