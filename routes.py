from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort, send_from_directory
from datetime import datetime
import os
import markdown
from werkzeug.utils import secure_filename
from models import db, Note, Todo, TodoList, TeamMember, MemberTask, Link, UserPreference, MemberProject, MemberNote, MemberDevelopment, TeamPriority, File, AdHoc
from forms import NoteForm, TodoForm, TeamMemberForm, MemberTaskForm, LinkForm, UserPreferenceForm, MemberProjectForm, MemberNoteForm, MemberDevelopmentForm, FileForm
from forms import ProjectForm, TaskForm, DevelopmentForm, TeamPriorityForm, AdHocForm  # Add AdHocForm here
from PIL import Image
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.fields import DateField

# Create blueprints for different sections of the app
main = Blueprint('main', __name__)
notes = Blueprint('notes', __name__, url_prefix='/notes')
team = Blueprint('team', __name__, url_prefix='/team')
links = Blueprint('links', __name__, url_prefix='/links')
settings = Blueprint('settings', __name__, url_prefix='/settings')
todos = Blueprint('todos', __name__, url_prefix='/todos')  # Keep for redirects
files = Blueprint('files', __name__, url_prefix='/files')  # New blueprint for files
adhocs = Blueprint('adhocs', __name__, url_prefix='/adhocs')

# This should replace the existing inject_preferences function in routes.py
@main.app_context_processor
def inject_preferences():
    try:
        preferences = UserPreference.query.first()
        if not preferences:
            # Create a default preferences object using Stryker's brand values
            preferences = UserPreference(
                theme='light',  # White background, light theme as dominant
                font_family='Cambria, serif',  # Use Cambria for body copy
                font_size='16px',  # A slightly larger default for readability
                accent_color='#BF8A36'  # Stryker gold accent
            )
            db.session.add(preferences)
            try:
                db.session.commit()
            except Exception as e:
                print(f"Error saving preferences: {e}")
                db.session.rollback()

        # Ensure all required attributes exist
        if not hasattr(preferences, 'font_family') or not preferences.font_family:
            preferences.font_family = 'Cambria, serif'
        if not hasattr(preferences, 'font_size') or not preferences.font_size:
            preferences.font_size = '16px'
        if not hasattr(preferences, 'theme') or not preferences.theme:
            preferences.theme = 'light'
        if not hasattr(preferences, 'accent_color') or not preferences.accent_color:
            preferences.accent_color = '#BF8A36'
            
        return dict(preferences=preferences)
    except Exception as e:
        print(f"Error in context processor: {e}")
        # Return default preferences if anything goes wrong
        class DefaultPreferences:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        default_preferences = {
            'theme': 'light',
            'font_family': 'Cambria, serif',
            'font_size': '16px',
            'accent_color': '#BF8A36'
        }
        return dict(preferences=DefaultPreferences(**default_preferences))


# Function to save profile pictures
def save_profile_picture(form_picture):
    # Generate a secure filename
    filename = secure_filename(form_picture.filename)
    # Create a unique filename to avoid overwriting
    unique_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
    # Set the path
    picture_path = os.path.join('static', 'uploads', 'profile_pictures', unique_filename)
    # Ensure directory exists
    os.makedirs(os.path.dirname(picture_path), exist_ok=True)
    
    # Save the original file first
    form_picture.save(picture_path)
    
    try:
        # Open the image
        image = Image.open(picture_path)
        
        # Define a max size for profile pictures
        max_size = (400, 400)
        
        # Resize if larger than max size while preserving aspect ratio
        image.thumbnail(max_size)
        
        # Save the resized image (overwriting the original)
        image.save(picture_path)
    except Exception as e:
        # Log the error but continue with the original image
        print(f"Error processing image: {e}")
    
    return picture_path

# Function to save uploaded files
def save_uploaded_file(form_file):
    # Generate a secure filename
    filename = secure_filename(form_file.filename)
    # Create a unique filename to avoid overwriting
    unique_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
    # Set the path
    file_path = os.path.join('static', 'uploads', 'files', unique_filename)
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Save the file
    form_file.save(file_path)
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Determine file type based on extension
    _, ext = os.path.splitext(filename)
    ext = ext.lower().lstrip('.')
    
    # Map extensions to file types
    file_type_map = {
        'pdf': 'PDF',
        'doc': 'Word',
        'docx': 'Word',
        'xls': 'Excel',
        'xlsx': 'Excel',
        'ppt': 'PowerPoint',
        'pptx': 'PowerPoint',
        'txt': 'Text',
        'csv': 'CSV',
        'jpg': 'Image',
        'jpeg': 'Image',
        'png': 'Image',
        'gif': 'Image'
    }
    
    file_type = file_type_map.get(ext, 'Other')
    
    return file_path, file_size, file_type

