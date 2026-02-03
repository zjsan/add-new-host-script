import platform
import subprocess
from pathlib import Path


def get_hosts_path():

    DEBUG = True

    if DEBUG:

        # .parent gets the root directory of the project for the test hosts file
        # for development testing purposes
        #PROJECT_ROOT = Path(__file__).resolve().parent.parent

        return Path("/mnt/c/temp_test/hosts.txt")

    system = platform.system()

    #actual hosts file paths
    if system == "Windows":
        return Path(r"C:\Windows\System32\drivers\etc\hosts")
    elif system in ("Linux", "Darwin"):
        return Path("/etc/hosts")
    raise RuntimeError("Unsupported OS for now")
    

def read_hosts_file():

    HOSTS_PATH = get_hosts_path()

    try:
        content = HOSTS_PATH.read_text(encoding="utf-8")
        return content.splitlines(keepends=True)
    except FileNotFoundError:
        return []


def write_hosts_file(lines):

    HOSTS_PATH = get_hosts_path()

    #create a backup before writing
    backup_path = HOSTS_PATH.with_suffix(".bak")

    try:
        #cheeck if backup already exists before creating
        #back up only the original hosts file once
        if not backup_path.exists():
            # Check if original exists first
            if HOSTS_PATH.exists():
                backup_path.write_text(
                    HOSTS_PATH.read_text(encoding="utf-8"),
                    encoding="utf-8"    
                )
            else:
                
                backup_path.write_text("# Initial Hosts File Created by Tool\n", encoding="utf-8")

    except Exception as e:
        print(f"\n Failed to create backup: {e}")
        print(" Aborting to prevent potential data loss.")
        return False

    with HOSTS_PATH.open("w", encoding="utf-8", newline="") as file:
        file.writelines(lines)

    return True

def host_exist(domain,lines):

    #remove whitespace and comments
    for line in lines:
        clean = line.strip()

        #skip empty lines and comments
        if clean and not clean.startswith("#"):

            #split line into whiteespaces
            #check if domain exists in a token, not substring
            if domain in clean.split():
                return True

    return False

def dnsflush():
    try:

        #flush DNS cache on Windows
        subprocess.run(
        ["ipconfig", "/flushdns"],
        check=True,         # Raise an exception if the command fails
        shell=True,         # Required to interpret "ipconfig /flushdns" correctly as a single command
        )
        print("DNS cache flushed successfully.")
    except Exception as e:
        print(f"Failed to flush DNS cache: {e}")


def add_host_entry(ip, domain):

    lines = read_hosts_file()#read the file

    #check if host already exists
    if host_exist(domain,lines):
        return False #host already exists

    #ensure the file ends with a newline before appending
    if lines and not lines[-1].endswith('\n'):
        lines[-1] += '\n'

    lines.append(f"{ip}\t{domain}\n")

    return write_hosts_file(lines)#write back to file for the new host addition

def remove_host_entry(domain):

    lines = read_hosts_file()
    new_lines = []#list to hold lines after removal

    removed = False

    #iterate through lines and filter out the one to remove
    for line in lines:

        #remove whitespace and comments
        clean = line.strip()

        #skip empty line and comments
        #aand check if domain exists in line
        if clean and not clean.startswith("#") and domain in clean.split():
            removed = True
            continue
        new_lines.append(line)

    #write only if something was removed
    if removed:
        # if the domain was found write the cleaned list
        return write_hosts_file(new_lines)
    return removed
        

