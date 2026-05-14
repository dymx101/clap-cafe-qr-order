# backend/Dockerfile — single-stage, lean for Render free tier
FROM python:3.11-slim

WORKDIR /app

# Install deps in one layer, then remove cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt greenlet

# Copy app
COPY ./app ./app
COPY alembic ./alembic
COPY alembic.ini .

ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

COPY startup.sh .
RUN chmod +x startup.sh

CMD ["./startup.sh"]
