#!/bin/bash

# Exit on any error
set -e

# ==============================================================================
# CONFIGURATION VARIABLES
# ==============================================================================
PROJECT_DIR_NAME="fitness-freaks"
SYSTEM_USER="ubuntu"
PROJECT_DIR="/home/$SYSTEM_USER/$PROJECT_DIR_NAME"
# ==============================================================================

echo "Starting Application Update..."

# It's safest to run this script as root so it can restart the systemd service at the end.
# If run as root, execute git and python commands as the unprivileged user snippet.
if [ "$EUID" -eq 0 ]; then
  EXEC_AS="sudo -u $SYSTEM_USER"
else
  EXEC_AS=""
fi

# Ensure the directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Error: Directory $PROJECT_DIR does not exist."
    exit 1
fi

cd "$PROJECT_DIR"

echo "========================================="
echo "1. Pulling Latest Changes from Git"
echo "========================================="
# Force pull to ensure latest
$EXEC_AS git pull origin main || $EXEC_AS git pull origin master

echo "========================================="
echo "2. Activating Env & Installing Requirements"
echo "========================================="
$EXEC_AS bash -c "source venv/bin/activate && pip install -r requirements.txt"

echo "========================================="
echo "3. Running Migrations & CollectStatic"
echo "========================================="
$EXEC_AS bash -c "source venv/bin/activate && python manage.py makemigrations accounts core finance whisper"
$EXEC_AS bash -c "source venv/bin/activate && python manage.py migrate"
$EXEC_AS bash -c "source venv/bin/activate && python manage.py collectstatic --noinput"

echo "========================================="
echo "4. Running Tests"
echo "========================================="
$EXEC_AS bash -c "source venv/bin/activate && python manage.py test"

echo "========================================="
echo "5. Restarting Gunicorn Server"
echo "========================================="
if [ "$EUID" -ne 0 ]; then
  echo "You are not root. Attempting to use sudo to restart Gunicorn..."
  sudo systemctl restart gunicorn
else
  systemctl restart gunicorn
fi

echo "========================================="
echo "Update Complete! The application has been restarted seamlessly."
echo "========================================="
