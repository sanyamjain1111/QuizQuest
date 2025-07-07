import os
import sys
from flask import Flask

# Add the current directory to Python path if needed

# Import your Flask app and configuration
from main import app  # Import your Flask app
from tasks import send_daily_reminders, send_monthly_reports

def test_celery_tasks():
    """Test Celery tasks with proper Flask app context"""
    
    with app.app_context():
        print("Testing Celery tasks...")
        print(f"Redis URL: {app.config.get('CELERY_BROKER_URL')}")
        
        try:
            # Test daily reminders
            print("Sending daily reminders task...")
            daily = send_daily_reminders.delay()
            print(f"Daily reminders task ID: {daily.id}")
            print(f"Task state: {daily.state}")
            
            # Test monthly reports
            print("Sending monthly reports task...")
            monthly = send_monthly_reports.delay()
            print(f"Monthly reports task ID: {monthly.id}")
            print(f"Task state: {monthly.state}")
            
            # Wait a bit to see if tasks are picked up
            import time
            time.sleep(2)
            
            print(f"Daily task state after 2s: {daily.state}")
            print(f"Monthly task state after 2s: {monthly.state}")
            
        except Exception as e:
            print(f"Error testing tasks: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_celery_tasks()