from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from application.models import User, Subjects, Chapters, Questions, Options, QuizDetails, Scores, QuizResponse, File, Viewed, Reminder
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from flask import current_app
import logging
from .database import db

logger = logging.getLogger(__name__)

def setup_reminder_scheduler(app):
    """Set up the scheduled reminders for quizzes"""
    scheduler = BackgroundScheduler()
    
    # Schedule jobs for different times of the day
    scheduler.add_job(
        func=send_morning_reminders,
        trigger=CronTrigger(hour=8, minute=0),  # 8:00 AM
        args=[app],
        id='morning_reminders',
        name='Send morning reminders to users',
        replace_existing=True
    )
    
    scheduler.add_job(
        func=send_afternoon_reminders,
        trigger=CronTrigger(hour=13, minute=0),  # 1:00 PM
        args=[app],
        id='afternoon_reminders',
        name='Send aftern   oon reminders to users',
        replace_existing=True
    )
    
    scheduler.add_job(
        func=send_evening_reminders,
        trigger=CronTrigger(hour=19, minute=0),  # 7:00 PM
        args=[app],
        id='evening_reminders',
        name='Send evening reminders to users',
        replace_existing=True
    )
    
    scheduler.start()
    app.scheduler = scheduler  # Store scheduler instance in app
    
    return scheduler

def send_morning_reminders(app):
    """Send reminders to users who prefer morning reminders"""
    with app.app_context():
        _send_reminders_to_users('morning')

def send_afternoon_reminders(app):
    """Send reminders to users who prefer afternoon reminders"""
    with app.app_context():
        _send_reminders_to_users('afternoon')

def send_evening_reminders(app):
    """Send reminders to users who prefer evening reminders"""
    with app.app_context():
        _send_reminders_to_users('evening')

def _send_reminders_to_users(time_of_day):
    """Helper function to send reminders to users based on time preference"""
    try:
        # Get all users who prefer reminders at this time
        users_with_reminder_pref = db.session.query(User, Reminder).join(
            Reminder, User.uid == Reminder.uid
        ).filter(Reminder.reminder == time_of_day).all()
        
        if not users_with_reminder_pref:
            logger.info(f"No users with {time_of_day} reminder preference found")
            return
        
        # Get all quizzes
        quizzes = QuizDetails.query.all()
        
        # For each user, check for unviewed quizzes
        for user, reminder in users_with_reminder_pref:
            # Find quizzes the user hasn't viewed
            unviewed_quizzes = []
            
            for quiz in quizzes:
                # Check if the user has viewed this quiz
                viewed = Viewed.query.filter_by(
                    uid=user.uid, 
                    quizid=quiz.quizid
                ).first()
                
                # If not viewed or viewed is 0, add to unviewed
                if not viewed or viewed.viewed == 0:
                    unviewed_quizzes.append(quiz)
            
            # If there are unviewed quizzes, send a reminder
            if unviewed_quizzes:
                send_reminder_to_user(user, unviewed_quizzes, time_of_day)
                
    except Exception as e:
        logger.error(f"Error sending {time_of_day} reminders: {str(e)}")

def send_reminder_to_user(user, unviewed_quizzes, time_of_day):
    """Send a reminder to a specific user about unviewed quizzes"""
    try:
        # Build message content
        quiz_count = len(unviewed_quizzes)
        quiz_titles = [quiz.quizname for quiz in unviewed_quizzes[:3]]  # List first 3 quizzes
        
        subject = f"You have {quiz_count} unviewed quiz{'es' if quiz_count > 1 else ''}"
        
        message_content = f"""
        <html>
        <body>
            <h2>Quiz Reminder</h2>
            <p>Hello {user.fullname},</p>
            <p>You have {quiz_count} unviewed quiz{'es' if quiz_count > 1 else ''} waiting for you:</p>
        """
        
        # Add quiz list
        if quiz_count > 0:
            message_content += "<ul>"
            for title in quiz_titles:
                message_content += f"<li>{title}</li>"
            if quiz_count > 3:
                message_content += f"<li>...and {quiz_count - 3} more</li>"
            message_content += "</ul>"
        
        message_content += """
            <p>Login to view and attempt these quizzes.</p>
            <p>Thank you!</p>
        </body>
        </html>
        """
        
        # Send email
        send_email(user.email, subject, message_content)
        
        logger.info(f"Reminder sent to user {user.uid} ({user.email}) for {quiz_count} quizzes")
        
    except Exception as e:
        logger.error(f"Error sending reminder to user {user.uid}: {str(e)}")

def send_email(to_email, subject, html_content):
    """Send an email using Flask-Mail"""
    try:
        from flask_mail import Message
        from flask import current_app as app
        
        msg = Message(
            subject=subject,
            recipients=[to_email],
            html=html_content
        )
        
        mail = app.extensions.get('mail')
        if mail:
            mail.send(msg)
            return True
        else:
            logger.error("Mail extension not found in app")
            return False
            
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False