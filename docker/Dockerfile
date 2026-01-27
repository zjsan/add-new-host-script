# Use a lightweight Windows Python image
FROM python:3.10-windowsservercore-ltsc2022

# Set working directory
WORKDIR /app

# Install PyInstaller
RUN pip install pyinstaller

# Copy source code
COPY src/ .

# Command to build the executable
# --onefile: Bundles everything into one .exe
# --uac-admin: Forces the .exe to request Admin rights when opened
# --name: The output filename
CMD pyinstaller ^
  --onefile ^
  --uac-admin ^
  --clean ^
  --name AppSetupTool ^
  main.py
# The resulting executable will be in the dist/ directory