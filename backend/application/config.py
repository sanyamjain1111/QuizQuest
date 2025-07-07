import os
from celery.schedules import crontab
basedir=os.path.abspath(os.path.dirname(__file__))

class Config():
    DEBUG=False
    SQLITE_DB_dIR= None 
    SQLALCHEMY_DATABASE_URI=None
    SQLALCHEMY_TRACK_MODIFICATIONS= False
    REDIS_HOST = '172.17.244.178'
    REDIS_PORT = 6380
    REDIS_DB = 0
    REDIS_URL = 'redis://172.17.244.178:6380/0'
    CELERY_BROKER_URL = 'redis://172.17.244.178:6380/0'
    CELERY_RESULT_BACKEND = 'redis://172.17.244.178:6380/0'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ENABLE_UTC = False
    CELERY_TIMEZONE = 'Asia/Kolkata'
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    CACHE_KEY_PREFIX = 'mad2_' 
    
    # Celery Beat Schedule
    CELERY_BEAT_SCHEDULE = {
        'daily-reminders': {
            'task': 'tasks.send_daily_reminders',
            'schedule': crontab(hour=18, minute=0),  # 6 PM daily
        },
        'monthly-reports': {
            'task': 'tasks.send_monthly_reports',
            'schedule': crontab(day_of_month=1, hour=9, minute=0),  # 1st of every month at 9 AM
        },}

class LocalDevelopementConfig(Config):
    SQLITE_DB_DIR=os.path.join(basedir, "../db_directory")
    SQLALCHEMY_DATABASE_URI="sqlite:///"+os.path.join(SQLITE_DB_DIR, "mydb.sqlite3")
    DEBUG=True