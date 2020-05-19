import os
import logging
from setting import LogsSettings


def init_logger(settings: LogsSettings):
    log_path = os.path.join(settings.log_dir, 'app.log')    
    handler = logging.FileHandler(
        filename=str(log_path), encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter(
        '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    app_logger = logging.getLogger('wintego')
    app_logger.setLevel(settings.log_level)
    app_logger.addHandler(handler)
    app_logger.addHandler(ch)
