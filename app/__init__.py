from flask import Flask
from celery import Celery
from app.config import Config  

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # register blueprints, etc...
    return app

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config["CELERY_BROKER_URL"],       # ← pull from config
        backend=app.config["CELERY_RESULT_BACKEND"],  # ← pull from config
        include=["app.tasks"],                        # ← auto‑load your tasks
    )
    celery.conf.update(app.config)

    # so tasks run in Flask context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask

    return celery

# initialize
app    = create_app()
celery = make_celery(app)
