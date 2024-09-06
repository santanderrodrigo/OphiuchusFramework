# app.py
from routes import routes
from core.router import run

if __name__ == '__main__':
    run(port=8080)
