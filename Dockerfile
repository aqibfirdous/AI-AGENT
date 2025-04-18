# 1. Base image
FROM python:3.12-slim

# 2. Create a non‑root user & group for running Celery
RUN groupadd --system celery \
 && useradd --system --create-home --home-dir /home/celery --gid celery --shell /usr/sbin/nologin celery

# 3. Install OS deps (if any) and pip
#    here we install gcc just in case any pip packages need to compile,
#    remove it later to keep image slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc \
 && rm -rf /var/lib/apt/lists/*

# 4. Set the working directory
WORKDIR /app

# 5. Copy only requirements first (for better layer caching)…
COPY requirements.txt /app/

# 6. Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copy your entire application code
COPY . /app

# 8. chown everything to the celery user
RUN chown -R celery:celery /app

# 9. Switch to that unprivileged user
USER celery

# 10. Default command: start your Celery worker
CMD ["celery", "-A", "app", "worker", "--loglevel=INFO", "--concurrency=48"]
