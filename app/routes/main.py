from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from app.models import Skill, Request, User
from sqlalchemy import func

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Get some stats for the homepage
    skill_count = Skill.query.count()
    user_count = User.query.count()
    top_categories = db.session.query(
        Skill.category, func.count(Skill.id).label('count')
    ).group_by(Skill.category).order_by(func.count(Skill.id).desc()).limit(5).all()
    
    return render_template('index.html', title='Home', 
                          skill_count=skill_count, 
                          user_count=user_count,
                          top_categories=top_categories)

@main.route('/dashboard')
@login_required
def dashboard():
    # Get skills the user offers
    my_skills = Skill.query.filter_by(owner_id=current_user.id).all()
    
    # Get pending requests for the user's skills
    pending_requests = Request.query.filter_by(
        skill_owner_id=current_user.id, 
        status='pending'
    ).order_by(Request.created_at.desc()).all()
    
    # Get requests the user has sent
    my_requests = Request.query.filter_by(
        requester_id=current_user.id
    ).order_by(Request.created_at.desc()).all()
    
    # Get some recommended skills based on categories the user has shown interest in
    # (This is a simple recommendation system)
    user_interests = db.session.query(Skill.category).join(Request, Request.skill_id == Skill.id)\
                    .filter(Request.requester_id == current_user.id).distinct().all()
    interest_categories = [interest[0] for interest in user_interests]
    
    recommended_skills = []
    if interest_categories:
        recommended_skills = Skill.query.filter(
            Skill.category.in_(interest_categories),
            Skill.owner_id != current_user.id
        ).order_by(func.random()).limit(5).all()
    
    return render_template('dashboard.html', title='Dashboard',
                          my_skills=my_skills,
                          pending_requests=pending_requests,
                          my_requests=my_requests,
                          recommended_skills=recommended_skills)

@main.route('/about')
def about():
    return render_template('about.html', title='About SkillSwap')