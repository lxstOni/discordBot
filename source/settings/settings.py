import discord
import ezcord
import os
from pathlib import Path
import logging
import logging.handlers

####### LOGGING ######################

def setup_logger():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    logging.getLogger('discord.http').setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
        filename='source/log/discord.log',
        encoding='utf-8',
        maxBytes=4 * 1024 * 1024,
        backupCount=3,  
    )
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

#####################################