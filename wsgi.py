"""
Entry point WSGI.

Uso comum:
    - `flask --app wsgi:app run`
    - `gunicorn wsgi:app -b 0.0.0.0:8000`
"""

from app import create_app

app = create_app()
