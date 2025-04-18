# 1) Start RabbitMQ on its host (or docker/rpi/etc.)
# 2) In your venv:
pip install -r requirements.txt

# Run Celery worker:
celery -A app.tasks.celery_app worker --loglevel=info

# (Optional) run beat scheduler:
celery -A app.tasks.celery_app beat --loglevel=info

# Run Flask production server:
gunicorn --workers 4 --bind 0.0.0.0:5000 wsgi:app
