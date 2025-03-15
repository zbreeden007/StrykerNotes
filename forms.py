from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, Optional

class NoteForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('Content')
    is_permanent = BooleanField('Keep Permanently')
    category = StringField('Category', validators=[Length(max=50)])
    submit = SubmitField('Save Note')

class TodoForm(FlaskForm):
    content = StringField('Task', validators=[DataRequired(), Length(max=200)])
    priority = SelectField('Priority', choices=[(0, 'Low'), (1, 'Medium'), (2, 'High')], coerce=int)
    submit = SubmitField('Add Task')

class TeamMemberForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    role = StringField('Role', validators=[Length(max=100)])
    notes = TextAreaField('Notes')
    profile_picture = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Save Team Member')

class MemberTaskForm(FlaskForm):
    content = StringField('Task', validators=[DataRequired(), Length(max=200)])
    submit = SubmitField('Add Task')

class LinkForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    url = StringField('URL', validators=[DataRequired(), Length(max=500)])
    description = TextAreaField('Description')
    category = StringField('Category', validators=[Length(max=50)])
    is_favorite = BooleanField('Add to Favorites')
    submit = SubmitField('Save Link')

class UserPreferenceForm(FlaskForm):
    theme = SelectField('Theme', choices=[('light', 'Light'), ('dark', 'Dark'), ('blue', 'Blue'), ('green', 'Green')])
    font_family = SelectField('Font Family', choices=[
        ('Arial, sans-serif', 'Arial'), 
        ('Helvetica, sans-serif', 'Helvetica'),
        ('Times New Roman, serif', 'Times New Roman'),
        ('Georgia, serif', 'Georgia'),
        ('Courier New, monospace', 'Courier New')
    ])
    font_size = SelectField('Font Size', choices=[
        ('12px', 'Small'),
        ('14px', 'Medium'),
        ('16px', 'Large'),
        ('18px', 'Extra Large')
    ])
    accent_color = StringField('Accent Color')
    submit = SubmitField('Save Preferences')

class MemberProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    submit = SubmitField('Save Project')

class MemberNoteForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('Content')
    submit = SubmitField('Save Note')

class MemberDevelopmentForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    submit = SubmitField('Save Development')