import os
from pydantic import (BaseModel, BaseSettings, FilePath, DirectoryPath)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

class LogsSettings(BaseModel):
    log_dir: DirectoryPath = os.path.join(ROOT_DIR, "..\\logs")
    log_level: str = "INFO"

class Settings(BaseSettings): 
    output_path: FilePath = os.path.join(ROOT_DIR,"..\\resources\\input-2.json")
    logs_settings: LogsSettings = LogsSettings()