# Helper function to convert Markdown to HTML
def convert_markdown_to_html(markdown_text):
    if not markdown_text:
        return ""
    return markdown.markdown(markdown_text)

@main.route('/')
def index():
    # Get latest notes, todos, and team members for dashboard
    recent_notes = Note.query.order_by(Note.updated_at.desc()).limit(5).all()
    permanent_notes = Note.query.filter_by(is_permanent=True).all()
    
    # Get all todos with ordering
    try:
        todos = Todo.query.order_by(Todo.order.asc(), Todo.priority.desc()).all()
    except:
        # Fallback in case order column doesn't exist yet
        todos = Todo.query.order_by(Todo.priority.desc()).all()
    
    # Get team priorities with ordering
    try:
        team_priorities = TeamPriority.query.order_by(TeamPriority.order.asc()).all()
    except:
        # Fallback in case order column doesn't exist yet
        team_priorities = TeamPriority.query.all()
    
    # Initialize the todo form for direct editing on dashboard
    todo_form = TodoForm()
    
    # Initialize the team priority form
    priority_form = TeamPriorityForm()
    
    team_members = TeamMember.query.all()
    favorite_links = Link.query.filter_by(is_favorite=True).all()
    favorite_files = File.query.filter_by(is_favorite=True).all()
    
    # Get ad-hoc statistics
    adhoc_count = AdHoc.query.count()
    total_adhoc_hours = db.session.query(db.func.sum(AdHoc.hours_needed)).scalar() or 0
    
    # Convert markdown to HTML for all notes
    for note in recent_notes + permanent_notes:
        note.html_content = convert_markdown_to_html(note.content)
    
    # Pass current time for due date comparison
    now = datetime.utcnow()
    
    return render_template('index.html', 
                          recent_notes=recent_notes,
                          permanent_notes=permanent_notes,
                          todos=todos,
                          todo_form=todo_form,
                          team_members=team_members,
                          favorite_links=favorite_links,
                          favorite_files=favorite_files,
                          team_priorities=team_priorities,
                          priority_form=priority_form,
                          adhoc_count=adhoc_count,
                          total_adhoc_hours=total_adhoc_hours,
                          now=now)

# Todo routes - Now only on dashboard
@main.route('/todo/add', methods=['POST'])
def add_todo():
    form = TodoForm()
    
    if form.validate_on_submit():
        # Get the highest order value to add new todos at the end
        try:
            highest_order = db.session.query(db.func.max(Todo.order)).scalar() or -1
            
            todo = Todo(
                content=form.content.data,
                priority=form.priority.data,
                order=highest_order + 1  # Set order to be after all existing todos
            )
        except:
            # Fallback in case order column doesn't exist yet
            todo = Todo(
                content=form.content.data,
                priority=form.priority.data
            )
            
        db.session.add(todo)
        db.session.commit()
        flash('Task added successfully!', 'success')
    
    return redirect(url_for('main.index'))

@main.route('/get_todos', methods=['GET'])
def get_todos():
    """AJAX endpoint to get the current todo list HTML"""
    try:
        todos = Todo.query.order_by(Todo.order.asc(), Todo.priority.desc()).all()
    except:
        # Fallback in case order column doesn't exist yet
        todos = Todo.query.order_by(Todo.priority.desc()).all()
    
    # Render just the todo list items (not the full page)
    return render_template('partials/todo_list.html', todos=todos)

@main.route('/todo/<int:todo_id>/toggle', methods=['POST'])
def toggle_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.completed = not todo.completed
    db.session.commit()
    return jsonify({'status': 'success', 'completed': todo.completed})

@main.route('/todo/<int:todo_id>/delete', methods=['POST'])
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('main.index'))

@main.route('/todo/<int:todo_id>/edit', methods=['POST'])
def edit_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    
    # Update the todo with the form data
    todo.content = request.form.get('content', todo.content)
    todo.priority = int(request.form.get('priority', todo.priority))
    
    db.session.commit()
    
    # Check if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success', 'message': 'Task updated successfully!'})
    
    flash('Task updated successfully!', 'success')
    return redirect(url_for('main.index'))

@main.route('/todo/clear-completed', methods=['POST'])
def clear_completed():
    completed_todos = Todo.query.filter_by(completed=True).all()
    for todo in completed_todos:
        db.session.delete(todo)
    db.session.commit()
    flash('Completed tasks have been cleared.', 'success')
    return redirect(url_for('main.index'))

