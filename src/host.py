import platform
from pathlib import Path

def get_hosts_path():
    system = platform.system()

    if system == "Windows":
        return Path(r"C:\Windows\System32\drivers\etc\hosts")

    raise RuntimeError("Unsupported OS for now")
    

def read_hosts_file():

    HOSTS_PATH = get_hosts_path()

    with HOSTS_PATH.open("r", encoding="utf-8") as file:
        return file.readlines()


def write_hosts_file(lines):

    HOSTS_PATH = get_hosts_path()
    
    with HOSTS_PATH.open("w", encoding="utf-8") as file:
        file.writelines(lines)

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

    lines = read_hosts_file()#read the file

    #check if host already exists
    if host_exist(domain,lines):

        print(f"Host entry for {domain} already exists.")
        return False #host already exists

    lines.append(f"{ip}\t{domain}\n")

    write_hosts_file(lines)#write back to file for the new host addition

    return True

def remove_host_entry(domain):

    lines = read_hosts_file()
    new_lines = []#list to hold lines after removal

    removed = False

    #iterate through lines and filter out the one to remove

    for line in lines:

        #remove whitespace and comments
        clean = line.strip()

        #skip empty line and comments
        if clean and not clean.startswith("#") and domain in clean.split():
            removed = True
            continue
        new_lines.append(line)

    #write only if something was removed
    if removed:
        write_hosts_file(new_lines)#write back to file after removal
        return True
    
    return removed
        

