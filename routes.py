from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import os
import markdown
from werkzeug.utils import secure_filename
from models import db, Note, Todo, TodoList, TeamMember, MemberTask, Link, UserPreference, MemberProject, MemberNote, MemberDevelopment
from forms import NoteForm, TodoForm, TodoListForm, TeamMemberForm, MemberTaskForm, LinkForm, UserPreferenceForm, MemberProjectForm, MemberNoteForm, MemberDevelopmentForm
from PIL import Image

# Create blueprints for different sections of the app
main = Blueprint('main', __name__)
notes = Blueprint('notes', __name__, url_prefix='/notes')
todos = Blueprint('todos', __name__, url_prefix='/todos')
team = Blueprint('team', __name__, url_prefix='/team')
links = Blueprint('links', __name__, url_prefix='/links')
settings = Blueprint('settings', __name__, url_prefix='/settings')

# Add context processor to make preferences available in all templates
@main.app_context_processor
def inject_preferences():
    preferences = UserPreference.query.first()
    if not preferences:
        preferences = UserPreference()
        db.session.add(preferences)
        db.session.commit()
    return dict(preferences=preferences)

# Helper function to generate a title from content
def generate_title_from_content(content, max_length=50):
    # Get the first line, or first few characters
    if '\n' in content:
        first_line = content.split('\n')[0].strip()
    else:
        first_line = content.strip()
    
    # Truncate if needed and add ellipsis
    if len(first_line) > max_length:
        return first_line[:max_length] + '...'
    elif not first_line:  # If empty or just whitespace
        return f"Quick Note - {datetime.utcnow().strftime('%m/%d/%Y %H:%M')}"
    else:
        return first_line

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
    todo_lists = TodoList.query.all()
    team_members = TeamMember.query.all()
    favorite_links = Link.query.filter_by(is_favorite=True).all()
    
    # Convert markdown to HTML for all notes
    for note in recent_notes + permanent_notes:
        note.html_content = convert_markdown_to_html(note.content)
    
    return render_template('index.html', 
                          recent_notes=recent_notes,
                          permanent_notes=permanent_notes,
                          todo_lists=todo_lists,
                          team_members=team_members,
                          favorite_links=favorite_links)

# Notes routes
@notes.route('/')
def all_notes():
    notes_list = Note.query.order_by(Note.updated_at.desc()).all()
    for note in notes_list:
        note.html_content = convert_markdown_to_html(note.content)
    return render_template('notes/all_notes.html', notes=notes_list)

@notes.route('/quick')
def quick_notes():
    quick_notes = Note.query.filter_by(is_quick_note=True).order_by(Note.updated_at.desc()).all()
    for note in quick_notes:
        note.html_content = convert_markdown_to_html(note.content)
    return render_template('notes/quick_notes.html', notes=quick_notes)

@notes.route('/new', methods=['GET', 'POST'])
def new_note():
    form = NoteForm()
    is_quick = request.args.get('quick', 'false').lower() == 'true'
    
    if form.validate_on_submit():
        # If it's a quick note and no title is provided, generate one from content
        title = form.title.data
        if is_quick and not title:
            title = generate_title_from_content(form.content.data)
            
        note = Note(
            title=title,
            content=form.content.data,
            is_quick_note=form.is_quick_note.data,
            is_permanent=form.is_permanent.data,
            category=form.category.data
        )
        db.session.add(note)
        db.session.commit()
        flash('Note created successfully!', 'success')
        return redirect(url_for('notes.view_note', note_id=note.id))
    
    # Pre-select quick note checkbox if query param is set
    if is_quick:
        form.is_quick_note.data = True
    
    return render_template('notes/note.html', form=form, is_new=True, is_quick=is_quick)

@notes.route('/<int:note_id>', methods=['GET'])
def view_note(note_id):
    note = Note.query.get_or_404(note_id)
    form = NoteForm(obj=note)
    html_content = convert_markdown_to_html(note.content)
    is_quick = note.is_quick_note
    return render_template('notes/note.html', note=note, form=form, is_new=False, html_content=html_content, is_quick=is_quick)

@notes.route('/<int:note_id>/edit', methods=['GET', 'POST'])
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    form = NoteForm(obj=note)
    is_quick = note.is_quick_note
    
    if form.validate_on_submit():
        # If it's a quick note and title is empty, generate one
        title = form.title.data
        if is_quick and not title:
            title = generate_title_from_content(form.content.data)
            
        note.title = title
        note.content = form.content.data
        note.is_quick_note = form.is_quick_note.data
        note.is_permanent = form.is_permanent.data
        note.category = form.category.data
        note.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Note updated successfully!', 'success')
        return redirect(url_for('notes.view_note', note_id=note.id))
    
    html_content = convert_markdown_to_html(note.content)
    return render_template('notes/note.html', note=note, form=form, is_new=False, html_content=html_content, is_quick=is_quick)

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
    content = data.get('content', '')
    is_quick_note = data.get('is_quick_note', False)
    
    # Generate title for quick notes if not provided
    title = data.get('title')
    if is_quick_note and not title:
        title = generate_title_from_content(content)
    
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
            is_quick_note=is_quick_note,
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

# The rest of the routes.py file remains the same...