@main.route('/todo/reorder', methods=['POST'])
def reorder_todos():
    data = request.json
    todo_ids = data.get('todoIds', [])
    
    try:
        # Update the order of todos in the database
        for i, todo_id in enumerate(todo_ids):
            todo = Todo.query.get_or_404(int(todo_id))
            todo.order = i
        
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Team Priority routes
@main.route('/priority/add', methods=['POST'])
def add_priority():
    form = TeamPriorityForm()
    
    if form.validate_on_submit():
        # Get the highest order value to add new priorities at the end
        try:
            highest_order = db.session.query(db.func.max(TeamPriority.order)).scalar() or -1
            
            priority = TeamPriority(
                content=form.content.data,
                color=form.color.data,
                order=highest_order + 1  # Set order to be after all existing priorities
            )
        except:
            # Fallback in case order column doesn't exist yet
            priority = TeamPriority(
                content=form.content.data,
                color=form.color.data
            )
            
        db.session.add(priority)
        db.session.commit()
        flash('Team priority added successfully!', 'success')
    
    return redirect(url_for('main.index'))

@main.route('/priority/<int:priority_id>/delete', methods=['POST'])
def delete_priority(priority_id):
    priority = TeamPriority.query.get_or_404(priority_id)
    db.session.delete(priority)
    db.session.commit()
    flash('Team priority deleted successfully!', 'success')
    return redirect(url_for('main.index'))

@main.route('/priority/reorder', methods=['POST'])
def reorder_priorities():
    data = request.json
    priority_ids = data.get('priorityIds', [])
    
    try:
        # Update the order of priorities in the database
        for i, priority_id in enumerate(priority_ids):
            priority = TeamPriority.query.get_or_404(int(priority_id))
            priority.order = i
        
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Redirect all to-do list pages to the dashboard
@todos.route('/', defaults={'path': ''})
@todos.route('/<path:path>')
def redirect_to_dashboard(path):
    """Force redirect all to-do list pages to the dashboard"""
    return redirect(url_for('main.index'))

# Block all todo-specific routes with 404 fallback
@todos.route('/new', methods=['GET', 'POST'])
@todos.route('/all', methods=['GET'])
@todos.route('/<int:list_id>', methods=['GET', 'POST'])
@todos.route('/<int:list_id>/edit', methods=['GET', 'POST'])
@todos.route('/<int:list_id>/delete', methods=['POST'])
@todos.route('/add_todo', methods=['POST'])
@todos.route('/edit_todo/<int:todo_id>', methods=['POST'])
@todos.route('/delete_todo/<int:todo_id>', methods=['POST'])
def block_todo_routes():
    return redirect(url_for('main.index'))

# Notes routes
@notes.route('/')
def all_notes():
    notes_list = Note.query.order_by(Note.updated_at.desc()).all()
    for note in notes_list:
        note.html_content = convert_markdown_to_html(note.content)
    return render_template('all_notes.html', notes=notes_list)

@notes.route('/new', methods=['GET', 'POST'])
def new_note():
    form = NoteForm()
    is_permanent = request.args.get('permanent', 'false').lower() == 'true'
    is_quick_note = request.args.get('quick', 'false').lower() == 'true'
    
    if form.validate_on_submit():
        note = Note(
            title=form.title.data or 'Untitled',
            content=form.content.data,
            is_permanent=form.is_permanent.data,
            category=form.category.data,
            is_quick_note=is_quick_note
        )
        db.session.add(note)
        db.session.commit()
        flash('Note created successfully!', 'success')
        
        # Redirect based on the type of note
        if is_quick_note:
            return redirect(url_for('notes.quick_notes'))
        return redirect(url_for('notes.view_note', note_id=note.id))
    
    # Pre-select permanent note checkbox if query param is set
    if is_permanent:
        form.is_permanent.data = True
    
    return render_template('note.html', form=form, is_new=True)

@notes.route('/<int:note_id>', methods=['GET'])
def view_note(note_id):
    note = Note.query.get_or_404(note_id)
    form = NoteForm(obj=note)
    html_content = convert_markdown_to_html(note.content)
    return render_template('note.html', note=note, form=form, is_new=False, html_content=html_content)

@notes.route('/<int:note_id>/edit', methods=['GET', 'POST'])
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    form = NoteForm(obj=note)
    
    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data
        note.is_permanent = form.is_permanent.data
        note.category = form.category.data
        note.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Note updated successfully!', 'success')
        return redirect(url_for('notes.view_note', note_id=note.id))
    
    html_content = convert_markdown_to_html(note.content)
    return render_template('note.html', note=note, form=form, is_new=False, html_content=html_content)

