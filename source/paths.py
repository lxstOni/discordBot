"""
Pfad-Management für relative Pfade.
Alle Pfade werden relativ zum Projektroot definiert.
"""

import os
from pathlib import Path

# Projektroot - der Ordner wo main.py liegt
PROJECT_ROOT = Path(__file__).parent.parent

# Datenbank Pfade
DB_DIR = PROJECT_ROOT / "source" / "db"
TICKETS_DB = DB_DIR / "tickets.db"
LEVEL_DB = DB_DIR / "level.db"
CONFIG_DB = DB_DIR / "config.db"

# Log Pfade
LOGS_DIR = PROJECT_ROOT / "logs"
BOT_LOG = LOGS_DIR / "bot.log"

# Daten Pfade
DATA_DIR = PROJECT_ROOT / "data"
IMAGES_DIR = DATA_DIR / "Images"
WELCOME_IMAGE = IMAGES_DIR / "pic1.jpg"

# Temporäre Daten
TEMP_DATA_DIR = PROJECT_ROOT / "source"
TEMP_DATA_FILE = TEMP_DATA_DIR / "temporary_data.json"

# Erstelle alle notwendigen Verzeichnisse
def ensure_directories():
    """Erstellt alle notwendigen Verzeichnisse"""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DATA_DIR.mkdir(parents=True, exist_ok=True)


# Konvertiere Path Objekte zu Strings
def get_tickets_db_path() -> str:
    """Gibt den Pfad zur Tickets Datenbank zurück"""
    return str(TICKETS_DB)


def get_level_db_path() -> str:
    """Gibt den Pfad zur Level Datenbank zurück"""
    return str(LEVEL_DB)


def get_config_db_path() -> str:
    """Pfad zur Konfigurations-Datenbank (GuildConfig/J2C/Reminders/Games)"""
    return str(CONFIG_DB)


def get_logs_dir_path() -> str:
    """Gibt den Pfad zum Logs Verzeichnis zurück"""
    return str(LOGS_DIR)


def get_bot_log_path() -> str:
    """Gibt den Pfad zur Bot Log Datei zurück"""
    return str(BOT_LOG)


def get_welcome_image_path() -> str:
    """Gibt den Pfad zum Welcome Bild zurück"""
    return str(WELCOME_IMAGE)


def get_temp_data_file_path() -> str:
    """Gibt den Pfad zur temporären Datendatei zurück"""
    return str(TEMP_DATA_FILE)


# Initialisiere Verzeichnisse beim Import
ensure_directories()
