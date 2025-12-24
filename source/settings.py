import logging
import os
import json
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, List, Optional

from sqlalchemy import Boolean, Column, String, Integer, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from source.paths import get_logs_dir_path, get_bot_log_path, get_config_db_path


Base = declarative_base()


class GuildConfig(Base):
    __tablename__ = "guild_config"
    guild_id = Column(String, primary_key=True)
    mod_role_ids = Column(Text, nullable=True)  # JSON array
    ticket_role_ids = Column(Text, nullable=True)  # JSON array
    welcome_channel_id = Column(String, nullable=True)
    j2c_lobby_channel_id = Column(String, nullable=True)
    j2c_category_channel_id = Column(String, nullable=True)
    ticket_embed_channel_id = Column(String, nullable=True)  # Channel für Ticket Embed
    ticket_category_id = Column(String, nullable=True)  # Kategorie für Tickets


class J2CState(Base):
    __tablename__ = "j2c_state"
    channel_id = Column(String, primary_key=True)  # clone voice or category id
    guild_id = Column(String, index=True, nullable=False)
    kind = Column(String, nullable=False)  # 'clone' or 'category'
    category_id = Column(String, nullable=True)
    voice_channel_id = Column(String, nullable=True)
    name = Column(String, nullable=True)


class Settings:
    def __init__(self):
        self.logger = None
        self.engine = None
        self.SessionLocal = None
    
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

    # --- SQL initialisieren ---
    def init_db(self):
        db_path = get_config_db_path()
        self.engine = create_engine(
            f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
        )
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
        Base.metadata.create_all(self.engine)
        
        # Automatische Migration: Füge fehlende Spalten hinzu
        self._migrate_db()
        
        if self.logger:
            self.logger.info("Config-DB initialisiert: %s", db_path)

    def _migrate_db(self):
        """Füge neue Spalten hinzu, falls sie fehlen (für DB-Updates)"""
        import sqlite3
        try:
            db_path = get_config_db_path()
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Hole alle Spalten der guild_config Tabelle
            cursor.execute("PRAGMA table_info(guild_config)")
            columns = {row[1] for row in cursor.fetchall()}
            
            # Neue Spalten, die hinzugefügt werden müssen
            new_columns = [
                ("ticket_embed_channel_id", "VARCHAR"),
                ("ticket_category_id", "VARCHAR"),
            ]
            
            # Füge fehlende Spalten hinzu
            for col_name, col_type in new_columns:
                if col_name not in columns:
                    alter_sql = f"ALTER TABLE guild_config ADD COLUMN {col_name} {col_type}"
                    cursor.execute(alter_sql)
                    if self.logger:
                        self.logger.info(f"Spalte hinzugefügt: {col_name}")
            
            conn.commit()
            conn.close()
        except Exception as e:
            if self.logger:
                self.logger.warning(f"DB Migration fehlgeschlagen (ignoriert): {e}")

    def _ensure_session(self):
        if self.SessionLocal is None:
            self.init_db()
        return self.SessionLocal()

    # --- GuildConfig Helpers ---
    def get_config(self, guild_id: int | str) -> Dict[str, Any]:
        session = self._ensure_session()
        gid = str(guild_id)
        try:
            obj = session.get(GuildConfig, gid)
            if obj is None:
                obj = GuildConfig(guild_id=gid)
                session.add(obj)
                session.commit()
            return {
                "guild_id": obj.guild_id,
                "mod_role_ids": json.loads(obj.mod_role_ids) if obj.mod_role_ids else [],
                "ticket_role_ids": json.loads(obj.ticket_role_ids) if obj.ticket_role_ids else [],
                "welcome_channel_id": obj.welcome_channel_id,
                "j2c_lobby_channel_id": obj.j2c_lobby_channel_id,
                "j2c_category_channel_id": obj.j2c_category_channel_id,
                "ticket_embed_channel_id": obj.ticket_embed_channel_id,
                "ticket_category_id": obj.ticket_category_id,
            }
        finally:
            session.close()

    def update_config(self, guild_id: int | str, updates: Dict[str, Any]) -> Dict[str, Any]:
        session = self._ensure_session()
        gid = str(guild_id)
        try:
            obj = session.get(GuildConfig, gid)
            if obj is None:
                obj = GuildConfig(guild_id=gid)
                session.add(obj)
            if "mod_role_ids" in updates:
                obj.mod_role_ids = json.dumps([str(i) for i in updates["mod_role_ids"]])
            if "ticket_role_ids" in updates:
                obj.ticket_role_ids = json.dumps([str(i) for i in updates["ticket_role_ids"]])
            if "welcome_channel_id" in updates:
                obj.welcome_channel_id = str(updates["welcome_channel_id"]) if updates["welcome_channel_id"] else None
            if "j2c_lobby_channel_id" in updates:
                obj.j2c_lobby_channel_id = str(updates["j2c_lobby_channel_id"]) if updates["j2c_lobby_channel_id"] else None
            if "j2c_category_channel_id" in updates:
                obj.j2c_category_channel_id = str(updates["j2c_category_channel_id"]) if updates["j2c_category_channel_id"] else None
            if "ticket_embed_channel_id" in updates:
                obj.ticket_embed_channel_id = str(updates["ticket_embed_channel_id"]) if updates["ticket_embed_channel_id"] else None
            if "ticket_category_id" in updates:
                obj.ticket_category_id = str(updates["ticket_category_id"]) if updates["ticket_category_id"] else None
            session.commit()
            return self.get_config(gid)
        finally:
            session.close()

    # --- JoinToCreate State ---
    def add_j2c_clone(self, guild_id: int | str, channel_id: int | str, name: Optional[str] = None):
        session = self._ensure_session()
        try:
            session.merge(J2CState(channel_id=str(channel_id), guild_id=str(guild_id), kind="clone", name=name))
            session.commit()
        finally:
            session.close()

    def add_j2c_category(self, guild_id: int | str, category_id: int | str, voice_channel_id: int | str, name: Optional[str] = None):
        session = self._ensure_session()
        try:
            session.merge(
                J2CState(
                    channel_id=str(category_id), guild_id=str(guild_id), kind="category",
                    category_id=str(category_id), voice_channel_id=str(voice_channel_id), name=name
                )
            )
            session.commit()
        finally:
            session.close()

    def remove_j2c_entry(self, channel_or_category_id: int | str):
        session = self._ensure_session()
        cid = str(channel_or_category_id)
        try:
            obj = session.get(J2CState, cid)
            if obj:
                session.delete(obj)
                session.commit()
        finally:
            session.close()

    def list_j2c_entries(self, guild_id: int | str) -> List[Dict[str, Any]]:
        session = self._ensure_session()
        try:
            rows = session.query(J2CState).filter(J2CState.guild_id == str(guild_id)).all()
            return [
                {
                    "channel_id": r.channel_id,
                    "guild_id": r.guild_id,
                    "kind": r.kind,
                    "category_id": r.category_id,
                    "voice_channel_id": r.voice_channel_id,
                    "name": r.name,
                }
                for r in rows
            ]
        finally:
            session.close()


# Singleton-Instanz
settings = Settings()
