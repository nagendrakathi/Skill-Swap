from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from app import db
from app.models import Skill, Request as SkillRequest, User, Message
from app.forms import RequestForm, MessageForm

requests = Blueprint('requests', __name__)

@requests.route('/skills/<int:skill_id>/request', methods=['POST'])
@login_required
def request_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    
    # Check if user is trying to request their own skill
    if skill.owner_id == current_user.id:
        flash('You cannot request your own skill!', 'danger')
        return redirect(url_for('skills.detail', skill_id=skill_id))
    
    # Check if request already exists
    existing_request = SkillRequest.query.filter_by(
        requester_id=current_user.id,
        skill_id=skill_id
    ).first()
    
    if existing_request:
        flash('You have already requested this skill!', 'warning')
        return redirect(url_for('skills.detail', skill_id=skill_id))
    
    # Process the form
    form = RequestForm()
    if form.validate_on_submit():
        skill_request = SkillRequest(
            requester_id=current_user.id,
            skill_id=skill_id,
            skill_owner_id=skill.owner_id,
            message=form.message.data
        )
        db.session.add(skill_request)
        db.session.commit()
        flash('Your request has been sent!', 'success')
    
    return redirect(url_for('skills.detail', skill_id=skill_id))

@requests.route('/requests/manage')
@login_required
def manage():
    # Get all incoming requests for the user's skills
    incoming_requests = SkillRequest.query.filter_by(
        skill_owner_id=current_user.id
    ).order_by(SkillRequest.created_at.desc()).all()
    
    # Get all outgoing requests from the user
    outgoing_requests = SkillRequest.query.filter_by(
        requester_id=current_user.id
    ).order_by(SkillRequest.created_at.desc()).all()
    
    return render_template('requests/manage.html', title='Manage Requests',
                          incoming_requests=incoming_requests,
                          outgoing_requests=outgoing_requests)

@requests.route('/requests/<int:request_id>/accept', methods=['POST'])
@login_required
def accept(request_id):
    skill_request = SkillRequest.query.get_or_404(request_id)
    
    # Check if current user is the skill owner
    if skill_request.skill_owner_id != current_user.id:
        flash('You can only accept requests for your own skills!', 'danger')
        return redirect(url_for('requests.manage'))
    
    # Check if request is already processed
    if skill_request.status != 'pending':
        flash('This request has already been processed!', 'warning')
        return redirect(url_for('requests.manage'))
    
    # Accept the request
    skill_request.status = 'accepted'
    db.session.commit()
    
    # Add the skill to the requester's learning skills
    requester = User.query.get(skill_request.requester_id)
    skill = Skill.query.get(skill_request.skill_id)
    
    if skill not in requester.skills_learning:
        requester.skills_learning.append(skill)
        db.session.commit()
    
    flash('You have accepted the request!', 'success')
    return redirect(url_for('requests.manage'))

@requests.route('/requests/<int:request_id>/reject', methods=['POST'])
@login_required
def reject(request_id):
    skill_request = SkillRequest.query.get_or_404(request_id)
    
    # Check if current user is the skill owner
    if skill_request.skill_owner_id != current_user.id:
        flash('You can only reject requests for your own skills!', 'danger')
        return redirect(url_for('requests.manage'))
    
    # Check if request is already processed
    if skill_request.status != 'pending':
        flash('This request has already been processed!', 'warning')
        return redirect(url_for('requests.manage'))
    
    # Reject the request
    skill_request.status = 'rejected'
    db.session.commit()
    
    flash('You have rejected the request.', 'info')
    return redirect(url_for('requests.manage'))

@requests.route('/requests/<int:request_id>/message', methods=['GET', 'POST'])
@login_required
def message(request_id):
    skill_request = SkillRequest.query.get_or_404(request_id)
    
    # Check if current user is part of this request
    if skill_request.requester_id != current_user.id and skill_request.skill_owner_id != current_user.id:
        flash('You are not authorized to view this conversation!', 'danger')
        return redirect(url_for('requests.manage'))
    
    # Get the other user
    other_user_id = skill_request.requester_id if current_user.id == skill_request.skill_owner_id else skill_request.skill_owner_id
    other_user = User.query.get(other_user_id)
    
    # Get existing messages
    messages = Message.query.filter_by(request_id=request_id).order_by(Message.timestamp).all()
    
    # Mark messages as read
    for msg in messages:
        if msg.receiver_id == current_user.id and not msg.read:
            msg.read = True
    
    db.session.commit()
    
    # Process new message form
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(
            content=form.content.data,
            sender_id=current_user.id,
            receiver_id=other_user_id,
            request_id=request_id
        )
        db.session.add(message)
        db.session.commit()
        flash('Message sent!', 'success')
        return redirect(url_for('requests.message', request_id=request_id))
    
    return render_template('requests/message.html', title='Messages',
                          request=skill_request, other_user=other_user,
                          messages=messages, form=form)

@requests.route('/requests/<int:request_id>/cancel', methods=['POST'])
@login_required
def cancel(request_id):
    skill_request = SkillRequest.query.get_or_404(request_id)
    
    # Check if current user is the requester
    if skill_request.requester_id != current_user.id:
        flash('You can only cancel your own requests!', 'danger')
        return redirect(url_for('requests.manage'))
    
    # Delete the request
    db.session.delete(skill_request)
    db.session