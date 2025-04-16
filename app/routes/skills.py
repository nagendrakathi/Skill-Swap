from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app import db
from app.models import Skill, Request as SkillRequest
from app.forms import SkillForm

skills = Blueprint('skills', __name__)

@skills.route('/skills/browse')
def browse():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', None)
    search = request.args.get('search', None)
    
    # Base query
    query = Skill.query
    
    # Apply filters
    if category:
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(Skill.name.ilike(f'%{search}%') | 
                           Skill.description.ilike(f'%{search}%'))
    
    # Get all categories for the filter sidebar
    categories = db.session.query(Skill.category).distinct().all()
    categories = [category[0] for category in categories]
    
    # Paginate results
    skills = query.order_by(Skill.created_at.desc()).paginate(page=page, per_page=12)
    
    return render_template('skills/browse.html', title='Browse Skills',
                          skills=skills, categories=categories,
                          current_category=category, search=search)

@skills.route('/skills/add', methods=['GET', 'POST'])
@login_required
def add():
    form = SkillForm()
    if form.validate_on_submit():
        skill = Skill(
            name=form.name.data,
            description=form.description.data,
            category=form.category.data,
            difficulty=form.difficulty.data,
            owner_id=current_user.id
        )
        db.session.add(skill)
        db.session.commit()
        flash('Your skill has been added!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('skills/add.html', title='Add a Skill', form=form)

@skills.route('/skills/<int:skill_id>')
def detail(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    
    # Check if current user has already requested this skill
    has_requested = False
    if current_user.is_authenticated:
        request = SkillRequest.query.filter_by(
            requester_id=current_user.id,
            skill_id=skill_id
        ).first()
        has_requested = request is not None
    
    # Get request form if user is logged in
    form = None
    if current_user.is_authenticated and not has_requested and skill.owner_id != current_user.id:
        from app.forms import RequestForm
        form = RequestForm()
    
    return render_template('skills/detail.html', title=skill.name,
                          skill=skill, form=form, has_requested=has_requested)

@skills.route('/skills/<int:skill_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    
    # Check if current user is the owner
    if skill.owner_id != current_user.id:
        flash('You can only edit your own skills!', 'danger')
        return redirect(url_for('skills.detail', skill_id=skill_id))
    
    form = SkillForm()
    if form.validate_on_submit():
        skill.name = form.name.data
        skill.description = form.description.data
        skill.category = form.category.data
        skill.difficulty = form.difficulty.data
        db.session.commit()
        flash('Your skill has been updated!', 'success')
        return redirect(url_for('skills.detail', skill_id=skill_id))
    elif request.method == 'GET':
        form.name.data = skill.name
        form.description.data = skill.description
        form.category.data = skill.category
        form.difficulty.data = skill.difficulty
    
    return render_template('skills/edit.html', title='Edit Skill', form=form, skill=skill)

@skills.route('/skills/<int:skill_id>/delete', methods=['POST'])
@login_required
def delete(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    
    # Check if current user is the owner
    if skill.owner_id != current_user.id:
        flash('You can only delete your own skills!', 'danger')
        return redirect(url_for('skills.detail', skill_id=skill_id))
    
    # Delete any requests associated with this skill
    SkillRequest.query.filter_by(skill_id=skill_id).delete()
    
    # Delete the skill
    db.session.delete(skill)
    db.session.commit()
    
    flash('Your skill has been deleted!', 'success')
    return redirect(url_for('main.dashboard'))