#!/bin/bash

# Exit on any error
set -e

# ==============================================================================
# CONFIGURATION VARIABLES
# ==============================================================================
# Change these values before deploying
DB_NAME="fitness_freaks_db"
DB_USER="fitness_user"
DB_PASS="SecureSecretPasswordChangeMe123!"

DOMAIN="fitnessfreak.exarth.com"
ADMIN_EMAIL="mark@exarth.com"

# The Git SSH URL of your repository
GIT_REPO="git@github.com:IkramKhan-DevOps/fitness-freaks.git"
PROJECT_DIR_NAME="fitness-freaks"

# Server info
SYSTEM_USER="ubuntu"
PROJECT_BASE_DIR="/home/$SYSTEM_USER"
PROJECT_DIR="$PROJECT_BASE_DIR/$PROJECT_DIR_NAME"
# ==============================================================================

# Ensure the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run this script as root (e.g., using sudo)."
  exit 1
fi

echo "========================================="
echo "1. System Update & Installing Dependencies"
echo "========================================="
apt update
apt install -y python3-venv python3-dev libpq-dev postgresql postgresql-contrib nginx curl git build-essential ufw

echo "========================================="
echo "2. Setting up PostgreSQL Database & User "
echo "========================================="
# Check if DB user exists, create if not
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1 || \
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"

# Check if DB exists, create if not
sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1 || \
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"

# Adjust user settings and grants for Django
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET timezone TO 'UTC';"

# Assign ownership of the database
sudo -u postgres psql -c "ALTER DATABASE $DB_NAME OWNER TO $DB_USER;"

# Connect to the DB and grant schema permissions (fixes PostgreSQL 15+ issues)
sudo -u postgres psql -d "$DB_NAME" -c "GRANT ALL PRIVILEGES ON SCHEMA public TO $DB_USER;"

echo "========================================="
echo "3. Code Setup (Git Clone)"
echo "========================================="
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Cloning repository..."
    # Warning about SSH agent
    echo "IMPORTANT: The script is cloning via SSH. The SSH deploy key must be set for '$SYSTEM_USER'."
    
    # We clone as the system user (ubuntu) to ensure proper ownership
    if ! sudo -u "$SYSTEM_USER" git clone "$GIT_REPO" "$PROJECT_DIR"; then
        echo "Failed to clone repository. Make sure your SSH keys are configured correctly on the AWS instance."
        exit 1
    fi
else
    echo "Directory $PROJECT_DIR already exists."
    echo "Pulling latest changes..."
    # Force git pull
    sudo -u "$SYSTEM_USER" bash -c "cd $PROJECT_DIR && git pull origin main || git pull origin master"
fi

echo "========================================="
echo "4. Virtual Environment & Dependencies"
echo "========================================="
sudo -u "$SYSTEM_USER" bash -c "cd $PROJECT_DIR && python3 -m venv venv"

# Install packages
sudo -u "$SYSTEM_USER" bash -c "cd $PROJECT_DIR && source venv/bin/activate && pip install --upgrade pip"
sudo -u "$SYSTEM_USER" bash -c "cd $PROJECT_DIR && source venv/bin/activate && pip install -r requirements.txt"

# Ensure gunicorn and psycopg2 are installed
sudo -u "$SYSTEM_USER" bash -c "cd $PROJECT_DIR && source venv/bin/activate && pip install gunicorn psycopg2-binary"

