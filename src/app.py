# app.py
import os
import sys
from core.utils import load_env_file
load_env_file() # cargamnos la configuración de .env antes de importar run
from core.router import run_http, run_https, run_both
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
            http_port = int(os.getenv('SERVER_HTTP_PORT', 8080))
            https_port = int(os.getenv('SERVER_HTTPS_PORT', 8443))
            #si el argumento es --https ejecutamos el servidor en el puerto https
            if len(sys.argv) > 2 and sys.argv[2] == "--https":
                run_https(port= https_port)
            #si el argumento es --both ejecutamos el servidor en ambos puertos
            elif len(sys.argv) > 2 and sys.argv[2] == "--both":
                run_both(http_port=http_port, https_port=https_port)
            else:
                run_http(port=http_port)


        elif command == "help":
            print("Usage: python app.py [command]\n\nCommands:\n  update: Update the framework to the latest version\n  run: Start the server\n  help: Show this help message")
        else:
            print(f"Unknown command: {command}")
    else:
        # Si no se proporciona ningún argumento, se ejecuta el servidor
        # en el puerto configurado en la variable de entorno PORT
        http_port = int(os.getenv('SERVER_HTTP_PORT', 8080))
        run_http(port=http_port)
