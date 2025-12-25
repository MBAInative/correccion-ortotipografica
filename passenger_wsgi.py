"""
WSGI entry point for Hostinger cPanel Python App.
Passenger requires the variable to be named 'application'.
"""
import sys
import os

# Add the app directory to path
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_dir)

# Import the Flask app
from app_web import app as application

# Ensure templates and sessions directories exist
os.makedirs(os.path.join(app_dir, 'sessions'), exist_ok=True)
os.makedirs(os.path.join(app_dir, 'uploads'), exist_ok=True)

if __name__ == '__main__':
    application.run()