echo "========================================="
echo "5. Django Project Setup & .env Generation"
echo "========================================="
ENV_FILE="$PROJECT_DIR/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "Generating new .env file at $ENV_FILE from docs/configs/.env.production"
    sudo -u "$SYSTEM_USER" cp "$PROJECT_DIR/docs/configs/.env.production" "$ENV_FILE"
    
    # Generate a secure random Django secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    
    # Inject script variables to ensure DB config stays perfectly synced with the Postgres setup
    sudo -u "$SYSTEM_USER" sed -i "s|^SECRET_KEY=.*|SECRET_KEY='$SECRET_KEY'|g" "$ENV_FILE"
    sudo -u "$SYSTEM_USER" sed -i "s|^DOMAIN=.*|DOMAIN=$DOMAIN|g" "$ENV_FILE"
    sudo -u "$SYSTEM_USER" sed -i "s|^DB_NAME=.*|DB_NAME=$DB_NAME|g" "$ENV_FILE"
    sudo -u "$SYSTEM_USER" sed -i "s|^DB_USER=.*|DB_USER=$DB_USER|g" "$ENV_FILE"
    sudo -u "$SYSTEM_USER" sed -i "s|^DB_PASS=.*|DB_PASS=$DB_PASS|g" "$ENV_FILE"
else
    echo ".env file already exists. Skipping auto-generation."
fi

# Run Makemigrations, Migrate and Collectstatic
sudo -u "$SYSTEM_USER" bash -c "cd $PROJECT_DIR && source venv/bin/activate && python manage.py makemigrations"
sudo -u "$SYSTEM_USER" bash -c "cd $PROJECT_DIR && source venv/bin/activate && python manage.py migrate"
sudo -u "$SYSTEM_USER" bash -c "cd $PROJECT_DIR && source venv/bin/activate && python manage.py collectstatic --noinput"

# Create superuser if it doesn't already exist
sudo -u "$SYSTEM_USER" bash -c "cd $PROJECT_DIR && source venv/bin/activate && python manage.py shell -c \"
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='mark@exarth.com').exists():
    User.objects.create_superuser(username='mark', email='mark@exarth.com', password='mark')
    print('Superuser created: mark@exarth.com')
else:
    print('Superuser already exists, skipping.')
\""

echo "========================================="
echo "6. Configuring Gunicorn Systemd"
echo "========================================="

# Create Gunicorn socket
cat << 'EOF' > /etc/systemd/system/gunicorn.socket
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
EOF

# Create Gunicorn service
cat << EOF > /etc/systemd/system/gunicorn.service
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=$SYSTEM_USER
Group=www-data
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/gunicorn \\
          --access-logfile - \\
          --workers 3 \\
          --bind unix:/run/gunicorn.sock \\
          root.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# Start and enable Gunicorn
systemctl daemon-reload
systemctl start gunicorn.socket
systemctl enable gunicorn.socket
systemctl restart gunicorn  # Ensures it's using the latest code/venv

echo "========================================="
echo "7. Configuring Nginx"
echo "========================================="
NGINX_CONF="/etc/nginx/sites-available/$PROJECT_DIR_NAME"

cat << EOF > $NGINX_CONF
server {
    listen 80;
    server_name $DOMAIN;

    location = /favicon.ico { access_log off; log_not_found off; }
    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
EOF

# Enable the Nginx site
ln -sf $NGINX_CONF /etc/nginx/sites-enabled/
# Remove the default nginx config if exists
rm -f /etc/nginx/sites-enabled/default

# Test and reload Nginx
nginx -t
systemctl restart nginx

# Ensure firewall allows Nginx Full
ufw allow 'Nginx Full'
ufw allow 'OpenSSH'
ufw --force enable

echo "========================================="
echo "8. Setting up SSL with Let's Encrypt"
echo "========================================="
# Install Certbot via snap (Ubuntu standard way)
snap install core; snap refresh core
snap install --classic certbot
ln -sf /snap/bin/certbot /usr/bin/certbot

# Request Certificate and update Nginx configs automatically
echo "Attempting to run Certbot. (This will fail gracefully if the DNS isn't pointed yet)"
certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m $ADMIN_EMAIL || echo "Certbot check skipped or failed. Run 'sudo certbot --nginx' manually once DNS A records point to your instance."

echo "========================================="
echo "Deployment Setup Complete!"
echo "Your Django project server configurations are applied. Check https://$DOMAIN"
echo "========================================="
