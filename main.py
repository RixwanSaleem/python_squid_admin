import os
import subprocess
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

# Configuration from Environment (setup by systemd EnvironmentFile)
SESSION_SECRET = os.getenv("SESSION_SECRET", "squid_secret_fallback")
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "password")

app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)
templates = Jinja2Templates(directory="templates")

# Paths
SQUID_CONF = "/etc/squid/squid.conf"

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def is_logged_in(request: Request):
    return request.session.get("logged_in") == True

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html", context={})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USER and password == ADMIN_PASS:
        request.session["logged_in"] = True
        return RedirectResponse(url="/", status_code=303)
    return RedirectResponse(url="/login?error=1", status_code=303)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login")

@app.get("/")
async def dashboard(request: Request):
    if not is_logged_in(request):
        return RedirectResponse(url="/login")
    
    # Squid Info
    is_installed = run_cmd("rpm -q squid").returncode == 0
    status = run_cmd("systemctl is-active squid").stdout.strip()
    
    # Firewall Info
    fw_cmd = run_cmd("firewall-cmd --list-ports")
    open_ports = fw_cmd.stdout.strip().split()

    # Config Content
    config_content = ""
    if os.path.exists(SQUID_CONF):
        with open(SQUID_CONF, 'r') as f:
            config_content = f.read()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "installed": is_installed, 
            "status": status, 
            "config": config_content,
            "open_ports": open_ports
        }
    )

@app.post("/manage")
async def manage_squid(request: Request, action: str = Form(...)):
    if not is_logged_in(request): raise HTTPException(401)
    if action == "install":
        run_cmd("dnf install squid httpd-tools -y")
        run_cmd("systemctl enable --now squid")
    elif action == "uninstall":
        run_cmd("systemctl stop squid && dnf remove squid -y")
    else:
        run_cmd(f"systemctl {action} squid")
    return RedirectResponse("/", status_code=303)

@app.post("/save-config")
async def save_config(request: Request, config_text: str = Form(...)):
    if not is_logged_in(request): raise HTTPException(401)
    with open(SQUID_CONF, 'w') as f:
        f.write(config_text)
    run_cmd("systemctl restart squid")
    return RedirectResponse("/", status_code=303)

@app.post("/firewall")
async def manage_firewall(request: Request, action: str = Form(...), port: str = Form(None)):
    if not is_logged_in(request): raise HTTPException(401)
    if action == "add" and port:
        run_cmd(f"firewall-cmd --permanent --add-port={port}")
    elif action == "remove" and port:
        run_cmd(f"firewall-cmd --permanent --remove-port={port}")
    run_cmd("firewall-cmd --reload")
    return RedirectResponse("/", status_code=303)