@notes.route('/<int:note_id>/delete', methods=['POST'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    flash('Note deleted successfully!', 'success')
    return redirect(url_for('notes.all_notes'))

@notes.route('/quick', methods=['GET'])
def quick_notes():
    notes_list = Note.query.filter_by(is_quick_note=True).order_by(Note.updated_at.desc()).all()
    for note in notes_list:
        note.html_content = convert_markdown_to_html(note.content)
    return render_template('quick_notes.html', notes=notes_list)

@notes.route('/save', methods=['POST'])
def save_note_ajax():
    data = request.json
    note_id = data.get('id')
    title = data.get('title')
    content = data.get('content', '')
    is_quick_note = data.get('is_quick_note', False)
    
    if note_id:
        # Update existing note
        note = Note.query.get_or_404(note_id)
        note.title = title if title else note.title
        note.content = content
        note.updated_at = datetime.utcnow()
    else:
        # Create new note
        note = Note(
            title=title or 'Untitled',
            content=content,
            is_permanent=data.get('is_permanent', False),
            category=data.get('category', None),
            is_quick_note=is_quick_note
        )
        db.session.add(note)
    
    db.session.commit()
    return jsonify({
        'id': note.id,
        'title': note.title,
        'updated_at': note.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    })

# Files routes
@files.route('/')
def all_files():
    files_list = File.query.order_by(File.created_at.desc()).all()
    return render_template('all_files.html', files=files_list)

@files.route('/new', methods=['GET', 'POST'])
def new_file():
    form = FileForm()
    if form.validate_on_submit():
        try:
            file_path, file_size, file_type = save_uploaded_file(form.file.data)
            
            # Create file record in database
            file = File(
                filename=form.title.data or form.file.data.filename,
                filepath=file_path,
                description=form.description.data,
                filetype=file_type,
                filesize=file_size,
                category=form.category.data,
                is_favorite=form.is_favorite.data
            )
            db.session.add(file)
            db.session.commit()
            flash('File uploaded successfully!', 'success')
            return redirect(url_for('files.all_files'))
        except Exception as e:
            flash(f'Error uploading file: {str(e)}', 'danger')
    
    return render_template('file_form.html', form=form, is_new=True)

@files.route('/<int:file_id>', methods=['GET'])
def view_file(file_id):
    file = File.query.get_or_404(file_id)
    return render_template('file_view.html', file=file)

@files.route('/<int:file_id>/edit', methods=['GET', 'POST'])
def edit_file(file_id):
    file = File.query.get_or_404(file_id)
    form = FileForm(obj=file)
    
    # We don't require a new file upload when editing
    form.file.validators = []
    if form.file.data is None:
        del form.file
    
    if form.validate_on_submit():
        # Update file metadata
        file.filename = form.title.data
        file.description = form.description.data
        file.category = form.category.data
        file.is_favorite = form.is_favorite.data
        
        # If a new file is uploaded, replace the old one
        if hasattr(form, 'file') and form.file.data:
            # Delete old file if it exists
            if os.path.exists(file.filepath):
                try:
                    os.remove(file.filepath)
                except Exception as e:
                    print(f"Error deleting old file: {e}")
            
            # Save new file
            file_path, file_size, file_type = save_uploaded_file(form.file.data)
            file.filepath = file_path
            file.filesize = file_size
            file.filetype = file_type
        
        db.session.commit()
        flash('File updated successfully!', 'success')
        return redirect(url_for('files.all_files'))
    
    return render_template('file_form.html', form=form, file=file, is_new=False)

@files.route('/<int:file_id>/delete', methods=['POST'])
def delete_file(file_id):
    file = File.query.get_or_404(file_id)
    
    # Delete physical file
    if file.filepath and os.path.exists(file.filepath):
        try:
            os.remove(file.filepath)
        except Exception as e:
            print(f"Error deleting file: {e}")
    
    # Delete database record
    db.session.delete(file)
    db.session.commit()
    flash('File deleted successfully!', 'success')
    return redirect(url_for('files.all_files'))

@files.route('/<int:file_id>/download')
def download_file(file_id):
    file = File.query.get_or_404(file_id)
    
    # Extract directory and filename from the filepath
    directory = os.path.dirname(file.filepath)
    filename = os.path.basename(file.filepath)
    
    # Use send_from_directory to send the file
    return send_from_directory(
        directory, 
        filename, 
        as_attachment=True, 
        download_name=secure_filename(file.filename)
    )

@files.route('/<int:file_id>/toggle_favorite', methods=['POST'])
def toggle_favorite(file_id):
    file = File.query.get_or_404(file_id)
    file.is_favorite = not file.is_favorite
    db.session.commit()
    
    # Check if we should return to the dashboard or files page
    referer = request.headers.get('Referer')
    if referer and 'files' in referer:
        return redirect(url_for('files.all_files'))
    return redirect(url_for('main.index'))

# Team member routes
@team.route('/')
def all_members():
    members = TeamMember.query.all()
    
    # Add these forms
    project_form = ProjectForm()
    task_form = TaskForm()
    development_form = DevelopmentForm()

    return render_template(
        'all_members.html',
        members=members,
        project_form=project_form,
        task_form=task_form,
        development_form=development_form
    )

@team.route('/new', methods=['GET', 'POST'])
def new_member():
    form = TeamMemberForm()
    if form.validate_on_submit():
        profile_pic = None
        if form.profile_picture.data:
            profile_pic = save_profile_picture(form.profile_picture.data)
            
        member = TeamMember(
            name=form.name.data,
            role=form.role.data,
            notes=form.notes.data,
            profile_picture=profile_pic
        )
        db.session.add(member)
        db.session.commit()
        flash('Team member added successfully!', 'success')
        return redirect(url_for('team.view_member', member_id=member.id))
    
    return render_template('member_form.html', form=form, is_new=True)

@team.route('/<int:member_id>', methods=['GET'])
def view_member(member_id):
    try:
        member = TeamMember.query.get_or_404(member_id)
        # Instantiate the forms for the member detail modals
        project_form = MemberProjectForm()
        task_form = MemberTaskForm()
        development_form = MemberDevelopmentForm()
        
        # Sort projects by priority (higher priority first)
        projects = MemberProject.query.filter_by(member_id=member_id).order_by(MemberProject.priority.desc()).all()
        member.projects = projects
        
        # Convert markdown to HTML for member notes - safely handle None
        if member.notes:
            member.html_notes = convert_markdown_to_html(member.notes)
        else:
            member.html_notes = ""
        
        return render_template('member.html', member=member,
                              project_form=project_form,
                              task_form=task_form,
                              development_form=development_form)
    except Exception as e:
        # Log the error for troubleshooting
        print(f"Error in view_member: {e}")
        # Return a user-friendly error page
        return render_template('error.html', error=str(e)), 500

@team.route('/<int:member_id>/edit', methods=['GET', 'POST'])
def edit_member(member_id):
    member = TeamMember.query.get_or_404(member_id)
    form = TeamMemberForm(obj=member)

    if form.validate_on_submit():
        try:
            member.name = form.name.data
            member.role = form.role.data
            member.notes = form.notes.data

            # Handle profile picture upload properly
            if form.profile_picture.data and hasattr(form.profile_picture.data, 'filename') and form.profile_picture.data.filename:
                try:
                    member.profile_picture = save_profile_picture(form.profile_picture.data)
                except Exception as e:
                    print(f"Error saving profile picture: {e}")
                    flash('There was an error uploading the profile picture. Other information was saved.', 'warning')
            
            member.updated_at = datetime.utcnow()
            db.session.commit()
            flash('Team member updated successfully!', 'success')
            return redirect(url_for('team.view_member', member_id=member.id))
        except Exception as e:
            db.session.rollback()
            print(f"Error updating team member: {e}")
            flash('An error occurred while saving the team member information.', 'danger')

    return render_template('member_form.html', form=form, member=member, is_new=False)

@team.route('/<int:member_id>/delete', methods=['POST'])
def delete_member(member_id):
    member = TeamMember.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    flash('Team member deleted successfully!', 'success')
    return redirect(url_for('team.all_members'))

# Member Task Routes
@team.route('/member/<int:member_id>/add_task', methods=['POST'])
def add_member_task(member_id):
    member = TeamMember.query.get_or_404(member_id)
    form = MemberTaskForm()
    
    if form.validate_on_submit():
        task = MemberTask(
            content=form.content.data,
            member_id=member.id
        )
        
        # Handle the due_date if it's in the form
        if hasattr(form, 'due_date') and form.due_date.data:
            task.due_date = form.due_date.data
            
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully!', 'success')
    
    return redirect(url_for('team.view_member', member_id=member.id))

@team.route('/task/<int:task_id>/toggle', methods=['POST'])
def toggle_member_task(task_id):
    task = MemberTask.query.get_or_404(task_id)
    task.completed = not task.completed
    db.session.commit()
    return jsonify({'status': 'success', 'completed': task.completed})

@team.route('/task/<int:task_id>/delete', methods=['POST'])
def delete_member_task(task_id):
    task = MemberTask.query.get_or_404(task_id)
    member_id = task.member_id  # Save the member_id before deleting the task
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('team.view_member', member_id=member_id))

# Member Project Routes
@team.route('/member/<int:member_id>/add_project', methods=['POST'])
def add_member_project(member_id):
    member = TeamMember.query.get_or_404(member_id)
    form = MemberProjectForm()
    
    if form.validate_on_submit():
        project = MemberProject(
            name=form.name.data,
            description=form.description.data,
            priority=form.priority.data,
            member_id=member.id
        )
        db.session.add(project)
        db.session.commit()
        flash('Project added successfully!', 'success')
    
    return redirect(url_for('team.view_member', member_id=member.id))

@team.route('/project/<int:project_id>/delete', methods=['POST'])
def delete_member_project(project_id):
    project = MemberProject.query.get_or_404(project_id)
    member_id = project.member_id
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('team.view_member', member_id=member_id))

