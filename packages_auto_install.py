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
    command = "source ./%s/bin/activate && pip freeze" % venv_name
    print(f"Running command: {command}")
    subprocess.run(command, shell=True, check=True)


def install_packages(pip_dir, venv_path):
    if platform.system() == "Windows":
        pip_executable = os.path.join(os.getcwd(), venv_path, "Scripts", "pip")
        python_executable = os.path.join(os.getcwd(), venv_path, "Scripts", "python3")
    else:  # Assume Unix-like system
        pip_executable = os.path.join(os.getcwd(), venv_path, "bin", "pip")
        python_executable = os.path.join(os.getcwd(), venv_path, "bin", "python3")


    pip_dir = '%s/%s' % (os.getcwd(), pip_dir)
    os.chdir(pip_dir)
    for package in os.listdir(pip_dir):
        if '.whl' in package:
            command = "pip install %s" % package
            print(f"Running command: {command}")
            subprocess.run([pip_executable, "install", package], check=True, capture_output=True, text=True)
        elif '.tar.gz' in package:
            command = "tar -xzvf ./%s" % package
            print(f"Running command: {command}")
            subprocess.run(command, shell=True, check=True)
            os.chdir('%s/%s' % (pip_dir, package.split(".tar.gz")[0]))
            subprocess.run([python_executable, "setup.py", "install"], check=True, capture_output=True, text=True)
            os.chdir(pip_dir)


def get_os_info():
    os_name = platform.system().lower()
    if os_name == "linux":
        os_name = "manylinux1"
        # Further check for specific Linux distribution
        # distro = platform.linux_distribution()[0].lower()
        # if "centos" in distro and "stream" in distro and "9" in platform.release():
        # os_name = "centos9_stream"
    elif os_name == "windows":
        # os_name = "windows11" if "10.0" in platform.version() else os_name
        os_name = "win"
    return "win" if os_name == "win" else "manylinux1"


def install_dnf_packages(dnf_dir):
    cur_dir = os.getcwd()
    dnf_abs_dir = '%s/%s' % (cur_dir, dnf_dir)
    os.chdir(dnf_abs_dir)
    for package in os.listdir(dnf_abs_dir):
        if '.rpm' in package:
            command = 'dnf install -y %s/%s' % (dnf_abs_dir, package)
            print(f"Running command: {command}")
            os.system(command)
        else:
            print(f"Not an rpm package, skipping, filename: {package}")
    os.chdir(cur_dir)

#deprecated
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
    if 'linux' in get_os_info():
        install_dnf_packages('packages')
    venv_name = "columbus_work_station_venv"
    create_venv(venv_name)
    activate_venv(venv_name)
    install_packages('pip_packages', venv_name)
