from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_quick_note = db.Column(db.Boolean, default=False)
    is_permanent = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(50), nullable=True)
    
    def __repr__(self):
        return f'<Note {self.title}>'

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.Integer, default=0)  # 0 = low, 1 = medium, 2 = high
    order = db.Column(db.Integer, default=0)  # New field for drag and drop ordering
    
    def __repr__(self):
        return f'<Todo {self.content}>'

# Keeping this for backward compatibility but won't use multiple lists anymore
class TodoList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TodoList {self.name}>'

class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tasks = db.relationship('MemberTask', backref='member', lazy=True, cascade="all, delete-orphan")
    projects = db.relationship('MemberProject', backref='member', lazy=True, cascade="all, delete-orphan")
    member_notes = db.relationship('MemberNote', backref='member', lazy=True, cascade="all, delete-orphan")
    developments = db.relationship('MemberDevelopment', backref='member', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<TeamMember {self.name}>'

class MemberTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.DateTime, nullable=True)
    member_id = db.Column(db.Integer, db.ForeignKey('team_member.id'), nullable=False)
    
    def __repr__(self):
        return f'<MemberTask {self.content}>'

class MemberProject(db.Model):
    __tablename__ = 'member_project'
    __table_args__ = {'extend_existing': True}  # Add this to fix the duplicate table error
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    member_id = db.Column(db.Integer, db.ForeignKey('team_member.id'), nullable=False)
    
    def __repr__(self):
        return f'<MemberProject {self.name}>'

class MemberNote(db.Model):
    __tablename__ = 'member_note'
    __table_args__ = {'extend_existing': True}  # Add this to fix the duplicate table error
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    member_id = db.Column(db.Integer, db.ForeignKey('team_member.id'), nullable=False)
    
    def __repr__(self):
        return f'<MemberNote {self.title}>'

class MemberDevelopment(db.Model):
    __tablename__ = 'member_development'
    __table_args__ = {'extend_existing': True}  # Add this to fix the duplicate table error
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    member_id = db.Column(db.Integer, db.ForeignKey('team_member.id'), nullable=False)
    
    def __repr__(self):
        return f'<MemberDevelopment {self.title}>'

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(50), nullable=True)
    is_favorite = db.Column(db.Boolean, default=False)  # New column for favorite links
    
    def __repr__(self):
        return f'<Link {self.title}>'

class UserPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.String(50), default='light')
    font_family = db.Column(db.String(100), default='Arial, sans-serif')
    font_size = db.Column(db.String(20), default='14px')
    accent_color = db.Column(db.String(20), default='#007bff')
    
    def __repr__(self):
        return f'<UserPreference {self.id}>'