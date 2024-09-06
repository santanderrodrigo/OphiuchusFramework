# app.py
import sys
from routes import routes
from core.router import run
from core.updater.updater import Updater

def update_framework():
    updater = Updater(repo_url="https://github.com/santanderrodrigo/pyframework.git", current_version="1.0.0")
    updater.update()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "update":
            update_framework()
        elif command == "run":
            run(port=8080)
        elif command == "help":
            print("Usage: python app.py [command]\n\nCommands:\n  update: Update the framework to the latest version\n  run: Start the server\n  help: Show this help message")
        else:
            print(f"Unknown command: {command}")
    else:
        run(port=8080)
