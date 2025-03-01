import os
import subprocess
import sys
from pathlib import Path

try:
    print("winshell sí está instalado")
    import winshell  # Intenta importar winshell
except ImportError:
    print("winshell no está instalado. Instalando...")
    subprocess.run([sys.executable, "-m", "pip", "install", "winshell"], check=True)
    print("winshell instalado correctamente.")
    import winshell

def open_terminal():
    # This function will open a new terminal window to show the installation status
    if sys.platform == "win32":
        subprocess.Popen(["cmd", "/k", "echo Installation in progress..."])
    else:
        subprocess.Popen(["x-terminal-emulator", "-e", "echo Installation in progress..."])

def verify_python():
    # Verify that Python is installed
    try:
        subprocess.run([sys.executable, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Python is installed.")
    except subprocess.CalledProcessError:
        print("Python is not installed. Please install Python from https://www.python.org/")
        sys.exit(1)

def verify_git():
    # Verify that Git is installed
    try:
        subprocess.run(["git", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Git is installed.")
    except subprocess.CalledProcessError:
        print("Git is not installed. Please install Git from https://git-scm.com/")
        sys.exit(1)

def clone_or_update_repository(repo_url, target_dir):
    # Clone the GitHub repository to the target directory
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    if os.listdir(target_dir):
        print("Target directory already exists. Updating repository...")
        try:
            subprocess.run(["git", "-C", target_dir, "pull"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to update repository: {e}")
            sys.exit(1)
    else:
        print("Cloning repository...")
        try:
            subprocess.run(["git", "clone", repo_url, target_dir], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to clone repository: {e}")
            sys.exit(1)

def install_dependencies(requirements_path):
    # Install Python dependencies from requirements.txt
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        sys.exit(1)

def create_bat_file(target_dir, script_name, bat_name="run_app.bat"):
    # Create a .bat file that runs main.py using Python
    bat_path = os.path.join(target_dir, bat_name)
    with open(bat_path, "w") as f:
        f.write(f"""@echo off
{sys.executable} "{os.path.join(target_dir, script_name)}" %*
pause
""")
    print(f".bat file created at {bat_path}")

# Función para crear un acceso directo
def create_shortcut(target_path, shortcut_name, description=None, icon_path=None, working_directory=None):
    """
    Crea un acceso directo en el escritorio.

    Parámetros:
        target_path (str): Ruta del archivo o carpeta al que apunta el acceso directo.
        shortcut_name (str): Nombre del acceso directo (sin extensión .lnk).
        description (str, opcional): Descripción del acceso directo.
        icon_path (str, opcional): Ruta del icono personalizado.
        working_directory (str, opcional): Directorio de trabajo para el acceso directo.
    """
    # Obtener la ruta del escritorio
    desktop = Path(winshell.desktop())
    shortcut_path = str(desktop / f"{shortcut_name}.lnk")

    # Crear el acceso directo
    with winshell.shortcut(shortcut_path) as link:
        link.path = str(target_path)  # Ruta del archivo o carpeta
        link.description = description if description else f"Acceso directo a {shortcut_name}"
        link.icon_location = (icon_path, 0) if icon_path else (None, 0)
        link.working_directory = working_directory if working_directory else str(Path(target_path).parent)

    print(f"Acceso directo '{shortcut_name}' creado en el escritorio.")

def main():
    repo_url = "https://github.com/Jerbo03/Punto_de_venta.git"  # Replace with your GitHub repo URL
    target_dir = r"D:\PDV"
    requirements_path = os.path.join(target_dir, "requirements.txt")
    script_name = "main.py"  # Replace with your main script name
    bat_name = "Punto_de_venta.bat"  # Replace with your main script name

    open_terminal()
    verify_python()
    verify_git()
    clone_or_update_repository(repo_url, target_dir)
    install_dependencies(requirements_path)
    create_bat_file(target_dir, script_name, bat_name)

    # Definir las rutas de los archivos y carpetas
    main_py_path = os.path.join(target_dir, bat_name)
    ventas_csv_path = os.path.join(target_dir, "admin", "ventas_csv")
    ventas_excel_path = os.path.join(target_dir, "admin", "ventas_excel")
    recibos_path = os.path.join(target_dir, r"recibos")
    
    # Crear acceso directo para main.py
    create_shortcut(
        target_path=main_py_path,
        shortcut_name="main_py",
        description="Acceso directo a main.py",
        icon_path=str(main_py_path),  # Usar el icono del archivo
    )

    # Crear acceso directo para la carpeta ventas_csv
    create_shortcut(
        target_path=ventas_csv_path,
        shortcut_name="ventas_csv",
        description="Acceso directo a ventas_csv",
        icon_path=str(ventas_csv_path),  # Usar el icono predeterminado de carpeta
    )

    # Crear acceso directo para la carpeta ventas_excel
    create_shortcut(
        target_path=ventas_excel_path,
        shortcut_name="ventas_excel",
        description="Acceso directo a ventas_excel",
        icon_path=str(ventas_excel_path),  # Usar el icono predeterminado de carpeta
    )

    # Crear acceso directo para la carpeta recibos
    create_shortcut(
        target_path=recibos_path,
        shortcut_name="recibos",
        description="Acceso directo a recibos",
        icon_path=str(recibos_path),  # Usar el icono predeterminado de carpeta
    )

    print("Installation completed successfully!")

if __name__ == "__main__":
    main()