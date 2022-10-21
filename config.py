import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or "hard to guess string"
    TEMPORAL_FOLDER = os.getenv("TEMPORAL_FOLDER") or "tmp"
    TEMPLATES_AUTORELOAD = True

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False

config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig 
}