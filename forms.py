from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.fields import DateField
from datetime import datetime

class NoteForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('Content')
    is_permanent = BooleanField('Keep Permanently')
    category = StringField('Category', validators=[Length(max=50)])
    submit = SubmitField('Save Note')

class TodoForm(FlaskForm):
    content = StringField('Task', validators=[DataRequired(), Length(max=200)])
    priority = SelectField('Priority', choices=[(0, 'Later'), (1, 'This Week'), (2, 'Today')], coerce=int)
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

class ProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    priority = SelectField('Priority', 
                          choices=[(0, 'None')] + [(i, str(i)) for i in range(1, 21)], 
                          coerce=int, default=0)
    submit = SubmitField('Save Project')

class TaskForm(FlaskForm):
    content = StringField('Task Content', validators=[DataRequired()])
    completed = BooleanField('Completed')
    submit = SubmitField('Save Task')

class DevelopmentForm(FlaskForm):
    title = StringField('Development Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    date = DateField('Date', format='%Y-%m-%d')
    submit = SubmitField('Save Development')

class MoveItemForm(FlaskForm):
    item_type = SelectField('Move to', choices=[
        ('project', 'Project'),
        ('task', 'Task'),
        ('development', 'Development')
    ])
    submit = SubmitField('Move Item')

class LinkForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    url = StringField('URL', validators=[DataRequired(), Length(max=500)])
    description = TextAreaField('Description')
    category = StringField('Category', validators=[Length(max=50)])
    is_favorite = BooleanField('Add to Favorites')
    submit = SubmitField('Save Link')

class FileForm(FlaskForm):
    file = FileField('File', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv', 'jpg', 'jpeg', 'png', 'gif'], 
                   'Allowed file types: PDF, Office documents, text files, and images.')
    ])
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    category = StringField('Category', validators=[Length(max=50)])
    is_favorite = BooleanField('Add to Favorites')
    submit = SubmitField('Upload File')

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
    priority = SelectField('Priority', 
                          choices=[(0, 'None')] + [(i, str(i)) for i in range(1, 21)], 
                          coerce=int, default=0)
    submit = SubmitField('Save Project')

class MemberNoteForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('Content')
    submit = SubmitField('Save Note')

class MemberDevelopmentForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    submit = SubmitField('Save Development')

class TeamPriorityForm(FlaskForm):
    content = StringField('Priority', validators=[DataRequired(), Length(max=200)])
    color = SelectField('Color', choices=[
        ('#fff740', 'Yellow'),
        ('#ff7eb9', 'Pink'),
        ('#7afcff', 'Blue'),
        ('#8cff89', 'Green'),
        ('#ffa8a8', 'Red')
    ])
    submit = SubmitField('Add Priority')

class AdHocForm(FlaskForm):
    month = SelectField('Month', validators=[DataRequired()], choices=[])
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    completed_by = StringField('Completed By', validators=[DataRequired(), Length(max=100)])
    hours_needed = StringField('Hours Needed', validators=[DataRequired()])
    submit = SubmitField('Save')
    
    def __init__(self, *args, **kwargs):
        super(AdHocForm, self).__init__(*args, **kwargs)
        # Generate month choices for the current year and the past year
        current_year = datetime.utcnow().year
        months = []
        for year in range(current_year - 1, current_year + 1):
            for month in range(1, 13):
                month_name = datetime(year, month, 1).strftime('%B %Y')
                months.append((month_name, month_name))
        self.month.choices = months