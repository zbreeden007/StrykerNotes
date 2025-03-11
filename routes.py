from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import os
import markdown
from werkzeug.utils import secure_filename
from models import db, Note, Todo, TodoList, TeamMember, MemberTask, Link, UserPreference, MemberProject, MemberNote, MemberDevelopment
from forms import NoteForm, TodoForm, TeamMemberForm, MemberTaskForm, LinkForm, UserPreferenceForm, MemberProjectForm, MemberNoteForm, MemberDevelopmentForm
from PIL import Image

# Create blueprints for different sections of the app
main = Blueprint('main', __name__)
notes = Blueprint('notes', __name__, url_prefix='/notes')
team = Blueprint('team', __name__, url_prefix='/team')
links = Blueprint('links', __name__, url_prefix='/links')
settings = Blueprint('settings', __name__, url_prefix='/settings')
todos = Blueprint('todos', __name__, url_prefix='/todos')  # Keep for redirects

# Add context processor to make preferences available in all templates
@main.app_context_processor
def inject_preferences():
    preferences = UserPreference.query.first()
    if not preferences:
        preferences = UserPreference()
        db.session.add(preferences)
        db.session.commit()
    return dict(preferences=preferences)

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

# Helper function to convert Markdown to HTML
def convert_markdown_to_html(markdown_text):
    if not markdown_text:
        return ""
    return markdown.markdown(markdown_text)

# Main routes
@main.route('/')
def index():
    # Get latest notes, todos, and team members for dashboard
    recent_notes = Note.query.order_by(Note.updated_at.desc()).limit(5).all()
    permanent_notes = Note.query.filter_by(is_permanent=True).all()
    
    # Get all todos with ordering
    try:
        todos = Todo.query.order_by(Todo.order.asc(), Todo.priority.desc(), Todo.due_date.asc()).all()
    except:
        # Fallback in case order column doesn't exist yet
        todos = Todo.query.order_by(Todo.priority.desc(), Todo.due_date.asc()).all()
    
    # Initialize the todo form for direct editing on dashboard
    todo_form = TodoForm()
    
    team_members = TeamMember.query.all()
    favorite_links = Link.query.filter_by(is_favorite=True).all()
    
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
                due_date=form.due_date.data,
                priority=form.priority.data,
                order=highest_order + 1  # Set order to be after all existing todos
            )
        except:
            # Fallback in case order column doesn't exist yet
            todo = Todo(
                content=form.content.data,
                due_date=form.due_date.data,
                priority=form.priority.data
            )
            
        db.session.add(todo)
        db.session.commit()
        flash('Task added successfully!', 'success')
    
    return redirect(url_for('main.index'))

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
    
    # Handle due date - might be empty string
    due_date = request.form.get('due_date', '')
    if due_date:
        try:
            todo.due_date = datetime.strptime(due_date, '%Y-%m-%dT%H:%M')
        except ValueError:
            pass  # Keep the current value if parsing fails
    else:
        # If empty string is passed, clear the due date
        todo.due_date = None
    
    db.session.commit()
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

# Redirect all to-do list pages to the dashboard
@todos.route('/', defaults={'path': ''})
@todos.route('/<path:path>')
def redirect_to_dashboard(path):
    """Redirect all to-do list pages to the dashboard"""
    return redirect(url_for('main.index'))

# Notes routes
@notes.route('/')
def all_notes():
    notes_list = Note.query.order_by(Note.updated_at.desc()).all()
    for note in notes_list:
        note.html_content = convert_markdown_to_html(note.content)
    return render_template('notes/all_notes.html', notes=notes_list)

@notes.route('/new', methods=['GET', 'POST'])
def new_note():
    form = NoteForm()
    is_permanent = request.args.get('permanent', 'false').lower() == 'true'
    
    if form.validate_on_submit():
        note = Note(
            title=form.title.data,
            content=form.content.data,
            is_permanent=form.is_permanent.data,
            category=form.category.data
        )
        db.session.add(note)
        db.session.commit()
        flash('Note created successfully!', 'success')
        return redirect(url_for('notes.view_note', note_id=note.id))
    
    # Pre-select permanent note checkbox if query param is set
    if is_permanent:
        form.is_permanent.data = True
    
    return render_template('notes/note.html', form=form, is_new=True)

@notes.route('/<int:note_id>', methods=['GET'])
def view_note(note_id):
    note = Note.query.get_or_404(note_id)
    form = NoteForm(obj=note)
    html_content = convert_markdown_to_html(note.content)
    return render_template('notes/note.html', note=note, form=form, is_new=False, html_content=html_content)

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
    return render_template('notes/note.html', note=note, form=form, is_new=False, html_content=html_content)

