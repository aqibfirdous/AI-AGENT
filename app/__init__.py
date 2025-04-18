# app/__init__.py
from flask import Flask
from celery import Celery

class Config:
    # ← your existing config.py values, e.g.:
    CELERY_BROKER_URL    = "amqps://bbinvvqj:Q5UOXa2UpvsQP3zoOFb1WcNaPwgOCBUL@chimpanzee.rmq.cloudamqp.com/bbinvvqj"
    CELERY_RESULT_BACKEND = "rpc://"

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # register blueprints, etc...
    return app

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config["amqps://bbinvvqj:Q5UOXa2UpvsQP3zoOFb1WcNaPwgOCBUL@chimpanzee.rmq.cloudamqp.com/bbinvvqj"],       # ← pull from config
        backend=app.config["rpc://"],  # ← pull from config
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
