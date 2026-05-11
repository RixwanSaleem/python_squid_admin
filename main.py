import os, subprocess, datetime
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

# Configuration
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "password")
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "squid_enterprise_secret"))
templates = Jinja2Templates(directory="templates")

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

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
    if not request.session.get("logged_in"): return RedirectResponse("/login")
    
    is_installed = run_cmd("rpm -q squid").returncode == 0
    status = run_cmd("systemctl is-active squid").stdout.strip()
    fw_status = run_cmd("systemctl is-active firewalld").stdout.strip()
    uptime = run_cmd("uptime -p").stdout.strip()
    open_ports = run_cmd("firewall-cmd --list-ports").stdout.strip().split()
    
    # Network Details
    net_cmd = run_cmd("ip -br -4 addr show").stdout.strip().split("\n")
    interfaces = []
    for line in net_cmd:
        parts = line.split()
        if len(parts) >= 3:
            name = parts[0]
            state = parts[1]
            ip = parts[2]
            mac = run_cmd(f"cat /sys/class/net/{name}/address").stdout.strip()
            interfaces.append({"name": name, "state": state, "ip": ip, "mac": mac})

    config = ""
    if os.path.exists("/etc/squid/squid.conf"):
        with open("/etc/squid/squid.conf", 'r') as f: config = f.read()

    return templates.TemplateResponse(request=request, name="dashboard.html", context={
        "installed": is_installed, "status": status, "fw_status": fw_status, 
        "config": config, "open_ports": open_ports, "interfaces": interfaces,
        "uptime": uptime, "year": datetime.datetime.now().year
    })

@app.post("/manage")
async def manage_squid(action: str = Form(...)):
    if action == "install":
        run_cmd("dnf install squid httpd-tools -y && systemctl enable --now squid")
    elif action == "uninstall":
        run_cmd("systemctl stop squid && dnf remove squid -y")
    else:
        run_cmd(f"systemctl {action} squid")
    return RedirectResponse("/", status_code=303)

@app.post("/server")
async def manage_server(action: str = Form(...)):
    if action == "reboot": run_cmd("reboot")
    elif action == "shutdown": run_cmd("shutdown now")
    return RedirectResponse("/", status_code=303)

@app.post("/firewall-port")
async def manage_ports(action: str = Form(...), port: str = Form(None)):
    if port: run_cmd(f"firewall-cmd --permanent --{action}-port={port} && firewall-cmd --reload")
    return RedirectResponse("/", status_code=303)

@app.post("/save-config")
async def save_config(config_text: str = Form(...)):
    with open("/etc/squid/squid.conf", 'w') as f: f.write(config_text)
    run_cmd("systemctl restart squid")
    return RedirectResponse("/", status_code=303)