# Member Note Routes
@team.route('/member/<int:member_id>/add_note', methods=['POST'])
def add_member_note(member_id):
    member = TeamMember.query.get_or_404(member_id)
    form = MemberNoteForm()
    
    if form.validate_on_submit():
        note = MemberNote(
            title=form.title.data,
            content=form.content.data,
            member_id=member.id
        )
        db.session.add(note)
        db.session.commit()
        flash('Note added successfully!', 'success')
    
    return redirect(url_for('team.all_members'))

@team.route('/note/<int:note_id>/delete', methods=['POST'])
def delete_member_note(note_id):
    note = MemberNote.query.get_or_404(note_id)
    member_id = note.member_id
    db.session.delete(note)
    db.session.commit()
    flash('Note deleted successfully!', 'success')
    return redirect(url_for('team.all_members'))

# Member Development Routes
@team.route('/member/<int:member_id>/add_development', methods=['POST'])
def add_member_development(member_id):
    member = TeamMember.query.get_or_404(member_id)
    form = MemberDevelopmentForm()
    
    if form.validate_on_submit():
        development = MemberDevelopment(
            title=form.title.data,
            description=form.description.data,
            date=form.date.data if hasattr(form, 'date') else None,
            member_id=member.id
        )
        db.session.add(development)
        db.session.commit()
        flash('Development added successfully!', 'success')
    
    return redirect(url_for('team.all_members'))

