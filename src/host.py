import platform
from pathlib import Path

def get_hosts_path():
    system = platform.system()

    if system == "Windows":
        return Path(r"C:\Windows\System32\drivers\etc\hosts")

    raise RuntimeError("Unsupported OS for now")
    

def read_hosts_file():
    with open(get_hosts_path(), "r") as f:
        return f.read()

def host_exist()