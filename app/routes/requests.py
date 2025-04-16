from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from app import db
from app.models import Request as SkillRequest, Message, Skill, User
from app.forms import RequestForm, MessageForm, ReviewForm

requests = Blueprint('requests', __name__)

@requests.route('/requests/send/<int:skill_id>', methods=['POST'])
@login_required
def send_request(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    
    # Check if user is not the owner
    if skill.owner_id == current_user.id:
        flash("You can't request your own skill!", 'danger')
        return redirect(url_for('skills.detail', skill_id=skill_id))
    
    # Check if there's an existing request
    existing_request = SkillRequest.query.filter_by(
        requester_id=current_user.id,
        skill_id=skill_id
    ).first()
    
    if existing_request:
        flash('You have already requested this skill.', 'warning')
        return redirect(url_for('skills.detail', skill_id=skill_id))
    
    # Create new request
    form = RequestForm()
    if form.validate_on_submit():
        new_request = SkillRequest(
            requester_id=current_user.id,
            skill_id=skill_id,
            skill_owner_id=skill.owner_id,
            message=form.message.data
        )
        db.session.add(new_request)
        db.session.commit()
        
        flash('Your request has been sent!', 'success')
        return redirect(url_for('skills.detail', skill_id=skill_id))
    
    flash('There was an error with your request.', 'danger')
    return redirect(url_for('skills.detail', skill_id=skill_id))

@requests.route('/requests/manage')
@login_required
def manage():
    # Get requests received
    requests_received = SkillRequest.query.filter_by(
        skill_owner_id=current_user.id
    ).order_by(SkillRequest.created_at.desc()).all()
    
    # Get requests sent
    requests_sent = SkillRequest.query.filter_by(
        requester_id=current_user.id
    ).order_by(SkillRequest.created_at.desc()).all()
    
    return render_template('requests/manage.html', title='Manage Requests',
                          requests_received=requests_received,
                          requests_sent=requests_sent)

@requests.route('/requests/<int:request_id>/accept', methods=['POST'])
@login_required
def accept_request(request_id):
    skill_request = SkillRequest.query.get_or_404(request_id)
    
    # Check if current user is the skill owner
    if skill_request.skill_owner_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('requests.manage'))
    
    skill_request.status = 'accepted'
    db.session.commit()
    
    # Add the requester to the list of learners for this skill
    requester = User.query.get(skill_request.requester_id)
    if requester not in skill_request.skill.learners:
        skill_request.skill.learners.append(requester)
        db.session.commit()
    
    # Send a notification message
    message = Message(
        content=f"Your request to learn {skill_request.skill.name} has been accepted! You can now start learning.",
        sender_id=current_user.id,
        receiver_id=skill_request.requester_id,
        request_id=request_id
    )
    db.session.add(message)
    db.session.commit()
    
    flash('Request accepted!', 'success')
    return redirect(url_for('requests.manage'))

@requests.route('/requests/<int:request_id>/reject', methods=['POST'])
@login_required
def reject_request(request_id):
    skill_request = SkillRequest.query.get_or_404(request_id)
    
    # Check if current user is the skill owner
    if skill_request.skill_owner_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('requests.manage'))
    
    skill_request.status = 'rejected'
    db.session.commit()
    
    # Send a notification message
    message = Message(
        content=f"Your request to learn {skill_request.skill.name} has been declined.",
        sender_id=current_user.id,
        receiver_id=skill_request.requester_id,
        request_id=request_id
    )
    db.session.add(message)
    db.session.commit()
    
    flash('Request rejected.', 'info')
    return redirect(url_for('requests.manage'))

@requests.route('/requests/<int:request_id>/messages', methods=['GET', 'POST'])
@login_required
def messages(request_id):
    skill_request = SkillRequest.query.get_or_404(request_id)
    
    # Check if current user is either the requester or skill owner
    if skill_request.requester_id != current_user.id and skill_request.skill_owner_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('requests.manage'))
    
    form = MessageForm()
    if form.validate_on_submit():
        # Determine receiver ID (the other person in the conversation)
        receiver_id = skill_request.requester_id if current_user.id == skill_request.skill_owner_id else skill_request.skill_owner_id
        
        message = Message(
            content=form.content.data,
            sender_id=current_user.id,
            receiver_id=receiver_id,
            request_id=request_id
        )
        db.session.add(message)
        db.session.commit()
        
        flash('Message sent!', 'success')
        return redirect(url_for('requests.messages', request_id=request_id))
    
    # Get all messages for this request
    messages = Message.query.filter_by(request_id=request_id).order_by(Message.timestamp).all()
    
    # Mark unread messages as read
    unread_messages = Message.query.filter_by(
        request_id=request_id, 
        receiver_id=current_user.id,
        read=False
    ).all()
    
    for message in unread_messages:
        message.read = True
    
    db.session.commit()
    
    return render_template('requests/messages.html', title='Messages',
                          request=skill_request,
                          messages=messages,
                          form=form)

@requests.route('/requests/<int:request_id>/review', methods=['GET', 'POST'])
@login_required
def review(request_id):
    skill_request = SkillRequest.query.get_or_404(request_id)
    
    # Check if current user is the requester and request is accepted
    if skill_request.requester_id != current_user.id or skill_request.status != 'accepted':
        flash('You can only review skills you have learned.', 'danger')
        return redirect(url_for('requests.manage'))
    
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            rating=form.rating.data,
            comment=form.comment.data,
            reviewer_id=current_user.id,
            reviewee_id=skill_request.skill_owner_id,
            skill_id=skill_request.skill_id
        )
        db.session.add(review)
        db.session.commit()
        
        flash('Thank you for your review!', 'success')
        return redirect(url_for('requests.manage'))
    
    return render_template('requests/review.html', title='Review',
                          request=skill_request,
                          form=form)

@requests.route('/api/notifications')
@login_required
def get_notifications():
    # Count pending requests
    pending_requests = SkillRequest.query.filter_by(
        skill_owner_id=current_user.id,
        status='pending'
    ).count()
    
    # Count unread messages
    unread_messages = Message.query.filter_by(
        receiver_id=current_user.id,
        read=False
    ).count()
    
    return jsonify({
        'pending_requests': pending_requests,
        'unread_messages': unread_messages
    })