@team.route('/development/<int:development_id>/delete', methods=['POST'])
def delete_member_development(development_id):
    development = MemberDevelopment.query.get_or_404(development_id)
    member_id = development.member_id
    db.session.delete(development)
    db.session.commit()
    flash('Development deleted successfully!', 'success')
    return redirect(url_for('team.all_members'))

@team.route('/simple/<int:member_id>', methods=['GET'])
def simple_view_member(member_id):
    """A simplified view to test member access"""
    member = TeamMember.query.get_or_404(member_id)
    return f"<h1>Member: {member.name}</h1><p>Role: {member.role or 'Not specified'}</p>"

# Add New Entries
@team.route('/member/<int:member_id>/add_project', methods=['POST'])
def add_project(member_id):
    form = ProjectForm()
    if form.validate_on_submit():
        project = MemberProject(
            name=form.name.data,
            description=form.description.data,
            member_id=member_id
        )
        db.session.add(project)
        db.session.commit()
        flash('Project added successfully!', 'success')
    return redirect(url_for('team.view_member', member_id=member_id))

@team.route('/member/<int:member_id>/add_task', methods=['POST'])
def add_task(member_id):
    form = TaskForm()
    if form.validate_on_submit():
        task = MemberTask(
            content=form.content.data,
            completed=form.completed.data,
            member_id=member_id
        )
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully!', 'success')
    return redirect(url_for('team.view_member', member_id=member_id))

@team.route('/member/<int:member_id>/add_development', methods=['POST'])
def add_development(member_id):
    form = DevelopmentForm()
    if form.validate_on_submit():
        development = MemberDevelopment(
            title=form.title.data,
            description=form.description.data,
            date=form.date.data,
            member_id=member_id
        )
        db.session.add(development)
        db.session.commit()
        flash('Development added successfully!', 'success')
    return redirect(url_for('team.view_member', member_id=member_id))

# Edit Entries
@team.route('/project/<int:project_id>/edit', methods=['POST'])
def edit_project(project_id):
    project = MemberProject.query.get_or_404(project_id)
    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        project.name = form.name.data
        project.description = form.description.data
        project.priority = form.priority.data  # Add this line to update priority
        db.session.commit()
        flash('Project updated successfully!', 'success')
    return redirect(url_for('team.view_member', member_id=project.member_id))

