# Add these functions to your routes.py file

@team.route('/task/<int:member_id>/add', methods=['POST'])
def add_member_task(member_id):
    member = TeamMember.query.get_or_404(member_id)
    form = MemberTaskForm()
    
    if form.validate_on_submit():
        task = MemberTask(
            content=form.content.data,
            member_id=member.id
        )
        
        # Handle due date if provided
        if hasattr(form, 'due_date') and form.due_date.data:
            task.due_date = form.due_date.data
            
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully!', 'success')
    
    return redirect(url_for('team.view_member', member_id=member.id))

@team.route('/task/<int:task_id>/delete', methods=['POST'])
def delete_member_task(task_id):
    task = MemberTask.query.get_or_404(task_id)
    member_id = task.member_id
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('team.view_member', member_id=member_id))

@team.route('/task/<int:task_id>/toggle', methods=['POST'])
def toggle_member_task(task_id):
    task = MemberTask.query.get_or_404(task_id)
    task.completed = not task.completed
    db.session.commit()
    return jsonify({'status': 'success', 'completed': task.completed})

@team.route('/project/<int:member_id>/add', methods=['POST'])
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
    
    return redirect(url_for('team.view_member', member_id=member.id))

@team.route('/project/<int:project_id>/delete', methods=['POST'])
def delete_member_project(project_id):
    project = MemberProject.query.get_or_404(project_id)
    member_id = project.member_id
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('team.all_members'))

@team.route('/note/<int:member_id>/add', methods=['POST'])
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

@team.route('/development/<int:member_id>/add', methods=['POST'])
def add_member_development(member_id):
    member = TeamMember.query.get_or_404(member_id)
    form = MemberDevelopmentForm()
    
    if form.validate_on_submit():
        development = MemberDevelopment(
            title=form.title.data,
            description=form.description.data,
            member_id=member.id
        )
        
        # Handle date if present
        if hasattr(form, 'date') and form.date.data:
            development.date = form.date.data
            
        db.session.add(development)
        db.session.commit()
        flash('Development record added successfully!', 'success')
    
    return redirect(url_for('team.all_members'))

@team.route('/development/<int:development_id>/delete', methods=['POST'])
def delete_member_development(development_id):
    development = MemberDevelopment.query.get_or_404(development_id)
    member_id = development.member_id
    db.session.delete(development)
    db.session.commit()
    flash('Development record deleted successfully!', 'success')
    return redirect(url_for('team.all_members'))