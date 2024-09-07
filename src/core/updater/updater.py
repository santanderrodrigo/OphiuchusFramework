import os
import subprocess
import sys
import shutil
import datetime

class Updater:
    def __init__(self, repo_url, current_version, repo_path='repo'):
        self.repo_url = repo_url
        self.current_version = current_version
        self.repo_path = repo_path
        self.backup_path = f'backup_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}'
        self.backup_zip = f'{self.backup_path}.zip'

    def check_for_updates(self):
        # Clonamos el repositorio si no existe
        if not os.path.exists(self.repo_path):
            subprocess.run(['git', 'clone', self.repo_url, self.repo_path])
        # Obtenemos  la última versión del repositorio
        subprocess.run(['git', 'fetch'], cwd=self.repo_path)
        latest_version = subprocess.check_output(['git', 'rev-parse', 'origin/main'], cwd=self.repo_path).strip().decode('utf-8')
        if self.is_newer_version(latest_version):
            print(f"New version available: {latest_version}")
            return latest_version
        return None

    def is_newer_version(self, latest_version):
        return latest_version != self.current_version

    def create_backup(self):
        print(f"Creating backup at {self.backup_path}...")
        shutil.copytree(os.getcwd(), self.backup_path)
        shutil.make_archive(self.backup_path, 'zip', self.backup_path)
        shutil.rmtree(self.backup_path)  # Remove the uncompressed backup directory
        print(f"Backup created successfully at {self.backup_zip}.")

    def apply_update(self, version):
        #Creamos el backup
        self.create_backup()

        # Hacemos pull de la última versión
        subprocess.run(['git', 'pull'], cwd=self.repo_path)
        
        # Copiamops los archivos actualizados al directorio actual
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                src_file = os.path.join(root, file)
                rel_path = os.path.relpath(src_file, self.repo_path)
                dest_file = os.path.join(os.getcwd(), rel_path)
                
                if 'core' in rel_path:
                    # los archivos del core del frameworl los actualizamos siempre
                    shutil.copy(src_file, dest_file)
                else:
                    # Averiguamos si el archivo ya existe
                    if os.path.exists(dest_file):
                        # Preguntamos al usuario si desea sobreescribir el archivo
                        user_input = input(f"File {rel_path} exists. Overwrite? (y/n): ").strip().lower()
                        if user_input == 'y':
                            shutil.copy(src_file, dest_file)
                            print(f"File {rel_path} overwritten.")
                        else:
                            print(f"File {rel_path} kept as is.")
                    else:
                        shutil.copy(src_file, dest_file)
                        print(f"File {rel_path} copied.")

        print("Update applied successfully.")

    def update(self):
        latest_version = self.check_for_updates()
        if latest_version:
            print("This is an experimental feature. Use at your own risk.")
            user_input = input("Are you sure you want to update? (y/n): ").strip().lower()
            if user_input == 'y':
                self.apply_update(latest_version)
                self.restart_service()

    def restart_service(self):
        print("Restarting service...")
        os.execv(sys.executable, ['python'] + sys.argv)

if __name__ == "__main__":
    updater = Updater(repo_url="https://github.com/tu_usuario/tu_repositorio.git", current_version="1.0.0")
    updater.update()