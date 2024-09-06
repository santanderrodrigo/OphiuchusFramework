import os
import subprocess
import sys

class Updater:
    def __init__(self, repo_url, current_version, repo_path='repo'):
        self.repo_url = repo_url
        self.current_version = current_version
        self.repo_path = repo_path

    def check_for_updates(self):
        # Clona el repositorio si no existe
        if not os.path.exists(self.repo_path):
            subprocess.run(['git', 'clone', self.repo_url, self.repo_path])
        # Obtiene la última versión del repositorio
        subprocess.run(['git', 'fetch'], cwd=self.repo_path)
        latest_version = subprocess.check_output(['git', 'rev-parse', 'origin/main'], cwd=self.repo_path).strip().decode('utf-8')
        if self.is_newer_version(latest_version):
            print(f"New version available: {latest_version}")
            return latest_version
        return None

    def is_newer_version(self, latest_version):
        return latest_version != self.current_version

    def apply_update(self, version):
        # Hace pull de la última versión
        subprocess.run(['git', 'pull'], cwd=self.repo_path)
        # Copia los archivos actualizados al directorio actual
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith('.py'):
                    shutil.copy(os.path.join(root, file), os.path.join(os.getcwd(), file))
        print("Update applied successfully.")

    def update(self):
        latest_version = self.check_for_updates()
        if latest_version:
            self.apply_update(latest_version)
            self.restart_service()

    def restart_service(self):
        print("Restarting service...")
        os.execv(sys.executable, ['python'] + sys.argv)

if __name__ == "__main__":
    updater = Updater(repo_url="https://github.com/tu_usuario/tu_repositorio.git", current_version="1.0.0")
    updater.update()