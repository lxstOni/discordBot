import logging
import os
from logging.handlers import RotatingFileHandler
from source.paths import get_logs_dir_path, get_bot_log_path


class Settings:
    def __init__(self):
        self.logger = None
    
    def setup_logger(self):
        """
        Richtet das Logging-System ein mit rotating file handler.
        - Logs werden in 'logs/bot.log' gespeichert
        - Maximal 5 Dateien
        - Maximale Größe pro Datei: 5MB
        - Wenn 5 Dateien erreicht sind, wird die älteste entfernt
        """
        # Erstelle logs Ordner falls nicht vorhanden
        log_folder = get_logs_dir_path()
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)
            print(f"Ordner '{log_folder}' wurde erstellt.")
        
        # Logger konfigurieren
        self.logger = logging.getLogger('discord_bot')
        self.logger.setLevel(logging.DEBUG)
        
        # Entferne existierende Handler um Duplikate zu vermeiden
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        
        # Rotating File Handler (5MB pro Datei, maximal 5 Dateien)
        file_handler = RotatingFileHandler(
            filename=get_bot_log_path(),
            maxBytes=5 * 1024 * 1024,  # 5MB in Bytes
            backupCount=5,  # Maximal 5 Dateien (bot.log + 5 Backups)
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console Handler für Terminal-Ausgabe
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter für Log-Nachrichten
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Handler zum Logger hinzufügen
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info("Logger wurde erfolgreich eingerichtet.")
        
        return self.logger


# Singleton-Instanz
settings = Settings()
