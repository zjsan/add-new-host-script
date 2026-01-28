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

def host_exist(domain,lines):

    #remove whitespace and comments
    for line in lines:
        clean = line.strip()

        #skip empty lines and comments
        if clean and not clean.startswith("#"):

            #split line into whiteespaces
            #check if domain exists in a token, not substring
            if domain in clean.split():
                return True.
    return False

def add_host_entry(ip, domain):

    line = read_hosts_file()#read the file

    #check if host already exists
    if host_exist(domain,lines):
        return False #host already exists

    lines.append(f"{ip}\t{domain}\n")


