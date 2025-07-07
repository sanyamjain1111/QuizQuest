from flask import current_app, render_template_string
from flask_mail import Mail, Message
from application.models import User, Scores, QuizDetails, Subjects, Chapters, Admin
from sqlalchemy import func
import csv
import os
from datetime import datetime, timedelta
import pandas as pd
from celery_app import redis_client
from application.database import db

# Import your celery instance - adjust the import path as needed
from celery_app import celery  # or wherever your celery instance is defined


@celery.task(bind=True)
def send_reminder_email(self, user_id, new_quiz_count):
    """Send individual reminder email to user."""
    try:
        with current_app.app_context():
            user = User.query.get(user_id)
            if not user:
                return
                
            mail = Mail(current_app)
            
            # Email template
            email_template = """
            <html>
            <body>
                <h2>Quiz Master - Daily Reminder</h2>
                <p>Hello {{ user.fullname }},</p>
                <p>We hope you're doing well! This is a friendly reminder to visit Quiz Master.</p>
                {% if new_quiz_count > 0 %}
                <p><strong>{{ new_quiz_count }} new quiz(s)</strong> have been added that might interest you.</p>
                {% endif %}
                <p>Take a moment to challenge yourself and improve your knowledge!</p>
                <p><a href="http://localhost:8080/login">Visit Quiz Master</a></p>
                <p>Best regards,<br>Quiz Master Team</p>
            </body>
            </html>
            """
            
            html_content = render_template_string(email_template, user=user, new_quiz_count=new_quiz_count)
            
            msg = Message(
                subject="Quiz Master - Daily Reminder",
                recipients=[user.username],  # Assuming username is email
                html=html_content
            )
            mail.send(msg)
        
    except Exception as e:
        current_app.logger.error(f"Error sending reminder email to user {user_id}: {str(e)}")
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery.task(bind=True)
def send_monthly_reports(self):
    """Send monthly activity reports to all users."""
    try:
        # Get all users
        users = User.query.all()
        
        for user in users:
            generate_monthly_report.delay(user.uid)
            
    except Exception as e:
        current_app.logger.error(f"Error in send_monthly_reports: {str(e)}")
        raise self.retry(exc=e, countdown=60, max_retries=3)
