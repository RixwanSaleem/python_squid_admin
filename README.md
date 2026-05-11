# Squid Admin Web-panel

A small FastAPI-based administration UI for managing Squid proxy service and firewall rules on a Linux host.

## Project Overview

This project provides:

- Login page for administrator authentication
- Dashboard showing Squid installation and service status
- Controls to install, start, stop, restart, and uninstall Squid
- Firewall port management using `firewall-cmd`
- Squid configuration editor for `/etc/squid/squid.conf`

## Files

- `main.py` - FastAPI application logic
- `templates/login.html` - login page template
- `templates/dashboard.html` - admin dashboard template
- `var/` - included folder in repository (unused by current app)

## Requirements

- Python 3.9+
- FastAPI
- Uvicorn or another ASGI server
- `squid` package managed via `dnf`
- `firewalld` and `firewall-cmd`
- Systemd for controlling the Squid service

## Required System Packages
dnf install epel-release -y
dnf install python3 python3-pip python3-devel gcc httpd-tools certbot firewalld openssl -y



## Environment Variables

The application reads these environment variables:

- `SESSION_SECRET` - secret key for session middleware
- `ADMIN_USER` - admin login username (default: `admin`)
- `ADMIN_PASS` - admin login password (default: `password`)

> Important: for production, set a strong `SESSION_SECRET` and do not use default credentials.

## Running the Application

Install Python dependencies if needed:

```bash
python -m pip install fastapi uvicorn
```

Start the app:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Then open:

```text
http://localhost:8000/login
```

## Usage

1. Log in with the configured admin credentials.
2. Use the dashboard to view Squid status and installed state.
3. Install Squid if not already installed.
4. Start, stop, or restart the Squid service.
5. Add or remove firewall ports.
6. Edit and save `/etc/squid/squid.conf` directly from the dashboard.

## Security Notes

- The app uses a simple session-based login and stores credentials in environment variables.
- The default credentials are insecure; update `ADMIN_USER`/`ADMIN_PASS` before deployment.
- Directly editing `/etc/squid/squid.conf` and executing system commands from a web UI carries risk — only run on trusted hosts.


## Structure Setup

mkdir -p /opt/squid-panel/python_squid_admin/var
cd /opt/squid-panel/python_squid_admin
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn python-multipart jinja2

## Create the Environment File
nano /etc/squid-panel.env

SESSION_SECRET=SQUID_SECRET_CHANGE_ME
ADMIN_USER=admin
ADMIN_PASS=YourSecurePassword

SQUID_CONF=/etc/squid/squid.conf
SQUID_SERVICE=squid
SQUID_PORT=3128

## firewall 
firewall-cmd --permanent --add-port=8444/tcp
firewall-cmd --reload

## Create the Environment File
nano /etc/squid-panel.env

SESSION_SECRET=SQUID_SECRET_CHANGE_ME
ADMIN_USER=admin
ADMIN_PASS=YourSecurePassword

SQUID_CONF=/etc/squid/squid.conf
SQUID_SERVICE=squid
SQUID_PORT=3128

## Configure the Systemd Service
nano /etc/systemd/system/squid-panel.service

[Unit]
Description=Squid Proxy Manager
After=network.target

[Service]
WorkingDirectory=/opt/squid-panel/python_squid_admin
EnvironmentFile=/etc/squid-panel.env
ExecStart=/opt/squid-panel/python_squid_admin/venv/bin/uvicorn main:app \
    --host 0.0.0.0 \
    --port 8444 \
    --ssl-certfile /etc/letsencrypt/live/YOUR-DOMAIN.COM/fullchain.pem \
    --ssl-keyfile /etc/letsencrypt/live/YOUR-DOMAIN.COM/privkey.pem
Restart=always
User=root

[Install]
WantedBy=multi-user.target


## Service start
systemctl enable --now squid-panel
systemctl restart squid-panel



## Author 

Rizwan Saleem


