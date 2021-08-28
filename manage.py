import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import app, db
from config import config

config_name = os.environ.get("APP_MODE") or "development"

app.config.from_object(config[config_name])

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()