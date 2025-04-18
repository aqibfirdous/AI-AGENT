from flask import Flask
from celery import Celery
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # Additional Flask configuration or blueprint registrations can be added here.
    return app


def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config.get('CELERY_BROKER_URL'),
        backend=app.config.get('CELERY_RESULT_BACKEND')
    )
    celery.conf.update(app.config)

    # Ensure Celery tasks have access to the Flask application context.
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


# Initialize the Flask app and the Celery instance.
app = create_app()
celery = make_celery(app)
