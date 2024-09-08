# app.py
import os
import sys
from pathlib import Path
from core.utils import load_env_file
load_env_file() # cargamnos la configuración de .env antes de importar run
from core.router import run_http, run_https, run_both
from core.updater.updater import Updater

# Verificar y crear archivos SSL si no existen
def create_ssl_certificates():
    cert_file = Path(os.getenv('SSL_CERT_FILE', 'cert.pem'))
    key_file = Path(os.getenv('SSL_KEY_FILE', 'key.pem'))


    if not cert_file.exists() or not key_file.exists():
        # Importar OpenSSL solo si es necesario
        #averiguamos si el modulo esta instalado
        try:
            from OpenSSL import crypto, SSL
        except ImportError:
            print("OpenSSL module not found. Please install it using 'pip install pyopenssl'")
            sys.exit(1)

        # Crear una clave privada
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)

        # Crear un certificado autofirmado
        cert = crypto.X509()
        cert.get_subject().C = "AR"
        cert.get_subject().ST = "Buenos Aires"
        cert.get_subject().L = "Monte Hermoso"
        cert.get_subject().O = "My Company"
        cert.get_subject().OU = "My Organization"
        cert.get_subject().CN = "localhost"
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(10*365*24*60*60)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(key)
        cert.sign(key, 'sha256')

        # Guardar la clave privada y el certificado en archivos
        with open(cert_file, "wb") as cert_file_out:
            cert_file_out.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        with open(key_file, "wb") as key_file_out:
            key_file_out.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

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
            host = os.getenv('SERVER_HOST', '0.0.0.0')
            #si el argumento es --https ejecutamos el servidor en el puerto https
            if len(sys.argv) > 2 and sys.argv[2] == "--https":
                #si no existen los archivos de certificado y clave, poreguntamos al usuario si desea crearlos
                if not Path('cert.pem').exists() or not Path('key.pem').exists():
                    print("SSL certificates not found. Do you want to create them? (y/n)")
                    answer = input()
                    if answer.lower() == 'y':
                        create_ssl_certificates()
                    else:
                        print("SSL certificates are required to run the server in HTTPS mode.")
                        sys.exit(1)
                run_https(port= https_port, host=host)
            #si el argumento es --both ejecutamos el servidor en ambos puertos
            elif len(sys.argv) > 2 and sys.argv[2] == "--both":
                run_both(http_port=http_port, https_port=https_por, host=host)
            else:
                run_http(port=http_port, host=host)

        elif command == "help":
            print("Usage: python app.py [command]\n\nCommands:\n  update: Update the framework to the latest version\n  run: Start the server\n  help: Show this help message")
        else:
            print(f"Unknown command: {command}")
    else:
        # Si no se proporciona ningún argumento, se ejecuta el servidor
        # en el puerto configurado en la variable de entorno PORT
        http_port = int(os.getenv('SERVER_HTTP_PORT', 8080))
        run_http(port=http_port)
