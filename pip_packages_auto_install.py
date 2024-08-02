import os
import subprocess
import platform
import sys

# python3 -m venv my_venv
def create_venv(venv_name):
    command = [sys.executable, "-m", "venv", venv_name]
    print(f"Running command: {' '.join(command)}")
    subprocess.run(command, check=True)

def activate_venv(venv_name):
    command = f"source /Users/kuangyuan/Documents/columbus/%s/bin/activate && pip freeze" % venv_name
    print(f"Running command: {' '.join(command)}")
    subprocess.run(command, shell=True, check=True)

def install_packages(venv_name, dir):
    for filename in os.listdir(dir):
        if '.whl' in filename:
            command = ["./%s/bin/pip" % venv_name, "install", "./%s/%s" % (dir, filename)]
            print(f"Running command: {' '.join(command)}")
            subprocess.call(command, shell=True)

def activate_virtualenv_and_install(venv_path, packages_dir):
    # Determine the path to the activate script based on the operating system
    if platform.system() == "Windows":
        activate_script = os.path.join(venv_path, "Scripts", "activate")
        pip_executable = os.path.join(venv_path, "Scripts", "pip")
    else:  # Assume Unix-like system
        activate_script = os.path.join(venv_path, "bin", "activate")
        pip_executable = os.path.join(venv_path, "bin", "pip")

    # Ensure the virtual environment activation script exists
    if not os.path.exists(activate_script):
        print(f"Virtual environment activation script not found at {activate_script}")
        sys.exit(1)

    # Install each package using the virtual environment's pip
    for package in packages:
        try:
            print(f"Installing package: {package}")
            result = subprocess.run([pip_executable, "install", package], check=True, capture_output=True, text=True)
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Failed to install package: {package}")
            print(e.stderr)
            sys.exit(1)

if __name__ == "__main__":
    name = "columbus_work_station"
    # create_venv(name)
    activate_venv(name)
    install_packages(name, 'pip_packages')