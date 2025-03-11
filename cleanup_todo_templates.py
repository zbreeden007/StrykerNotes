import os
import shutil

def cleanup_todo_templates():
    """Remove todo-specific template files and clean up"""
    
    print("Starting cleanup of todo templates...")
    
    # Files to delete
    files_to_delete = [
        'todos.html',
        'view_list.html',
        'new_list.html'
    ]
    
    # Try to delete files from potential locations
    potential_locations = [
        '',  # Current directory
        'templates/',
        'templates/todos/'
    ]
    
    deleted_count = 0
    
    for location in potential_locations:
        for file in files_to_delete:
            file_path = os.path.join(location, file)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"✓ Deleted {file_path}")
                    deleted_count += 1
                except Exception as e:
                    print(f"× Error deleting {file_path}: {str(e)}")
    
    # Also try to delete the todos directory if it exists
    todos_dir = 'templates/todos'
    if os.path.exists(todos_dir) and os.path.isdir(todos_dir):
        try:
            if len(os.listdir(todos_dir)) == 0:  # Only if empty
                shutil.rmtree(todos_dir)
                print(f"✓ Deleted empty directory {todos_dir}")
            else:
                print(f"× Directory {todos_dir} is not empty, skipping")
        except Exception as e:
            print(f"× Error deleting directory {todos_dir}: {str(e)}")
    
    print(f"Cleanup complete. Deleted {deleted_count} files.")

if __name__ == "__main__":
    cleanup_todo_templates()