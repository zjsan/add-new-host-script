# Use a lightweight Windows Python image
FROM python:3.10-windowsservercore-ltsc2022

# Install PyInstaller
RUN pip install pyinstaller

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Set working directory
WORKDIR /app/src

# Command to build the executable
# --onefile: Bundles everything into one .exe
# --uac-admin: Forces the .exe to request Admin rights when opened
# --name: The output filename
CMD ["pyinstaller", "--onefile", "--uac-admin", "--clean", "--name", "SDG_Host_Manager", "main.py"]
# The resulting executable will be in the dist/ directory