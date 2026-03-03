import platform
import subprocess
import re
from pathlib import Path


def get_hosts_path():

    DEBUG = False #set to True for development testing with a test hosts file, False for production use with actual hosts file

    if DEBUG:

        # .parent gets the root directory of the project for the test hosts file
        # for development testing purposes
        #PROJECT_ROOT = Path(__file__).resolve().parent.parent
        if platform.system() == "Windows":
            return Path(r"C:\temp_test\hosts.txt")
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


def host_exist(ip,domain,lines):

    #remove whitespace and comments
    for line in lines:
        clean = line.strip()

        #skip empty lines and comments
        if clean and not clean.startswith("#"):
            
            tokens = line.split()#retrieving ip and domain tokens 
            #check if tokens matches the desired ip and domain 
            if len(tokens) >= 2 and tokens[0] == ip and domain in tokens[1]:
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
    if host_exist(ip,domain,lines):
        return False #host already exists

    #ensure the file ends with a newline before appending
    if lines and not lines[-1].endswith('\n'):
        lines[-1] += '\n'

    lines.append(f"{ip}\t{domain}\n")

    return write_hosts_file(lines)#write back to file for the new host addition

def remove_host_entry(ip,domain):

    lines = read_hosts_file()
    new_lines = []#list to hold lines after removal

    removed = False

    #iterate through lines and filter out the one to remove
    for line in lines:

        #remove whitespace and comments
        clean = line.strip()

        #skip empty line and comments
        #aand check if domain exists in line
        if clean and not clean.startswith("#"):
            tokens = line.split()#retrieving ip and domain tokens
            print(tokens)
            if len(tokens) >=2 and tokens[0] == ip and domain in tokens[1]:
                removed = True
                continue
        new_lines.append(line)

    #write only if something was removed
    if removed:
        # if the domain was found write the cleaned list
        return write_hosts_file(new_lines)
    return removed


def fix_glued_entries(ip, domain):
            
    try: 
        lines = read_hosts_file()
        content = "".join(lines)
    except FileNotFoundError:
        print(" CRITICAL ERROR: Windows 'hosts' file is missing from the system.")
        return False

    #escape IP and domain for regex operations
    #considering special characters for the domain and IP
    escaped_ip = re.escape(ip)
    escaped_domain = re.escape(domain)

    #reusable patterns 
    ip_pattern = r"(?:\d{1,3}\.){3}\d{1,3}"
    domain_pattern = r"(?=[^ \n]*[a-zA-Z])[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+"

    #Glued Patterns
    #changed if-else codntion to dictionary of patters for better readability and maintainability
    patterns = [
        {
            "name": "Domain + literal n + IP + literal t + Domain",
            "pattern": rf"((?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{{2,}})n({escaped_ip})t(\S+)",#specific pattern for the glued entry with literal 'n' and 't' between domain and IP
            "replacement": r"\1\n\2\t\3"
        },
        {
            "name": "IP glued to another IP",
            "pattern": rf"\b({ip_pattern})({escaped_ip})\b",
            "replacement": r"\1\n\2"
        },
        {
            "name": "Domain glued to IP",
            "pattern": rf"({domain_pattern})({escaped_ip})",
            "replacement": r"\1\n\2"
        },
        {
            "name": "IP glued to Domain",
            "pattern": rf"({escaped_ip})({domain_pattern})",
            "replacement": r"\1\n\2"
        },
        {
            "name": "IP + whitespace + IP + whitespace + Domain",
            "pattern": rf"({ip_pattern})\s+({escaped_ip})\s+({domain_pattern})",
            "replacement": r"\1\n\2\t\3"
        },
        {
            "name": "IP + Domain + whitespace + IP + whitespace + Domain",
            "pattern": rf"({ip_pattern})\s+({domain_pattern})\s+({escaped_ip})\s+({domain_pattern})",
            "replacement": r"\1\t\2\n\3\t\4"
        },
      
    ]   

    #loop through patters and search for the matches

    for entry in patterns: 
        print(f" Checking pattern: {entry['name']}")

        #perform the replacement to fix the glued entries
        fixed_content,count = re.subn(entry["pattern"], entry["replacement"], content, count=1)
        
        #if matched found and replacement was made, write the fixed content back to the file
        if count > 0: 
            #start searching for the pattern in the content
            print(f" Match found: {entry['name']}")

            #appending the fixed content ensuring proper newlines are maintained
            new_lines = fixed_content.splitlines(keepends=True)

            #calling write function to update the file
            if write_hosts_file(new_lines):
                print(f" Successfully fixed glued entries for pattern: {entry['name']}")
                return True
            else:
                print(f" Failed to write fixed content for pattern: {entry['name']}")
                return False
    return False #no patterns matched, no fixes applied
   
def restore_hosts():
    HOSTS_PATH = get_hosts_path()
    backup_path = HOSTS_PATH.with_suffix(".bak")

    if not backup_path.exists():
        print(" No backup found to restore.")
        print(" Creating a backup of the current hosts file")

        # Check if original exists first
        if HOSTS_PATH.exists():
                backup_path.write_text(
                    HOSTS_PATH.read_text(encoding="utf-8"),
                    encoding="utf-8"    
                )
        print(" Backup created successfully. No changes made to hosts file.")
        print(" Please run the restore option again to restore from the newly created backup if needed.")        
        return False
    
    try:
        #read backup content and write it back to the hosts file
        content = backup_path.read_text(encoding="utf-8")
        HOSTS_PATH.write_text(content, encoding="utf-8")
        return True
    except Exception as e:
        print(f" Failed to restore hosts file from backup: {e}")
        return False

      
def file_contents():
    contents = read_hosts_file()

    if contents:
        print("\n Current hosts file content: \n")
        for line in contents:
            print(line, end="")
        return True
    else:
        print(" Hosts file is empty or missing.")
        return False
        

