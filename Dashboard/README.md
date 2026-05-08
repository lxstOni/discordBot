# Discord Bot Dashboard

Ein sicheres, skalierbares Dashboard für den Discord Bot, implementiert mit Django.

## Architektur

- **Config**: Globale Einstellungen (Security, Datenbanken, Middleware)
- **Core**: Verwaltung der `GuildConfig` Tabellen des Bots.
- **Docker**: Wird gemeinsam mit dem Bot in `../Docker/docker-compose.yml` gestartet.

## Setup (Produktiv)

1. Setze die Umgebungsvariablen in der `docker-compose.yml` oder einer `.env` Datei:
   - `DASHBOARD_SECRET_KEY`: Langer Zufallsstring (Pflicht für Produktion!).
   - `DASHBOARD_DEBUG`: `false` für Produktion.
   - `DASHBOARD_ALLOWED_HOSTS`: Erlaubte Domains (Bsp: `dashboard.example.com`).

2. Starte die Services:
   ```bash
   cd ../Docker
   docker-compose up -d --build
   ```

3. Erstelle einen Admin-User (Superuser) für das Dashboard:
   ```bash
   docker exec -it discord-dashboard python manage.py createsuperuser
   ```

4. Öffne das Dashboard im Browser auf `http://localhost:8000` und logge dich ein.
