FROM python:3.12-slim

# Verhindert, dass Python pyc-Dateien schreibt und Puffer nutzt
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Erstelle non-root User für Sicherheit
RUN addgroup --system dashboard && adduser --system --ingroup dashboard dashboard

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Kopiere das gesamte Dashboard
COPY . /app

# Stelle sicher, dass staticfiles Ordner existiert (für collectstatic)
RUN mkdir -p /app/staticfiles && chown -R dashboard:dashboard /app

USER dashboard

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --database=default --noinput && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --threads 2 --timeout 60"]
