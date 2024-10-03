import os
from app import create_app

#  In order to launch the application tap
# sudo python entrypoint.py

settings_module = os.getenv('APP_SETTINGS_MODULE') or 'config.dev'

app = create_app(settings_module)

if settings_module != 'config.prod':
    app.run(host='0.0.0.0', port=5000)