@team.route('/task/<int:task_id>/edit', methods=['POST'])
def edit_task(task_id):
    task = MemberTask.query.get_or_404(task_id)
    form = TaskForm(obj=task)
    if form.validate_on_submit():
        task.content = form.content.data
        task.completed = form.completed.data
        db.session.commit()
        flash('Task updated successfully!', 'success')
    return redirect(url_for('team.view_member', member_id=task.member_id))

@team.route('/development/<int:development_id>/edit', methods=['POST'])
def edit_development(development_id):
    development = MemberDevelopment.query.get_or_404(development_id)
    form = DevelopmentForm(obj=development)
    if form.validate_on_submit():
        development.title = form.title.data
        development.description = form.description.data
        development.date = form.date.data
        db.session.commit()
        flash('Development updated successfully!', 'success')
    return redirect(url_for('team.view_member', member_id=development.member_id))

# Move Items
@team.route('/move_item/<string:item_type>/<int:item_id>', methods=['POST'])
def move_item(item_type, item_id):
    form = MoveItemForm()
    if form.validate_on_submit():
        if item_type == 'project':
            item = MemberProject.query.get_or_404(item_id)
        elif item_type == 'task':
            item = MemberTask.query.get_or_404(item_id)
        elif item_type == 'development':
            item = MemberDevelopment.query.get_or_404(item_id)
        else:
            flash('Invalid item type.', 'danger')
            return redirect(url_for('team.all_members'))

        new_type = form.item_type.data
        if new_type == 'project':
            new_item = MemberProject(name=item.name, description=item.description, member_id=item.member_id)
        elif new_type == 'task':
            new_item = MemberTask(content=item.content, completed=False, member_id=item.member_id)
        elif new_type == 'development':
            new_item = MemberDevelopment(title=item.title, description=item.description, date=item.date, member_id=item.member_id)

        db.session.add(new_item)
        db.session.delete(item)
        db.session.commit()
        flash(f'Item successfully moved to {new_type.capitalize()}!', 'success')
    return redirect(url_for('team.view_member', member_id=item.member_id))

@team.route('/project/<int:project_id>/delete', methods=['POST'])
def delete_project(project_id):
    project = MemberProject.query.get_or_404(project_id)
    member_id = project.member_id
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('team.view_member', member_id=member_id))

@team.route('/reorder_items/<string:item_type>', methods=['POST'])
def reorder_items(item_type):
    data = request.json.get('order')
    if item_type == 'project':
        items = MemberProject.query.filter(MemberProject.id.in_(data)).all()
    elif item_type == 'task':
        items = MemberTask.query.filter(MemberTask.id.in_(data)).all()
    elif item_type == 'development':
        items = MemberDevelopment.query.filter(MemberDevelopment.id.in_(data)).all()
    else:
        return jsonify({'status': 'error', 'message': 'Invalid item type'}), 400

    # Reordering logic
    for index, item_id in enumerate(data):
        item = next((item for item in items if item.id == int(item_id)), None)
        if item:
            item.order = index

    db.session.commit()
    return jsonify({'status': 'success'})

@team.route('/update_item/<string:item_type>/<int:item_id>', methods=['POST'])
def update_item(item_type, item_id):
    data = request.json
    if item_type == 'project':
        item = MemberProject.query.get_or_404(item_id)
        item.name = data.get('name')
        item.description = data.get('description')
    elif item_type == 'task':
        item = MemberTask.query.get_or_404(item_id)
        item.content = data.get('content')
        item.completed = data.get('completed')
    elif item_type == 'development':
        item = MemberDevelopment.query.get_or_404(item_id)
        item.title = data.get('title')
        item.description = data.get('description')

    db.session.commit()
    return jsonify({'status': 'success'})

# Links routes
@links.route('/')
def all_links():
    links_list = Link.query.order_by(Link.title).all()
    return render_template('all_links.html', links=links_list)

@links.route('/new', methods=['GET', 'POST'])
def new_link():
    form = LinkForm()
    if form.validate_on_submit():
        link = Link(
            title=form.title.data,
            url=form.url.data,
            description=form.description.data,
            category=form.category.data,
            is_favorite=form.is_favorite.data
        )
        db.session.add(link)
        db.session.commit()
        flash('Link added successfully!', 'success')
        return redirect(url_for('links.all_links'))
    
    return render_template('link_form.html', form=form, is_new=True)

