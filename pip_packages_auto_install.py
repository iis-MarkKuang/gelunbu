import os
import subprocess
import platform
import sys
import shutil

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

    root_dir = os.getcwd()
    pip_dir = '%s/%s' % (root_dir, pip_dir)
    # install basic packages first
    all_packages = os.listdir(pip_dir)
    whl_packages = list(filter(lambda s: 'whl' in s, all_packages))
    tar_packages = list(filter(lambda s: 'tar.gz' in s, all_packages))
    whl_failed_pkg_list = handle_packages_set_with_retry(whl_packages, pip_executable, python_executable, pip_dir)
    tar_failed_pkg_list = handle_packages_set_with_retry(tar_packages, pip_executable, python_executable, pip_dir)
    print(f"FAILED PACKAGES = {whl_failed_pkg_list + tar_failed_pkg_list}")
    res_failed_pkg_list = handle_packages_set_with_retry(whl_failed_pkg_list + tar_failed_pkg_list, pip_executable, python_executable, pip_dir)
    print(f"FINAL FAILED PACKAGES = {whl_failed_pkg_list + tar_failed_pkg_list}")
    os.chdir(root_dir)


def handle_packages_set_with_retry(pkg_list, pip_executable, python_executable, pip_dir):
    install_failed_package_list = []
    for package in pkg_list:
        os.chdir(pip_dir)
        try:
            handle_install_single_package(pip_executable, python_executable, pip_dir, package)
        except Exception as e:
            os.chdir(pip_dir)
            print(str(e))
            install_failed_package_list.append(package)

    res_failed_list = []
    for package in install_failed_package_list:
        try:
            handle_install_single_package(pip_executable, python_executable, pip_dir, package)
        except Exception as e:
            os.chdir(pip_dir)
            print(str(e))
            res_failed_list.append(package)

    return res_failed_list


def handle_install_single_package(pip_executable, python_executable, pip_dir, package):
    if '.whl' in package:
        command = [pip_executable, "install", "--no-index", "--find-links=" + pip_dir + "/.", package]
        print(f"Running command: {' '.join(command)}, curdir: {os.getcwd()}")
        subprocess.run(command, check=True, capture_output=True,
                       text=True)
    elif '.tar.gz' in package:
        command = "tar -xzf ./%s" % package
        print(f"Running command: {command}, curdir: {os.getcwd()}")
        subprocess.run(command, shell=True, check=True)
        os.chdir('%s/%s' % (pip_dir, package.split(".tar.gz")[0]))
        subprocess.run([python_executable, "setup.py", "install"], check=True,
                       capture_output=True, text=True)
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


def cp_installed_pkgs_platform010(source_dir, target_dir):
    lib_dirs = os.listdir(os.path.join(os.getcwd(), source_dir, 'lib'))

    lib_dir = 'lib64'
    if 'lib64' in lib_dirs:
        python_dir_list = os.listdir(source_dir + '/lib64')
    else:
        python_dir_list = os.listdir(source_dir + '/lib')

    source_site_packages_dir = os.path.join(os.getcwd(), source_dir, lib_dir, python_dir_list[0], 'site-packages')
    for filename in os.listdir(source_site_packages_dir):
        source_file = os.path.join(source_site_packages_dir, filename)
        print(f"now copying file/folder: {source_file} to target path.")
        target_file = os.path.join(target_dir, filename)

        if os.path.isdir(source_file):
            shutil.copytree(source_file, target_file, dirs_exist_ok=True)
        else:
            shutil.copyfile(source_file, target_file)


if __name__ == "__main__":
    if 'linux' in get_os_info():
        install_dnf_packages('packages')
    venv_name = "columbus_work_station_venv"
    create_venv(venv_name)
    activate_venv(venv_name)
    install_packages('pip_packages', venv_name)
    cp_installed_pkgs_platform010(venv_name, "/usr/local/fbcode/platform010/lib/python3.10/site-packages")
