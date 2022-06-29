import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "hard to guess string")
    TEMPORAL_FOLDER = os.environ.get("TEMPORAL_FOLDER") or "tmp"

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False

config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig 
}