@links.route('/<int:link_id>/edit', methods=['GET', 'POST'])
def edit_link(link_id):
    link = Link.query.get_or_404(link_id)
    form = LinkForm(obj=link)
    
    if form.validate_on_submit():
        link.title = form.title.data
        link.url = form.url.data
        link.description = form.description.data
        link.category = form.category.data
        link.is_favorite = form.is_favorite.data
        db.session.commit()
        flash('Link updated successfully!', 'success')
        return redirect(url_for('links.all_links'))
    
    return render_template('link_form.html', form=form, link=link, is_new=False)

@links.route('/<int:link_id>/delete', methods=['POST'])
def delete_link(link_id):
    link = Link.query.get_or_404(link_id)
    db.session.delete(link)
    db.session.commit()
    flash('Link deleted successfully!', 'success')
    return redirect(url_for('links.all_links'))

@links.route('/<int:link_id>/toggle_favorite', methods=['POST'])
def toggle_favorite(link_id):
    link = Link.query.get_or_404(link_id)
    link.is_favorite = not link.is_favorite
    db.session.commit()
    
    # Check if we should return to the dashboard or links page
    referer = request.headers.get('Referer')
    if referer and 'links' in referer:
        return redirect(url_for('links.all_links'))
    return redirect(url_for('main.index'))

# Ad-hoc routes
@adhocs.route('/')
def all_adhocs():
    adhocs_list = AdHoc.query.order_by(AdHoc.created_at.desc()).all()
    # Calculate total hours
    total_hours = sum(adhoc.hours_needed for adhoc in adhocs_list)
    return render_template('all_adhocs.html', adhocs=adhocs_list, total_hours=total_hours)

@adhocs.route('/new', methods=['GET', 'POST'])
def new_adhoc():
    form = AdHocForm()
    if form.validate_on_submit():
        try:
            hours = float(form.hours_needed.data)
            adhoc = AdHoc(
                month=form.month.data,
                title=form.title.data,
                description=form.description.data,
                completed_by=form.completed_by.data,
                hours_needed=hours
            )
            db.session.add(adhoc)
            db.session.commit()
            flash('Ad-hoc added successfully!', 'success')
            return redirect(url_for('adhocs.all_adhocs'))
        except ValueError:
            flash('Please enter a valid number for hours needed', 'danger')
    
    return render_template('adhoc_form.html', form=form, is_new=True)

@adhocs.route('/<int:adhoc_id>/edit', methods=['GET', 'POST'])
def edit_adhoc(adhoc_id):
    adhoc = AdHoc.query.get_or_404(adhoc_id)
    form = AdHocForm(obj=adhoc)
    
    if form.validate_on_submit():
        try:
            hours = float(form.hours_needed.data)
            adhoc.month = form.month.data
            adhoc.title = form.title.data
            adhoc.description = form.description.data
            adhoc.completed_by = form.completed_by.data
            adhoc.hours_needed = hours
            db.session.commit()
            flash('Ad-hoc updated successfully!', 'success')
            return redirect(url_for('adhocs.all_adhocs'))
        except ValueError:
            flash('Please enter a valid number for hours needed', 'danger')
    
    return render_template('adhoc_form.html', form=form, adhoc=adhoc, is_new=False)

@adhocs.route('/<int:adhoc_id>/delete', methods=['POST'])
def delete_adhoc(adhoc_id):
    adhoc = AdHoc.query.get_or_404(adhoc_id)
    db.session.delete(adhoc)
    db.session.commit()
    flash('Ad-hoc deleted successfully!', 'success')
    return redirect(url_for('adhocs.all_adhocs'))

# Settings routes
@settings.route('/', methods=['GET', 'POST'])
def preferences():
    preferences = UserPreference.query.first()
    form = UserPreferenceForm(obj=preferences)
    
    if form.validate_on_submit():
        if not preferences:
            preferences = UserPreference()
            db.session.add(preferences)
        
        preferences.theme = form.theme.data
        preferences.font_family = form.font_family.data
        preferences.font_size = form.font_size.data
        preferences.accent_color = form.accent_color.data
        db.session.commit()
        flash('Preferences updated successfully!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('settings/preferences.html', form=form)

# Register all blueprints
def register_blueprints(app):
    app.register_blueprint(main)
    app.register_blueprint(notes)
    app.register_blueprint(team)
    app.register_blueprint(links)
    app.register_blueprint(settings)
    app.register_blueprint(todos)  # Keep this to handle redirects
    app.register_blueprint(files)  # Register the files blueprint
    app.register_blueprint(adhocs)  # Register the adhocs blueprint