# SDG Host Tool Manager

A robust, self-healing Windows utility designed to manage host file entries safely. This tool automates the process of adding, removing, and repairing `hosts` file entries with built-in backup and restoration features.
Operations include, adding of fixed host, remove host, fix glued entries, backup/restore, and viewing the host file contents.

## Key Features

- **Safe Modifications:** Automatically creates a `.bak` backup before any write operation.
- **Self-Healing:** Uses Regex patterns to detect and fix "glued" or malformed entries.
- **DNS Integration:** Automatically flushes the Windows DNS cache after changes.
- **Safety First:** Includes confirmation prompts for destructive actions (Restore/Remove).
- **OS Aware:** Integrated UAC manifest to ensure Administrative privileges.

## Project Structure

- `src/` - Python source code (`main.py`, `host.py`).
- `docker/` - Linux-based development environment (for logic testing).
- `dist/` - Contains the compiled standalone `.exe` (after build).
- `requirements.txt` - Project dependencies (PyInstaller).

## Development Environment Setup

This project is designed to run in a Dockerized Linux environment to ensure consistency across Windows, macOS, and Linux. We use Docker Compose to handle volume mapping for testing.

Prerequisites

- **Docker Desktop** (ensure it is set to use the WSL 2 based engine).

- **WSL 2 installed** (Ubuntu/Debian recommended).
  1. Local Machine Preparation

     For development and testing, the script looks for a "test" hosts file to avoid accidentally modifying your system files.
  - Create a folder: C:\temp_test
  - Create a file named hosts.txt inside that folder.
  - Add some dummy data to hosts.txt for testing purposes.
  2. Running the Program (Docker)

     We use a separate "builder" service to interact with the CLI menu.
  - Build and Start the Container: **docker compose up -d --build**
  - Interact with the Menu: **docker compose run --rm builder**
  3. Understanding the Environment Logic

     The program automatically detects its environment and adjusts paths accordingly:

     | Environment    | Mode  | Path Used                             |
     | -------------- | ----- | ------------------------------------- |
     | Docker (WSL)   | Debug | /mnt/c/temp_test/hosts.txt            |
     | Native Windows | Debug | C:\temp_test\hosts.txt                |
     | Production     | Live  | C:\Windows\System32\drivers\etc\hosts |

  4. Common Troubleshooting
  - **Invalid Volume Specification:** If you get an error regarding **C:/**, ensure you are running the command from a WSL terminal. The docker-compose.yml uses /mnt/c/ syntax for compatibility.

  - **Permission Denied:** If the script cannot write to the hosts file, ensure hosts.txt is not "Read-only" in Windows.

Note: Set **DEBUG** to True for development mode and comment out the " is not is_admin()" block in the main.py.

## Production Build (Windows EXE)

Because Windows Home restricts Windows Containers, and PyInstaller requires a local file system, follow these steps exactly:

1.  Migrate to Local Filesystem

Move the project from WSL to a native Windows directory to avoid UNC path errors:

    # Run this in your WSL terminal
    mkdir -p /mnt/c/projects
    cp -r ~/add-host-script /mnt/c/projects/

2.  Build the Executable

Open PowerShell navigate in C:\projects\add-host-script and run:

    # 1. Create Virtual Environment
    python -m venv venv

    # 2. Enable Script Execution (if disabled)
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
    Note: Press Y after if prompted

    # 3. Activate Environment
    .\venv\Scripts\Activate.ps1

    # 4. Install Dependencies
    pip install -r requirements.txt

    # 5. Generate EXE
    .\venv\Scripts\pyinstaller.exe --onefile --uac-admin --clean --name SDG_Host_Manager src\main.py

The final executable will be located in the dist/ folder.

Note: If `pip list` shows a package but the .exe is missing from .\venv\Scripts\, perform a force reinstall:

        pip install -r requirements.txt --force-reinstall

## Important Notes for Users

- **Administrator Rights:** The .exe will automatically request Admin privileges (required to write to System32).

- **Antivirus/SmartScreen:** Since this tool modifies system files, Windows SmartScreen may show a warning. Click "More Info" -> "Run Anyway"

- **Backup:** A .bak file is created automatically in the etc/ folder upon first modification of adding the host.