import calendar
@celery.task(bind=True)
def generate_monthly_report(self, user_id):
    """Generate and send monthly report for a specific user."""
    try:
        with current_app.app_context():
            user = User.query.get(user_id)
            if not user:
                return
                
            # Get last month's date range
            now = datetime.utcnow()
            last_month = now.replace(day=1) - timedelta(days=1)
            first_day_last_month = last_month.replace(day=1)
            last_day_last_month = last_month.replace(day=calendar.monthrange(last_month.year, last_month.month)[1])
            
            # Format dates to match your quiz_date format (assuming it's stored as string)
            first_day_str = first_day_last_month.strftime('%Y-%m-%d')
            last_day_str = last_day_last_month.strftime('%Y-%m-%d')
            
            # Query user's quiz attempts from last month using nested query
            # First get quiz IDs from last month
            last_month_quiz_ids = db.session.query(QuizDetails.quizid).filter(
                QuizDetails.quiz_date >= first_day_str,
                QuizDetails.quiz_date <= last_day_str
            ).subquery()
            
            # Then get scores for this user for those quizzes
            monthly_scores = Scores.query.filter(
                Scores.uid == user_id,
                Scores.quiz_id.in_(db.session.query(last_month_quiz_ids.c.quizid))
            ).all()
            
            if not monthly_scores:
                return  # No activity last month
                
            # Calculate statistics - Fix: Ensure all values are numeric
            total_quizzes = len(monthly_scores)
            
            # Fix: Convert scores to int if they're strings, handle None values
            valid_scores = []
            valid_totals = []
            
            for score in monthly_scores:
                if score.score is not None:
                    try:
                        valid_scores.append(int(score.score))
                    except (ValueError, TypeError):
                        pass  # Skip invalid scores
                        
                if score.total is not None:
                    try:
                        valid_totals.append(int(score.total))
                    except (ValueError, TypeError):
                        pass  # Skip invalid totals
            
            total_score = sum(valid_scores)
            total_possible = sum(valid_totals)
            average_score = (total_score / total_possible * 100) if total_possible > 0 else 0
            
            # Get ranking (rank by average percentage score)
            # Get all users' scores for last month quizzes
            all_users_scores = db.session.query(
                Scores.uid,
                func.sum(Scores.score).label('total_score'),
                func.sum(Scores.total).label('total_possible')
            ).filter(
                Scores.quiz_id.in_(db.session.query(last_month_quiz_ids.c.quizid))
            ).group_by(Scores.uid).all()
            
            # Calculate percentage and sort
            user_rankings = []
            for user_score in all_users_scores:
                if user_score.total_possible and user_score.total_possible > 0:
                    try:
                        total_score_val = int(user_score.total_score) if user_score.total_score else 0
                        total_possible_val = int(user_score.total_possible) if user_score.total_possible else 0
                        if total_possible_val > 0:
                            percentage = (total_score_val / total_possible_val) * 100
                            user_rankings.append({
                                'uid': user_score.uid,
                                'percentage': percentage
                            })
                    except (ValueError, TypeError):
                        continue  # Skip invalid data
            
            # Sort by percentage (descending) and find user's rank
            user_rankings.sort(key=lambda x: x['percentage'], reverse=True)
            user_rank = next((i+1 for i, u in enumerate(user_rankings) if u['uid'] == user_id), 0)
            
            # Get additional statistics
            best_score = max(valid_scores) if valid_scores else 0
            
            # Fix: Handle time_stamp conversion (assuming it should be numeric)
            total_time_spent = 0
            for score in monthly_scores:
                if score.time_stamp:
                    try:
                        # Try to convert string to float/int
                        time_val = float(score.time_stamp)
                        total_time_spent += time_val
                    except (ValueError, TypeError):
                        # If it's not a number, skip it or handle differently
                        # You might need to parse a time format here
                        pass
            
            # Get subject-wise performance
            subject_performance = db.session.query(
                Subjects.subject_name,
                func.sum(Scores.score).label('subject_score'),
                func.sum(Scores.total).label('subject_total')
            ).join(
                Chapters, Subjects.subject_id == Chapters.subject_id
            ).join(
                QuizDetails, Chapters.chaoter_id == QuizDetails.chapter_id  # Note: using the typo as it exists in your model
            ).join(
                Scores, QuizDetails.quizid == Scores.quiz_id
            ).filter(
                Scores.uid == user_id,
                QuizDetails.quiz_date >= first_day_str,
                QuizDetails.quiz_date <= last_day_str
            ).group_by(Subjects.subject_name).all()
            print("hello")
            # Generate HTML report with all statistics
            html_report = generate_report_html(
                user=user, 
                monthly_scores=monthly_scores, 
                total_quizzes=total_quizzes, 
                average_score=average_score,
                rank=user_rank,
                best_score=best_score,
                total_time_spent=total_time_spent,
                subject_performance=subject_performance,
                month_name=last_month.strftime('%B %Y')
            )
            
            # Send email
            mail = Mail(current_app)
            msg = Message(
                subject=f"Quiz Master - Monthly Report for {last_month.strftime('%B %Y')}",
                recipients=[user.username],  # Assuming username is email
                html=html_report
            )
            mail.send(msg)
        
    except Exception as e:
        current_app.logger.error(f"Error generating monthly report for user {user_id}: {str(e)}")
        raise self.retry(exc=e, countdown=60, max_retries=3)