@notes.route('/<int:note_id>/delete', methods=['POST'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    flash('Note deleted successfully!', 'success')
    return redirect(url_for('notes.all_notes'))

@notes.route('/save', methods=['POST'])
def save_note_ajax():
    data = request.json
    note_id = data.get('id')
    title = data.get('title')
    content = data.get('content', '')
    
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
            category=data.get('category', None)
        )
        db.session.add(note)
    
    db.session.commit()
    return jsonify({
        'id': note.id,
        'title': note.title,
        'updated_at': note.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    })

# Team member routes
@team.route('/')
def all_members():
    members = TeamMember.query.all()
    project_form = MemberProjectForm()
    task_form = MemberTaskForm()
    note_form = MemberNoteForm()
    development_form = MemberDevelopmentForm()
    
    return render_template('team/all_members.html', 
                           members=members, 
                           project_form=project_form,
                           task_form=task_form,
                           note_form=note_form, 
                           development_form=development_form)

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
    
    return render_template('team/member_form.html', form=form, is_new=True)

@team.route('/<int:member_id>', methods=['GET'])
def view_member(member_id):
    member = TeamMember.query.get_or_404(member_id)
    task_form = MemberTaskForm()
    
    # Convert markdown to HTML for member notes
    member.html_notes = convert_markdown_to_html(member.notes)
    
    return render_template('team/member.html', member=member, form=task_form)

@team.route('/<int:member_id>/edit', methods=['GET', 'POST'])
def edit_member(member_id):
    member = TeamMember.query.get_or_404(member_id)
    form = TeamMemberForm(obj=member)
    
    if form.validate_on_submit():
        member.name = form.name.data
        member.role = form.role.data
        member.notes = form.notes.data
        
        if form.profile_picture.data:
            member.profile_picture = save_profile_picture(form.profile_picture.data)
            
        member.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Team member updated successfully!', 'success')
        return redirect(url_for('team.view_member', member_id=member.id))
    
    return render_template('team/member_form.html', form=form, member=member, is_new=False)

@team.route('/<int:member_id>/add_task', methods=['POST'])
def add_member_task(member_id):
    member = TeamMember.query.get_or_404(member_id)
    form = MemberTaskForm()
    
    if form.validate_on_submit():
        task = MemberTask(
            content=form.content.data,
            due_date=form.due_date.data,
            member_id=member.id
        )
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully!', 'success')
    
    return redirect(url_for('team.view_member', member_id=member_id))

@team.route('/task/<int:task_id>/toggle', methods=['POST'])
def toggle_member_task(task_id):
    task = MemberTask.query.get_or_404(task_id)
    task.completed = not task.completed
    db.session.commit()
    return jsonify({'status': 'success', 'completed': task.completed})

@team.route('/task/<int:task_id>/delete', methods=['POST'])
def delete_member_task(task_id):
    task = MemberTask.query.get_or_404(task_id)
    member_id = task.member_id
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('team.view_member', member_id=member_id))

@team.route('/<int:member_id>/delete', methods=['POST'])
def delete_member(member_id):
    member = TeamMember.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    flash('Team member deleted successfully!', 'success')
    return redirect(url_for('team.all_members'))

# Project routes
@team.route('/<int:member_id>/add_project', methods=['POST'])
def add_member_project(member_id):
    member = TeamMember.query.get_or_404(member_id)
    form = MemberProjectForm()
    
    if form.validate_on_submit():
        project = MemberProject(
            name=form.name.data,
            description=form.description.data,
            member_id=member.id
        )
        db.session.add(project)
        db.session.commit()
        flash('Project added successfully!', 'success')
    
    return redirect(url_for('team.all_members'))

@team.route('/project/<int:project_id>/delete', methods=['POST'])
def delete_member_project(project_id):
    project = MemberProject.query.get_or_404(project_id)
    member_id = project.member_id
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('team.all_members'))

# Note routes
@team.route('/<int:member_id>/add_note', methods=['POST'])
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

# Development routes
@team.route('/<int:member_id>/add_development', methods=['POST'])
def add_member_development(member_id):
    member = TeamMember.query.get_or_404(member_id)
    form = MemberDevelopmentForm()
    
    if form.validate_on_submit():
        development = MemberDevelopment(
            title=form.title.data,
            description=form.description.data,
            date=form.date.data,
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

# Links routes
@links.route('/')
def all_links():
    links_list = Link.query.order_by(Link.title).all()
    return render_template('links/all_links.html', links=links_list)

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
    
    return render_template('links/link_form.html', form=form, is_new=True)

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
    
    return render_template('links/link_form.html', form=form, link=link, is_new=False)

@links.route('/<int:link_id>/delete', methods=['POST'])
def delete_link(link_id):
    link = Link.query.get_or_404(link_id)
    db.session.delete(link)
    db.session.commit()
    flash('Link deleted successfully!', 'success')
    return redirect(url_for('links.all_links'))

# New route for toggling favorite status
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

# Settings routes
@settings.route('/', methods=['GET', 'POST'])
def preferences():
    preferences = UserPreference.query.first()
    form = UserPreferenceForm(obj=preferences)
    
    if form.validate_on_submit():
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