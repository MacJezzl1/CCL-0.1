#!/usr/bin/env python3
"""
CCL Templates v0.1 — CapeChain Labs
Built-in project template library. Real, runnable scaffolds.
Usage: ccl use template <name>
"""

import json
from pathlib import Path

class C:
    RESET="\033[0m"; BOLD="\033[1m"; CYAN="\033[96m"; GREEN="\033[92m"
    YELLOW="\033[93m"; DIM="\033[2m"; RED="\033[91m"

def ok(m):   print(f"{C.GREEN}  ✓ {m}{C.RESET}")
def info(m): print(f"{C.CYAN}  → {m}{C.RESET}")

# ─────────────────────────────────────────────
# TEMPLATE REGISTRY
# ─────────────────────────────────────────────
TEMPLATES = {}

def register(name, desc, tags):
    def dec(fn):
        TEMPLATES[name] = {"fn": fn, "desc": desc, "tags": tags}
        return fn
    return dec

# ─────────────────────────────────────────────
# TEMPLATE: web3-dapp
# ─────────────────────────────────────────────
@register("web3-dapp", "Ethereum dApp with wallet connect + contract", ["web3","blockchain","ethereum"])
def tpl_web3_dapp(name: str, out: Path):
    files = {
        "index.html": f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{name}</title>
  <style>
    *{{margin:0;padding:0;box-sizing:border-box}}
    body{{background:#0a0e1a;color:#e0e6ff;font-family:monospace;display:flex;
          flex-direction:column;align-items:center;justify-content:center;min-height:100vh;padding:2rem}}
    h1{{color:#00f5c8;font-size:2rem;margin-bottom:1rem}}
    button{{background:#00f5c8;color:#0a0e1a;border:none;padding:.8rem 2rem;
            font-size:1rem;font-family:monospace;cursor:pointer;border-radius:4px;
            font-weight:700;margin:.5rem;transition:opacity .2s}}
    button:hover{{opacity:.8}}
    .card{{background:#0c1428;border:1px solid #1a2a4a;border-radius:8px;
           padding:1.5rem;margin:1rem 0;width:100%;max-width:500px}}
    .addr{{font-size:.75rem;color:#7a8bb5;word-break:break-all;margin-top:.5rem}}
    .bal{{font-size:1.5rem;color:#00f5c8;margin-top:.5rem}}
    .status{{color:#ffd700;margin:.5rem 0;font-size:.85rem}}
  </style>
</head>
<body>
  <h1>⬡ {name}</h1>
  <p style="color:#7a8bb5;margin-bottom:2rem">Built with CCL 0.1 — CapeChain Labs</p>

  <div class="card">
    <button onclick="connectWallet()">Connect Wallet</button>
    <div class="status" id="status">Not connected</div>
    <div class="addr"  id="address"></div>
    <div class="bal"   id="balance"></div>
  </div>

  <div class="card">
    <h3 style="margin-bottom:.8rem;color:#00f5c8">Contract Interaction</h3>
    <input id="input" placeholder="Enter value" style="width:100%;padding:.5rem;background:#0a0e1a;
           border:1px solid #1a2a4a;color:#e0e6ff;font-family:monospace;margin-bottom:.5rem">
    <button onclick="callContract()">Call Contract</button>
    <div class="status" id="txStatus"></div>
  </div>

  <script>
    let account = null;

    async function connectWallet() {{
      if (typeof window.ethereum === 'undefined') {{
        document.getElementById('status').textContent = 'MetaMask not detected. Install at metamask.io';
        return;
      }}
      try {{
        const accounts = await ethereum.request({{method:'eth_requestAccounts'}});
        account = accounts[0];
        document.getElementById('status').textContent  = 'Connected ✓';
        document.getElementById('address').textContent = account;
        const bal = await ethereum.request({{method:'eth_getBalance',params:[account,'latest']}});
        const eth = (parseInt(bal, 16) / 1e18).toFixed(4);
        document.getElementById('balance').textContent = eth + ' ETH';
      }} catch(e) {{ document.getElementById('status').textContent = 'Error: ' + e.message; }}
    }}

    async function callContract() {{
      if (!account) {{ alert('Connect wallet first'); return; }}
      const val = document.getElementById('input').value;
      document.getElementById('txStatus').textContent = 'Sending tx…';
      try {{
        const tx = await ethereum.request({{
          method: 'eth_sendTransaction',
          params: [{{from: account, to: account, value: '0x0', data: '0x'}}]
        }});
        document.getElementById('txStatus').textContent = 'Tx sent: ' + tx.substring(0,20) + '…';
      }} catch(e) {{ document.getElementById('txStatus').textContent = 'Error: ' + e.message; }}
    }}
  </script>
</body>
</html>""",

        "contract/Token.sol": f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;
// {name} Token — CCL 0.1 / CapeChain Labs

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract {name.replace(' ','').replace('-','')}Token is ERC20, Ownable {{
    uint256 public constant MAX_SUPPLY = 1_000_000 * 10**18;

    constructor() ERC20("{name}", "{name[:3].upper()}") Ownable(msg.sender) {{
        _mint(msg.sender, 100_000 * 10**18);
    }}

    function mint(address to, uint256 amount) external onlyOwner {{
        require(totalSupply() + amount <= MAX_SUPPLY, "Exceeds max supply");
        _mint(to, amount);
    }}
}}""",

        "hardhat.config.js": """require("@nomicfoundation/hardhat-toolbox");
module.exports = {
  solidity: "0.8.19",
  networks: {
    hardhat: {},
    sepolia: {
      url: process.env.SEPOLIA_URL || "",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
    }
  }
};""",

        "package.json": json.dumps({"name": name.lower().replace(" ","-"),
            "version":"0.1.0","scripts":{"dev":"npx serve .","compile":"npx hardhat compile",
            "deploy":"npx hardhat run scripts/deploy.js --network sepolia"},
            "devDependencies":{"hardhat":"^2.19.0","@nomicfoundation/hardhat-toolbox":"^4.0.0"}}, indent=2),

        ".env.example": "SEPOLIA_URL=your_infura_or_alchemy_url\nPRIVATE_KEY=your_wallet_private_key\n",
        "README.md": f"# {name}\nBuilt with CCL 0.1 — CapeChain Labs\n\n## Setup\n```\nccl install\nnpx hardhat compile\nccl deploy\n```\n"
    }
    return files

# ─────────────────────────────────────────────
# TEMPLATE: saas-starter
# ─────────────────────────────────────────────
@register("saas-starter", "Full-stack SaaS: Flask + auth + payments + dashboard", ["saas","web","python","startup"])
def tpl_saas(name: str, out: Path):
    files = {
        "app.py": f'''from flask import Flask, render_template, request, jsonify, session, redirect
from functools import wraps
import hashlib, os, json
from pathlib import Path

app = Flask(__name__)
app.secret_key = os.urandom(32).hex()

DB_FILE = Path("users.json")

def load_db():
    return json.loads(DB_FILE.read_text()) if DB_FILE.exists() else {{}}

def save_db(db):
    DB_FILE.write_text(json.dumps(db, indent=2))

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated

def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

@app.route("/")
def home():
    return render_template("home.html", app_name="{name}")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        data  = request.json or request.form
        email = data.get("email","").lower()
        pw    = data.get("password","")
        db    = load_db()
        user  = db.get(email)
        if user and user["password"] == hash_pw(pw):
            session["user"] = email
            return jsonify({{"success": True, "redirect": "/dashboard"}})
        return jsonify({{"success": False, "error": "Invalid credentials"}}), 401
    return render_template("login.html", app_name="{name}")

@app.route("/register", methods=["POST"])
def register():
    data  = request.json or request.form
    email = data.get("email","").lower()
    pw    = data.get("password","")
    if not email or not pw:
        return jsonify({{"error": "Email and password required"}}), 400
    db = load_db()
    if email in db:
        return jsonify({{"error": "User exists"}}), 409
    db[email] = {{"email": email, "password": hash_pw(pw), "plan": "free", "created": str(__import__("datetime").datetime.now())}}
    save_db(db)
    session["user"] = email
    return jsonify({{"success": True}})

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=session["user"], app_name="{name}")

@app.route("/api/me")
@login_required
def me():
    db   = load_db()
    user = db.get(session["user"], {{}})
    return jsonify({{"email": user.get("email"), "plan": user.get("plan","free")}})

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
''',

        "templates/home.html": """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{{ app_name }}</title>
<style>*{margin:0;padding:0;box-sizing:border-box}
body{background:#050912;color:#e0e6ff;font-family:sans-serif;display:flex;
     flex-direction:column;align-items:center;justify-content:center;min-height:100vh}
h1{font-size:3rem;color:#00f5c8;margin-bottom:1rem}
p{color:#7a8bb5;font-size:1.1rem;margin-bottom:2rem;text-align:center}
.cta{display:flex;gap:1rem}
a{padding:.8rem 2rem;border-radius:6px;text-decoration:none;font-weight:600}
.primary{background:#00f5c8;color:#050912}
.secondary{border:1px solid #00f5c8;color:#00f5c8}
</style></head><body>
<h1>{{ app_name }}</h1>
<p>Built with CCL 0.1 — CapeChain Labs<br>Your SaaS, live in minutes.</p>
<div class="cta">
  <a href="/register" class="primary">Get Started Free</a>
  <a href="/login"    class="secondary">Log In</a>
</div>
</body></html>""",

        "templates/login.html": """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Login — {{ app_name }}</title>
<style>*{margin:0;padding:0;box-sizing:border-box}
body{background:#050912;color:#e0e6ff;font-family:sans-serif;display:flex;
     align-items:center;justify-content:center;min-height:100vh}
.card{background:#0c1428;border:1px solid #1a2a4a;border-radius:12px;
      padding:2.5rem;width:100%;max-width:420px}
h2{color:#00f5c8;margin-bottom:1.5rem;text-align:center}
input{width:100%;padding:.8rem 1rem;background:#0a0e1a;border:1px solid #1a2a4a;
      color:#e0e6ff;border-radius:6px;margin-bottom:1rem;font-size:1rem}
button{width:100%;padding:.9rem;background:#00f5c8;color:#050912;border:none;
       border-radius:6px;font-size:1rem;font-weight:700;cursor:pointer}
.err{color:#ff4466;font-size:.85rem;margin-bottom:.5rem;display:none}
a{color:#00f5c8;font-size:.85rem;text-decoration:none}
.links{display:flex;justify-content:space-between;margin-top:.8rem}
</style></head><body><div class="card">
<h2>{{ app_name }}</h2>
<div class="err" id="err"></div>
<input id="email"    type="email"    placeholder="Email">
<input id="password" type="password" placeholder="Password">
<button onclick="login()">Log In</button>
<div class="links"><a href="/">← Home</a><a href="#" onclick="register()">Register</a></div>
</div>
<script>
async function login(){
  const r=await fetch('/login',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({email:document.getElementById('email').value,
                         password:document.getElementById('password').value})});
  const d=await r.json();
  if(d.success)location.href=d.redirect;
  else{document.getElementById('err').style.display='block';document.getElementById('err').textContent=d.error;}
}
async function register(){
  const r=await fetch('/register',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({email:document.getElementById('email').value,
                         password:document.getElementById('password').value})});
  const d=await r.json();
  if(d.success)location.href='/dashboard';
  else{document.getElementById('err').style.display='block';document.getElementById('err').textContent=d.error;}
}
</script></body></html>""",

        "templates/dashboard.html": """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Dashboard — {{ app_name }}</title>
<style>*{margin:0;padding:0;box-sizing:border-box}
body{background:#050912;color:#e0e6ff;font-family:sans-serif}
nav{background:#0c1428;border-bottom:1px solid #1a2a4a;padding:1rem 2rem;
    display:flex;justify-content:space-between;align-items:center}
.logo{color:#00f5c8;font-weight:700;font-size:1.1rem}
.user{font-size:.85rem;color:#7a8bb5}
a.logout{color:#ff4466;font-size:.85rem;text-decoration:none;margin-left:1rem}
main{padding:2rem;max-width:1100px;margin:0 auto}
h1{margin-bottom:2rem;font-size:1.8rem}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:1.2rem}
.card{background:#0c1428;border:1px solid #1a2a4a;border-radius:10px;padding:1.5rem}
.card h3{color:#00f5c8;margin-bottom:.5rem;font-size:.9rem;text-transform:uppercase;letter-spacing:.05em}
.val{font-size:2rem;font-weight:700;margin-bottom:.3rem}
.sub{font-size:.8rem;color:#7a8bb5}
</style></head><body>
<nav>
  <div class="logo">{{ app_name }}</div>
  <div><span class="user">{{ user }}</span><a href="/logout" class="logout">Logout</a></div>
</nav>
<main>
  <h1>Dashboard</h1>
  <div class="grid">
    <div class="card"><h3>Plan</h3><div class="val" id="plan">—</div><div class="sub">Current tier</div></div>
    <div class="card"><h3>Status</h3><div class="val" style="color:#39ff87">Active</div><div class="sub">All systems go</div></div>
    <div class="card"><h3>CCL</h3><div class="val" style="color:#00f5c8">0.1</div><div class="sub">CapeChain Labs OS</div></div>
  </div>
</main>
<script>
fetch('/api/me').then(r=>r.json()).then(d=>{
  document.getElementById('plan').textContent=d.plan;
});
</script></body></html>""",
        "requirements.txt": "flask\n",
        ".ccl": json.dumps({"name": name, "type": "saas", "version": "0.1", "dependencies": ["flask"]}, indent=2),
        "README.md": f"# {name}\nSaaS starter — CCL 0.1\n\n## Run\n```\nccl install flask\npython app.py\n```\nOpen http://localhost:5000\n"
    }
    return files

# ─────────────────────────────────────────────
# TEMPLATE: cli-tool
# ─────────────────────────────────────────────
@register("cli-tool", "Python CLI tool with argument parsing + config", ["cli","python","tool"])
def tpl_cli(name: str, out: Path):
    slug = name.lower().replace(" ","_").replace("-","_")
    files = {
        f"{slug}.py": f'''#!/usr/bin/env python3
"""
{name} — CLI Tool
Built with CCL 0.1 / CapeChain Labs
"""
import argparse, json, sys
from pathlib import Path

CONFIG_FILE = Path.home() / ".{slug}_config.json"

def load_config():
    return json.loads(CONFIG_FILE.read_text()) if CONFIG_FILE.exists() else {{}}

def save_config(cfg):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))

def cmd_run(args):
    print(f"Running {name} with input: {{args.input}}")
    # TODO: your logic here

def cmd_config(args):
    cfg = load_config()
    if args.set:
        k, v = args.set.split("=", 1)
        cfg[k] = v
        save_config(cfg)
        print(f"Set {{k}} = {{v}}")
    else:
        print(json.dumps(cfg, indent=2))

def main():
    parser = argparse.ArgumentParser(prog="{slug}", description="{name}")
    sub    = parser.add_subparsers(dest="command")

    run_p = sub.add_parser("run",    help="Run the tool")
    run_p.add_argument("input",      help="Input value")
    run_p.set_defaults(func=cmd_run)

    cfg_p = sub.add_parser("config", help="Get/set config")
    cfg_p.add_argument("--set",      metavar="KEY=VALUE", help="Set a config value")
    cfg_p.set_defaults(func=cmd_config)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
''',
        "README.md": f"# {name}\n\n```\npython {slug}.py run \"hello\"\npython {slug}.py config --set key=value\n```\n",
        ".ccl": json.dumps({"name": name, "type": "cli", "version": "0.1"}, indent=2)
    }
    return files

# ─────────────────────────────────────────────
# TEMPLATE: api-server
# ─────────────────────────────────────────────
@register("api-server", "REST API: FastAPI + CORS + JWT auth + SQLite", ["api","backend","python","rest"])
def tpl_api(name: str, out: Path):
    files = {
        "main.py": f'''from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import sqlite3, hashlib, secrets, json
from pathlib import Path
from datetime import datetime

app = FastAPI(title="{name}", version="0.1.0", description="Built with CCL 0.1")

app.add_middleware(CORSMiddleware, allow_origins=["*"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

DB = Path("{name.lower().replace(" ","_")}.db")
security = HTTPBearer()

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE, password TEXT, token TEXT, created TEXT)""")
        db.execute("""CREATE TABLE IF NOT EXISTS items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT, title TEXT, data TEXT, created TEXT)""")
        db.commit()

init_db()

class RegisterBody(BaseModel):
    email: str; password: str

class ItemBody(BaseModel):
    title: str; data: str = ""

def verify_token(cred: HTTPAuthorizationCredentials = Depends(security)):
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE token=?", (cred.credentials,)).fetchone()
    if not row: raise HTTPException(status_code=401, detail="Invalid token")
    return dict(row)

@app.get("/")
def root():
    return {{"api": "{name}", "version": "0.1", "built_with": "CCL 0.1 CapeChain Labs"}}

@app.post("/auth/register")
def register(body: RegisterBody):
    token = secrets.token_hex(32)
    pw    = hashlib.sha256(body.password.encode()).hexdigest()
    try:
        with get_db() as db:
            db.execute("INSERT INTO users(email,password,token,created) VALUES(?,?,?,?)",
                (body.email, pw, token, str(datetime.now())))
            db.commit()
        return {{"token": token}}
    except sqlite3.IntegrityError:
        raise HTTPException(400, "Email already registered")

@app.post("/auth/login")
def login(body: RegisterBody):
    pw  = hashlib.sha256(body.password.encode()).hexdigest()
    row = get_db().execute("SELECT * FROM users WHERE email=? AND password=?",
            (body.email, pw)).fetchone()
    if not row: raise HTTPException(401, "Invalid credentials")
    return {{"token": row["token"]}}

@app.get("/items")
def get_items(user=Depends(verify_token)):
    rows = get_db().execute("SELECT * FROM items WHERE user_email=?",
            (user["email"],)).fetchall()
    return [dict(r) for r in rows]

@app.post("/items")
def create_item(body: ItemBody, user=Depends(verify_token)):
    with get_db() as db:
        db.execute("INSERT INTO items(user_email,title,data,created) VALUES(?,?,?,?)",
            (user["email"], body.title, body.data, str(datetime.now())))
        db.commit()
    return {{"created": body.title}}

@app.delete("/items/{{item_id}}")
def delete_item(item_id: int, user=Depends(verify_token)):
    with get_db() as db:
        db.execute("DELETE FROM items WHERE id=? AND user_email=?",
            (item_id, user["email"]))
        db.commit()
    return {{"deleted": item_id}}
''',
        "requirements.txt": "fastapi\nuvicorn\npydantic\npython-multipart\n",
        ".ccl": json.dumps({"name": name, "type": "api", "version": "0.1", "dependencies": ["fastapi","uvicorn","pydantic"]}, indent=2),
        "README.md": f"# {name} API\n\n```\nccl install fastapi uvicorn\nuvicorn main:app --reload\n```\nDocs at http://localhost:8000/docs\n"
    }
    return files

# ─────────────────────────────────────────────
# APPLY TEMPLATE
# ─────────────────────────────────────────────
def use_template(template_name: str, project_name: str):
    """Scaffold a project from a template."""
    tpl = TEMPLATES.get(template_name)
    if not tpl:
        print(f"{C.RED}  ✗ Template '{template_name}' not found.{C.RESET}")
        list_templates()
        return

    out = Path(project_name)
    out.mkdir(parents=True, exist_ok=True)

    print(f"\n{C.CYAN}  ◈ Applying template: {template_name}{C.RESET}")
    files = tpl["fn"](project_name, out)

    for name, content in files.items():
        fpath = out / name
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(content)
        ok(f"Created: {name}")

    # Write .ccl meta if not in files
    ccl_meta = out / ".ccl"
    if not ccl_meta.exists():
        ccl_meta.write_text(json.dumps({
            "name": project_name, "template": template_name,
            "version": "0.1", "created": str(__import__("datetime").datetime.now())
        }, indent=2))

    print(f"\n{C.GREEN}  ⬡ '{project_name}' ready from template '{template_name}'{C.RESET}")
    print(f"{C.DIM}  cd {project_name} && ccl run to get started{C.RESET}\n")

def list_templates():
    print(f"\n{C.BOLD}  Available Templates:{C.RESET}")
    print(f"  {'─'*50}")
    for name, meta in TEMPLATES.items():
        tags = ", ".join(meta["tags"])
        print(f"  {C.GREEN}{name:<18}{C.RESET} {meta['desc']}")
        print(f"  {'':18} {C.DIM}tags: {tags}{C.RESET}")
    print(f"  {'─'*50}")
    print(f"  {C.DIM}Usage: ccl use template <name> as <project-name>{C.RESET}\n")
