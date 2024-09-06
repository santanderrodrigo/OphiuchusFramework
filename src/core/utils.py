import os

def load_env_file(filepath='.env'):
    # Obtener el directorio raíz del proyecto
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    env_path = os.path.join(root_dir, filepath)
    
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
                    print(f"Setting environment variable: {key}={value}")
    else:
        print(f"Warning: {env_path} file not found.")