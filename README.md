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

## Author 

Rizwan Saleem
