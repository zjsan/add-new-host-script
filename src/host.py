import platform
import subprocess
import re
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

    #check orignal host if exists
    if not HOSTS_PATH.exists():
        print(" CRITICAL ERROR: Windows 'hosts' file is missing from the system.")
        print(f" Expected path: {HOSTS_PATH}")
        print(" This may indicate a system error or OS corruption. Aborting.")
        return False
    
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
            
        #perform the write operation
        with HOSTS_PATH.open("w", encoding="utf-8", newline="") as file:
            file.writelines(lines)

        return True

    except Exception as e:
        print(f"\n Failed to create backup: {e}")
        print(" Aborting to prevent potential data loss.")
        return False


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
        print(" DNS cache flushed successfully.")
    except Exception as e:
        print(f" Failed to flush DNS cache: {e}")


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


def fix_glued_entries(ip, domain):

    HOSTS_PATH = get_hosts_path()
    case1 = False
    case2 = False

    try: 
        content = HOSTS_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(" CRITICAL ERROR: Windows 'hosts' file is missing from the system.")
        return False

    #escape IP and domain for regex operations
    #considering special characters for the domain and IP
    escapeIP = re.escape(ip)
    escapeDomain = re.escape(domain)

    #Regex pattern seperately created to address specific glued entry scenerios

    #the pattern to search for glued entries, ensuring the IP is not preceded by whitespace and the domain is a separate token
    #it looks for for valid domain, junk characters, then the IP and domain without proper separation
    #sample pattern: "0.0.0.1 mssplus.mcafee.comn13.251.136.207tapp.sdg-dashboard.com" "mssplus.mcafee.com13.251.136.207 app.sdg-dashboard.com"
    pattern1 = rf"([a-zA-Z0-9\.-]+?)([nt]*)({escapeIP})([\snt]*)({escapeDomain})"
    replacement1 = r"\1\n\3\t\5"

    #pattern to match valid IP addresses (IPv4) for the regex search
    #sample pattern: "127.0.0.113.251.136.207"
    pattern2 = r"(?:\d{1,3}\.){3}\d{1,3}"
    replacement2 = r"\1\n\2"

    #condition checks for the patterns
    if pattern_exists(pattern1, content, replacement1):
        case1 = True
        print(" Case 1: Glued entries with domain followed by IP found and fixed.")
        return case1
    elif pattern_exists(pattern2, content, replacement2):
        case2 = True
        print(" Case 2: Glued entries with valid IP addresses found and fixed.")
        return case2

    else:
        print(" RegEx search completed. Can't find any glued entries matching the defined patterns.")
        return False

    def pattern_exists(pattern, content, replacement):
        #start searching the pattern from the file
        if re.search(pattern, content,replacement):

            #if found, replace with the correct format (newline before the IP and domain)
            #rebuilding the line and disregarding the junk characters in between

            fixed_content = re.sub(pattern, replacement, content)

            new_lines = fixed_content.splitlines(keepends=True)#split fixed lines while keeping newline characters

            if write_hosts_file(new_lines):
                return True

        print(" No glued entries found")
        return False



      




        

