from flask import Blueprint, jsonify, request
from application.models import Reminder  # Import your existing Reminder model
from application.database import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import text
from tasks import  send_monthly_reports
# Create the blueprint
reminder_bp = Blueprint('reminder', __name__, url_prefix='/api/reminders')

@reminder_bp.route('/', methods=['GET'])
@jwt_required()
def get_reminder_preference():
    """Get the user's reminder preference (morning, afternoon, evening)"""
    username = get_jwt_identity()
    
    # Get user ID from username
    user_query = text("SELECT uid FROM user WHERE username = :username")
    user_result = db.session.execute(user_query, {"username": username}).fetchone()
    
    if not user_result:
        return jsonify({"error": "User not found"}), 404
    
    user_id = user_result[0]
    
    # Get current reminder preference
    reminder = Reminder.query.filter_by(uid=user_id).first()
    
    if reminder:
        return jsonify({
            "user_id": user_id,
            "reminder_preference": reminder.reminder
        })
    else:
        # Default preference if not set
        return jsonify({
            "user_id": user_id,
            "reminder_preference": "morning"  # Default
        })

@reminder_bp.route('/', methods=['POST'])
@jwt_required()
def set_reminder_preference():
    """Set or update the user's reminder preference"""
    username = get_jwt_identity()
    
    # Get user ID from username
    user_query = text("SELECT uid FROM user WHERE username = :username")
    user_result = db.session.execute(user_query, {"username": username}).fetchone()
    
    if not user_result:
        return jsonify({"error": "User not found"}), 404
    
    user_id = user_result[0]
    data = request.get_json()
    print(data)
    # Validate the reminder preference
    preference = data.get('reminder_preference')
    print(f"Received reminder preference: {preference}")
    if not preference or preference not in ['morning', 'afternoon', 'evening']:
        return jsonify({
            "error": "Invalid reminder preference. Must be 'morning', 'afternoon', or 'evening'"
        }), 400
    
    # Check if reminder preference already exists
    existing_reminder = Reminder.query.filter_by(uid=user_id).first()
    
    if existing_reminder:
        # Update existing preference
        existing_reminder.reminder = preference
    else:
        # Create new preference
        new_reminder = Reminder(uid=user_id, reminder=preference)
        db.session.add(new_reminder)
    
    db.session.commit()
    
    return jsonify({
        "message": "Reminder preference updated successfully",
        "user_id": user_id,
        "reminder_preference": preference
    }), 200

@reminder_bp.route('/', methods=['DELETE'])
@jwt_required()
def disable_reminders():
    """Disable reminders for the user by removing their preference"""
    username = get_jwt_identity()
    
    # Get user ID from username
    user_query = text("SELECT uid FROM user WHERE username = :username")
    user_result = db.session.execute(user_query, {"username": username}).fetchone()
    
    if not user_result:
        return jsonify({"error": "User not found"}), 404
    
    user_id = user_result[0]
    
    # Find the reminder preference
    reminder = Reminder.query.filter_by(uid=user_id).first()
    
    if reminder:
        db.session.delete(reminder)
        db.session.commit()
        return jsonify({"message": "Reminders disabled successfully"})
    else:
        return jsonify({"message": "No reminder preferences found to disable"})


@reminder_bp.route('/test/monthly', methods=['POST'])
def trigger_monthly_reports():
    """Admin endpoint to test monthly reports"""
    result = send_monthly_reports.delay()
    return jsonify({
        "status": "success",
        "message": "Monthly reports task queued", 
        "task_id": result.id
    }), 202