def generate_report_html(user, monthly_scores, total_quizzes, average_score, rank, best_score=0, total_time_spent=0, subject_performance=None, month_name=""):
    """Generate beautiful HTML content for monthly report."""
    
    # Calculate additional stats
    if subject_performance is None:
        subject_performance = []
    
    # Pre-process scores to convert time_stamp to numeric values
    processed_scores = []
    for score in monthly_scores:
        processed_score = {
            'quiz_id': score.quiz_id,
            'score': score.score or 0,
            'total': score.total or 0,
            'time_stamp_numeric': 0,  # Default to 0
            'time_mins': 0,
            'time_secs': 0
        }
        
        # Convert time_stamp to numeric
        if score.time_stamp:
            try:
                time_numeric = float(score.time_stamp)
                processed_score['time_stamp_numeric'] = time_numeric
                processed_score['time_mins'] = int(time_numeric // 60)
                processed_score['time_secs'] = int(time_numeric % 60)
            except (ValueError, TypeError):
                # If conversion fails, keep defaults (0)
                pass
        
        processed_scores.append(processed_score)
    
    # Format time spent (convert seconds to hours and minutes)
    hours = int(total_time_spent // 3600)
    minutes = int((total_time_spent % 3600) // 60)
    time_formatted = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
    
    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Quiz Master - Monthly Report</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #2c3e50;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
                position: relative;
            }
            
            .header::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="50" r="1" fill="white" opacity="0.1"/><circle cx="25" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>') repeat;
                opacity: 0.3;
            }
            
            .header-content {
                position: relative;
                z-index: 1;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                font-weight: 700;
                text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .header h2 {
                font-size: 1.5em;
                margin-bottom: 15px;
                font-weight: 400;
                opacity: 0.9;
            }
            
            .month-badge {
                display: inline-block;
                background: rgba(255,255,255,0.2);
                padding: 8px 20px;
                border-radius: 25px;
                font-size: 1em;
                font-weight: 500;
                margin-top: 10px;
                backdrop-filter: blur(10px);
            }
            
            .content {
                padding: 40px 30px;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }
            
            .stat-card {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                padding: 25px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 8px 25px rgba(240, 147, 251, 0.3);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            
            .stat-card:nth-child(2) {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                box-shadow: 0 8px 25px rgba(79, 172, 254, 0.3);
            }
            
            .stat-card:nth-child(3) {
                background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
                box-shadow: 0 8px 25px rgba(67, 233, 123, 0.3);
            }
            
            .stat-card:nth-child(4) {
                background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
                box-shadow: 0 8px 25px rgba(250, 112, 154, 0.3);
            }
            
            .stat-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            }
            
            .stat-value {
                font-size: 2.5em;
                font-weight: 700;
                margin-bottom: 5px;
                text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .stat-label {
                font-size: 0.9em;
                opacity: 0.9;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .section {
                margin-bottom: 40px;
            }
            
            .section-title {
                font-size: 1.8em;
                font-weight: 600;
                margin-bottom: 20px;
                color: #2c3e50;
                position: relative;
                padding-bottom: 10px;
            }
            
            .section-title::after {
                content: '';
                position: absolute;
                bottom: 0;
                left: 0;
                width: 50px;
                height: 3px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 2px;
            }
            
            .quiz-table {
                width: 100%;
                border-collapse: collapse;
                background: white;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            }
            
            .quiz-table th {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px;
                font-weight: 600;
                text-align: left;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .quiz-table td {
                padding: 15px;
                border-bottom: 1px solid #f1f3f4;
                transition: background-color 0.2s ease;
            }
            
            .quiz-table tbody tr:hover {
                background-color: #f8f9ff;
            }
            
            .quiz-table tbody tr:last-child td {
                border-bottom: none;
            }
            
            .score-badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-weight: 600;
                font-size: 0.8em;
            }
            
            .score-excellent { background: #d4edda; color: #155724; }
            .score-good { background: #cce7ff; color: #004085; }
            .score-average { background: #fff3cd; color: #856404; }
            .score-poor { background: #f8d7da; color: #721c24; }
            
            .subject-performance {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            
            .subject-card {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }
            
            .subject-name {
                font-weight: 600;
                font-size: 1.1em;
                margin-bottom: 10px;
                color: #2c3e50;
            }
            
            .subject-score {
                font-size: 1.5em;
                font-weight: 700;
                color: #667eea;
            }
            
            .progress-bar {
                width: 100%;
                height: 8px;
                background: #e9ecef;
                border-radius: 4px;
                margin-top: 10px;
                overflow: hidden;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 4px;
                transition: width 0.3s ease;
            }
            
            .footer {
                background: #f8f9fa;
                padding: 30px;
                text-align: center;
                border-top: 1px solid #e9ecef;
            }
            
            .cta-button {
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 25px;
                font-weight: 600;
                font-size: 1.1em;
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
                transition: all 0.3s ease;
            }
            
            .cta-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
                text-decoration: none;
            }
            
            .emoji {
                font-size: 1.2em;
                margin-right: 8px;
            }
            
            @media (max-width: 600px) {
                .container {
                    margin: 10px;
                    border-radius: 15px;
                }
                
                .header {
                    padding: 30px 20px;
                }
                
                .header h1 {
                    font-size: 2em;
                }
                
                .content {
                    padding: 30px 20px;
                }
                
                .stats-grid {
                    grid-template-columns: repeat(2, 1fr);
                    gap: 15px;
                }
                
                .stat-value {
                    font-size: 2em;
                }
                
                .quiz-table {
                    font-size: 0.9em;
                }
                
                .quiz-table th,
                .quiz-table td {
                    padding: 10px 8px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="header-content">
                    <h1><span class="emoji">📊</span>Quiz Master Report</h1>
                    <h2>Hello {{ user.fullname }}!</h2>
                    <p>Here's your amazing progress for</p>
                    <div class="month-badge">{{ month_name or "Last Month" }}</div>
                </div>
            </div>
            
            <div class="content">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">{{ total_quizzes }}</div>
                        <div class="stat-label"><span class="emoji">🎯</span>Quizzes Taken</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{{ "%.1f"|format(average_score) }}%</div>
                        <div class="stat-label"><span class="emoji">📈</span>Average Score</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">#{{ rank }}</div>
                        <div class="stat-label"><span class="emoji">🏆</span>Your Rank</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{{ time_formatted }}</div>
                        <div class="stat-label"><span class="emoji">⏱️</span>Time Spent</div>
                    </div>
                </div>
                
                {% if subject_performance %}
                <div class="section">
                    <h3 class="section-title"><span class="emoji">📚</span>Subject Performance</h3>
                    <div class="subject-performance">
                        {% for subject in subject_performance %}
                        {% set percentage = (subject.subject_score / subject.subject_total * 100) if subject.subject_total > 0 else 0 %}
                        <div class="subject-card">
                            <div class="subject-name">{{ subject.subject_name }}</div>
                            <div class="subject-score">{{ "%.1f"|format(percentage) }}%</div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {{ percentage }}%"></div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endif %}
                
                <div class="section">
                    <h3 class="section-title"><span class="emoji">📝</span>Quiz Details</h3>
                    <table class="quiz-table">
                        <thead>
                            <tr>
                                <th>Quiz ID</th>
                                <th>Score</th>
                                <th>Percentage</th>
                                <th>Time Taken</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for score in processed_scores %}
                            {% set percentage = (score.score / score.total * 100) if score.total > 0 else 0 %}
                            <tr>
                                <td><strong>Quiz #{{ score.quiz_id }}</strong></td>
                                <td>{{ score.score }}/{{ score.total }}</td>
                                <td>
                                    <span class="score-badge 
                                        {% if percentage >= 90 %}score-excellent
                                        {% elif percentage >= 70 %}score-good
                                        {% elif percentage >= 50 %}score-average
                                        {% else %}score-poor{% endif %}">
                                        {{ "%.1f"|format(percentage) }}%
                                    </span>
                                </td>
                                <td>{{ score.time_mins }}m {{ score.time_secs }}s</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="footer">
                <p style="margin-bottom: 20px; font-size: 1.1em; color: #6c757d;">
                    <span class="emoji">🚀</span>Keep pushing your limits and reaching new heights!
                </p>
                <a href="http://localhost:8080" class="cta-button">
                    <span class="emoji">🎓</span>Continue Learning
                </a>
            </div>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(template, 
                                 user=user, 
                                 processed_scores=processed_scores, 
                                 total_quizzes=total_quizzes, 
                                 average_score=average_score, 
                                 rank=rank,
                                 best_score=best_score,
                                 total_time_spent=total_time_spent,
                                 time_formatted=time_formatted,
                                 subject_performance=subject_performance,
                                 month_name=month_name)
@celery.task(bind=True)
def export_user_quiz_data(self, user_id):
    """Export user's quiz data to CSV (Option C.1)."""
    try:
        with current_app.app_context():
            user = User.query.get(user_id)
            if not user:
                return {"status": "error", "message": "User not found"}
                
            # Get user's quiz attempts
            scores = Scores.query.filter_by(uid=user_id).all()
            print(f"Found {len(scores)} quiz attempts for user {user_id}")
            
            # Prepare data for CSV
            csv_data = []
            for score in scores:
                
                quiz = QuizDetails.query.filter_by(quizid=score.quiz_id).first()
                chapter= Chapters.query.filter_by(chaoter_id=quiz.chapter_id).first()
                subjects = Subjects.query.filter_by(subject_id=chapter.subject_id).first() if chapter else None

                
                csv_data.append({
                    'quiz_id': quiz.quizid,
                    'subject_name': subjects.subject_name,
                    'chapter_name': chapter.chapter_name,
                    'chapter_id': chapter.chaoter_id,
                    'date_of_quiz': quiz.quiz_date,
                    'time_duration': quiz.duration,
                    'score': score.score,
                    'time_taken': (score.time_stamp) + " seconds",
                    'remarks': "Excellent" if score.score >= 8 else "Good" if score.score >= 5 else "Needs Improvement"
                })
            
            # Create CSV file with simple timestamp (matching admin function style)
            import time
            timestamp = int(time.time())
            filename = f"user_{user_id}_quiz_data_{timestamp}.csv"
            filepath = os.path.join('exports', filename)
            os.makedirs('exports', exist_ok=True)
            
            df = pd.DataFrame(csv_data)
            df.to_csv(filepath, index=False)
            
            # Send notification email with CSV attachment
            send_export_notification.delay(user.username, filename, filepath, 'user')
            
            return {"status": "success", "filename": filename}
        
    except Exception as e:
        current_app.logger.error(f"Error exporting user quiz data: {str(e)}")
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery.task(bind=True)
def export_admin_users_data(self):
    """Export all users' performance data to CSV (Option C.2)."""
    try:
        with current_app.app_context():
            # Get all users with their quiz statistics
            users_data = []
            users = User.query.all()
            print(users)
            for user in users:
                scores = Scores.query.filter_by(uid=user.uid).all()
                
                if scores:
                    total_quizzes = len(scores)
                    average_score = sum(score1.score for score1 in scores) / total_quizzes
                    last_quiz_date = max(score1.time_stamp for score1 in scores)
                else:
                    total_quizzes = 0
                    average_score = 0
                    last_quiz_date = None
                
                users_data.append({
                    'user_id': user.uid,
                    'username': user.username,
                    'full_name': user.fullname,
                    'qualification': user.qualification,
                    'total_quizzes_taken': total_quizzes,
                    'average_score': round(average_score, 2),
                    'registration_date': user.uid  # Adjust this field as needed
                })
            
            # Create CSV file
            import time

# Simple timestamp
            timestamp = int(time.time())
            filename = f"admin_users_performance_{timestamp}.csv"
            filepath = os.path.join('exports', filename)
            os.makedirs('exports', exist_ok=True)
            
            df = pd.DataFrame(users_data)
            df.to_csv(filepath, index=False)
            
            # Get admin user (assuming admin has a specific identifier)
            admin = "jain78790@gmail.com"  # Adjust as needed
            if admin:
                send_export_notification.delay(admin, filename, filepath, 'admin')
            
            return {"status": "success", "filename": filename}
        
    except Exception as e:
        current_app.logger.error(f"Error exporting admin users data: {str(e)}")
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery.task(bind=True)
def send_export_notification(self, email, filename, filepath, export_type):
    """Send notification when CSV export is complete."""
    try:
        with current_app.app_context():
            mail = Mail(current_app)

            subject = f"Quiz Master - {'User Quiz Data' if export_type == 'user' else 'Users Performance Data'} Export Complete"

            # Compose the message
            msg = Message(
                subject=subject,
                recipients=[email],  # ← make sure this is a list
                body=f"Your export has been completed successfully. Please find the attached CSV file: {filename}"
            )

            # Attach the CSV file
            with open(filepath, 'rb') as f:
                msg.attach(
                    filename=filename,
                    content_type='text/csv',
                    data=f.read()
                )

            # Send the email
            mail.send(msg)

            # Remove the file after sending
            os.remove(filepath)

    except Exception as e:
        current_app.logger.error(f"Error sending export notification: {str(e)}")
        raise self.retry(exc=e, countdown=60, max_retries=3)

# Cache helper functions
def get_cached_data(key):
    """Get data from Redis cache."""
    try:
        data = redis_client.get(key)
        if data:
            import json
            return json.loads(data)
        return None
    except Exception as e:
        current_app.logger.error(f"Error getting cached data: {str(e)}")
        return None

def set_cached_data(key, data, timeout=300):
    """Set data in Redis cache."""
    try:
        import json
        redis_client.setex(key, timeout, json.dumps(data))
        return True
    except Exception as e:
        current_app.logger.error(f"Error setting cached data: {str(e)}")
        return False

def delete_cached_data(key):
    """Delete data from Redis cache."""
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        current_app.logger.error(f"Error deleting cached data: {str(e)}")
        return False
@celery.task(bind=True)
def send_morning_reminders(self):
    """Send morning reminders to users who prefer morning reminders"""
    try:
        with current_app.app_context():
            _send_reminders_by_preference('morning')
    except Exception as e:
        current_app.logger.error(f"Error in send_morning_reminders: {str(e)}")
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery.task(bind=True)
def send_afternoon_reminders(self):
    """Send afternoon reminders to users who prefer afternoon reminders"""
    try:
        with current_app.app_context():
            _send_reminders_by_preference('afternoon')
    except Exception as e:
        current_app.logger.error(f"Error in send_afternoon_reminders: {str(e)}")
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery.task(bind=True)
def send_evening_reminders(self):
    """Send evening reminders to users who prefer evening reminders"""
    try:
        with current_app.app_context():
            _send_reminders_by_preference('evening')
    except Exception as e:
        current_app.logger.error(f"Error in send_evening_reminders: {str(e)}")
        raise self.retry(exc=e, countdown=60, max_retries=3)

def _send_reminders_by_preference(time_preference):
    """Helper function to send reminders based on user's time preference"""
    from application.models import User, Reminder, QuizDetails, Viewed
    from application.database import db
    
    try:
        # Get users with specific time preference
        users_with_preference = db.session.query(User, Reminder).join(
            Reminder, User.uid == Reminder.uid
        ).filter(Reminder.reminder == time_preference).all()
        
        if not users_with_preference:
            current_app.logger.info(f"No users with {time_preference} reminder preference found")
            return
        from datetime import date
        # Get all available quizzes
        today = date.today()
        quizzes = QuizDetails.query.filter(QuizDetails.quiz_date >= today).all()
        
        for user, reminder_pref in users_with_preference:
            # Find unviewed quizzes for this user
            unviewed_quizzes = []
            
            for quiz in quizzes:
                viewed = Viewed.query.filter_by(
                    uid=user.uid, 
                    quizid=quiz.quizid
                ).first()
                
                if not viewed or viewed.viewed == 0:
                    unviewed_quizzes.append(quiz)
            
            # Send reminder if there are unviewed quizzes
            if unviewed_quizzes:
                send_preference_reminder_email.delay(user.uid, len(unviewed_quizzes), time_preference)
                
    except Exception as e:
        current_app.logger.error(f"Error in _send_reminders_by_preference for {time_preference}: {str(e)}")
        raise

@celery.task(bind=True)
def send_preference_reminder_email(self, user_id, quiz_count, time_preference):
    """Send reminder email based on user's time preference"""
    try:
        with current_app.app_context():
            from application.models import User
            
            user = User.query.get(user_id)
            if not user:
                return
                
            from flask_mail import Mail, Message
            mail = Mail(current_app)
            
            # Time-specific greetings
            greetings = {
                'morning': 'Good Morning',
                'afternoon': 'Good Afternoon', 
                'evening': 'Good Evening'
            }
            
            greeting = greetings.get(time_preference, 'Hello')
            
            email_template = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9;">
                    <h2 style="color: #4CAF50; text-align: center;">Quiz Master - {greeting}!</h2>
                    <div style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <p><strong>{greeting} {{{{ user.fullname }}}},</strong></p>
                        <p>Hope you're having a great {time_preference}! 🌟</p>
                        <p>You have <strong>{{{{ quiz_count }}}}new unviewed quiz{{{{ 'es' if quiz_count > 1 else '' }}}}</strong> waiting for you.</p>
                        <p>Perfect time to challenge yourself and learn something new!</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="http://localhost:8080/login" style="background-color: #4CAF50; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">Start Quiz Now</a>
                        </div>
                        <p style="color: #666; font-size: 14px;">Best regards,<br>Quiz Master Team</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            html_content = render_template_string(email_template, user=user, quiz_count=quiz_count)
            
            msg = Message(
                subject=f"Quiz Master - {greeting}! You have unviewed quizzes",
                recipients=[user.username],  # Assuming username is email
                html=html_content
            )
            mail.send(msg)
            
            current_app.logger.info(f"{time_preference.title()} reminder sent to user {user_id}")
        
    except Exception as e:
        current_app.logger.error(f"Error sending {time_preference} reminder email to user {user_id}: {str(e)}")
        raise self.retry(exc=e, countdown=60, max_retries=3)

