from celery import Celery
import redis
from application.config import Config
from celery.schedules import crontab

def make_celery(app=None):
    celery_instance = Celery('myapp')
    
    if app:
        # Configure with app
        celery_instance.conf.update(
            broker_url=app.config['CELERY_BROKER_URL'],
            result_backend=app.config['CELERY_RESULT_BACKEND'],
            accept_content=['json'],
            task_serializer='json',
            result_serializer='json',
            timezone='Asia/Kolkata',
            enable_utc=False,
            include=['tasks'],
            beat_schedule={
                # Morning reminders at 8:00 AM
                'morning-reminders': {
                    'task': 'tasks.send_morning_reminders',
                    'schedule': crontab(hour=8, minute=0),
                },
                # Afternoon reminders at 1:00 PM
                'afternoon-reminders': {
                    'task': 'tasks.send_afternoon_reminders',
                    'schedule': crontab(hour=19, minute=50),
                },
                # Evening reminders at 7:00 PM
                'evening-reminders': {
                    'task': 'tasks.send_evening_reminders',
                    'schedule': crontab(hour=19, minute=0),
                },
                # Daily general reminders at 6:00 PM (for inactive users)
                
                # Monthly reports on 1st of every month at 9:00 AM
                'monthly-reports': {
                    'task': 'tasks.send_monthly_reports',
                    'schedule': crontab(day_of_month=5, hour=19, minute=53),
                }
                
            }
        )

        class ContextTask(celery_instance.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery_instance.Task = ContextTask
    
    return celery_instance

# Create a basic instance for tasks.py to import
celery = Celery('myapp')

# Redis client for caching
redis_client = redis.Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=Config.REDIS_DB,
    decode_responses=True
)