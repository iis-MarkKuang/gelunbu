import subprocess
import platform
import sys


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


def get_architecture():
    machine = platform.machine().lower()
    if machine in ("x86_64", "amd64"):
        return "x86_64"
    elif machine in ("arm64", "aarch64"):
        return "arm64"
    elif machine in ("i386", "i686"):
        return machine  # i386 or i686
    else:
        return "unknown"


# --no-deps is by default
def download_pip_packages(pip_dept_file_path, target_folder, pypi_index):
    if not pypi_index or pypi_index == "":
        pypi_index = "https://pypi.tuna.tsinghua.edu.cn/simple"
    os_info = get_os_info()
    arch_info = get_architecture()

    if os_info == "unknown" or arch_info == "unknown":
        print("Unsupported OS or architecture")
        sys.exit(1)

    command = [sys.executable, "-m", "pip", "download", "--platform", os_info + "_" + arch_info, "--no-deps",
               "-r", pip_dept_file_path, "-d", target_folder, "-i", pypi_index]
    print(f"Running command: {' '.join(command)}")
    subprocess.run(command, check=True)


def download_dnf_packages(target_folder):
    dept_list = ["gcc-c++", "python3-devel"]
    for dept in dept_list:
        command = ["dnf", "install", dept, "--downloadonly", "--downloaddir", "=", target_folder]
        print(f"Running command: {' '.join(command)}")
        subprocess.run(command, check=True)


if __name__ == "__main__":
    dep_target_folder = './packages'
    download_dnf_packages(dep_target_folder)
    download_pip_packages('./requirements_station.txt', target_folder, "")

