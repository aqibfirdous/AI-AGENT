from celery.schedules import crontab


class Config:
    SECRET_KEY = '3fae1b2c9d7e4e48b3c52d5c87a9fa83b1f8c9e0a84723d6e9b2ff71b3e2c412'

    # RabbitMQ configuration for Celery
    CELERY_BROKER_URL = 'amqps://bbinvvqj:Q5UOXa2UpvsQP3zoOFb1WcNaPwgOCBUL@chimpanzee.rmq.cloudamqp.com/bbinvvqj'
    CELERY_RESULT_BACKEND = 'rpc://'

    # Provided API endpoint for task activity (adjust as needed)
    API_ENDPOINT = "https://startupworld.in/Version1/get_task_activity.php?from_date=2025-04-15!&to_date=2025-04-15"

    # Celery Beat schedule: run report tasks at 1:00 PM and 6:00 PM every day.
    CELERY_BEAT_SCHEDULE = {
        'report-1-pm': {
            'task': 'app.tasks.send_report',
            'schedule': crontab(hour=13, minute=0),
        },
        'report-6-pm': {
            'task': 'app.tasks.send_report',
            'schedule': crontab(hour=18, minute=0),
        },
    }
    # Ensure the tasks module is included using the old naming convention.
    CELERY_INCLUDE = ['app.tasks']
