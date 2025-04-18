web: gunicorn app.main:app
web:    gunicorn wsgi:app
worker: celery \
          --app app.celery_app:celery \
          worker \
          --loglevel=info \
          --uid nobody \
          --gid nobody
beat:   celery \
          --app app.celery_app:celery \
          beat \
          --loglevel=info \
          --uid nobody \
          --gid nobody
