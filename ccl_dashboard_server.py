#!/usr/bin/env python3
"""
CCL Dashboard Server v0.1 — CapeChain Labs
Flask backend powering the live dashboard.
Run: python3 ccl_dashboard_server.py
Then open: http://localhost:7741
"""

import os, sys, json, io, time, threading, hashlib, random, subprocess, shutil
from pathlib import Path
from datetime import datetime
from contextlib import redirect_stdout

# ── ensure core/ is importable ─────────────────────────────────────────────
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "core"))

try:
    from flask import Flask, request, jsonify, Response, send_from_directory
except ImportError:
    print("\n  CCL: Flask not installed. Installing now …")
    subprocess.run([sys.executable, "-m", "pip", "install", "flask", "--break-system-packages", "-q"])
    from flask import Flask, request, jsonify, Response, send_from_directory

from ccl_interpreter import CCLInterpreter, CCLExecutor, lex

# ─────────────────────────────────────────────
app    = Flask(__name__, static_folder=str(ROOT))
PORT   = 7741
ANSI   = __import__("re").compile(r'\033\[[0-9;]*m')

# ── config ────────────────────────────────────
def load_config():
    p = ROOT / "config" / "ccl_config.json"
    return json.loads(p.read_text()) if p.exists() else {}

def save_config(cfg):
    p = ROOT / "config" / "ccl_config.json"
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(cfg, indent=2))

# ── shared interpreter instance ───────────────
cfg      = load_config()
interp   = CCLInterpreter(cfg)
executor = interp.executor

# ── terminal output ring buffer ───────────────
_output_lines = []
_output_lock  = threading.Lock()

def push_output(line: str):
    clean = ANSI.sub("", line)
    with _output_lock:
        _output_lines.append({"t": time.time(), "text": clean})
        if len(_output_lines) > 400:
            _output_lines.pop(0)

# ── patch print so CCL output goes to buffer ──
import builtins
_real_print = builtins.print

def _ccl_print(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    end = kwargs.get("end", "\n")
    text = sep.join(str(a) for a in args)
    push_output(text)
    _real_print(*args, **kwargs)   # also show in terminal

builtins.print = _ccl_print

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def get_projects():
    projects = []
    for d in ROOT.iterdir():
        ccl_file = d / ".ccl"
        if d.is_dir() and ccl_file.exists():
            try:
                meta = json.loads(ccl_file.read_text())
                projects.append({
                    "name":    d.name,
                    "type":    meta.get("type", "unknown"),
                    "version": meta.get("version", "0.1"),
                    "created": meta.get("created", ""),
                    "deps":    meta.get("dependencies", []),
                })
            except: pass
    return projects

def get_files():
    files = []
    for f in ROOT.iterdir():
        if f.is_file() and not f.name.startswith("."):
            files.append({"name": f.name, "size": f.stat().st_size, "ext": f.suffix})
    return files

def get_notes():
    nf = ROOT / ".ccl_notes.json"
    try: return json.loads(nf.read_text()) if nf.exists() else []
    except: return []

def get_wallet():
    return executor.wallet

def get_stats():
    projects = get_projects()
    has_key  = bool(cfg.get("anthropic_api_key") or os.environ.get("ANTHROPIC_API_KEY"))
    return {
        "projects": len(projects),
        "files":    len(list(ROOT.glob("*.py"))) + len(list(ROOT.glob("*.html"))),
        "notes":    len(get_notes()),
        "ai_ready": has_key,
        "wallet":   bool(executor.wallet),
        "version":  cfg.get("version", "0.1"),
        "codename": cfg.get("codename", "Genesis"),
        "chain":    cfg.get("chain", "CCL-Devnet"),
    }

# ─────────────────────────────────────────────
# API ROUTES
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(str(ROOT), "ccl_dashboard_ui.html")

@app.route("/api/stats")
def api_stats():
    return jsonify(get_stats())

@app.route("/api/projects")
def api_projects():
    return jsonify(get_projects())

@app.route("/api/files")
def api_files():
    return jsonify(get_files())

@app.route("/api/notes")
def api_notes():
    return jsonify(get_notes())

@app.route("/api/wallet")
def api_wallet():
    return jsonify(executor.wallet or {})

@app.route("/api/wallet/create", methods=["POST"])
def api_wallet_create():
    seed    = str(random.getrandbits(256)).encode()
    address = "CCL" + hashlib.sha256(seed).hexdigest()[:40].upper()
    executor.wallet = {
        "address": address,
        "balance": "0.0 CCL",
        "chain":   "CCL-Devnet",
        "created": str(datetime.now())
    }
    push_output(f"  ✓ Wallet created: {address}")
    return jsonify(executor.wallet)

@app.route("/api/run", methods=["POST"])
def api_run():
    """Execute a CCL command string. Returns output lines."""
    data = request.json or {}
    cmd  = data.get("command", "").strip()
    if not cmd:
        return jsonify({"error": "No command provided"}), 400

    push_output(f"\n› {cmd}")

    def run():
        try:
            interp.execute_line(cmd, executor)
        except Exception as e:
            push_output(f"  ✗ Error: {e}")

    t = threading.Thread(target=run)
    t.start()
    t.join(timeout=60)

    return jsonify({"ok": True, "command": cmd})

@app.route("/api/output")
def api_output():
    """SSE stream of terminal output lines."""
    since = float(request.args.get("since", 0))

    def generate():
        last_sent = since
        while True:
            with _output_lock:
                new = [l for l in _output_lines if l["t"] > last_sent]
            if new:
                for line in new:
                    payload = json.dumps(line)
                    yield f"data: {payload}\n\n"
                last_sent = new[-1]["t"]
            else:
                yield ": ping\n\n"
            time.sleep(0.25)

    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@app.route("/api/output/history")
def api_output_history():
    with _output_lock:
        return jsonify(list(_output_lines[-100:]))

@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.json or {}
    desc = data.get("description", "").strip()
    if not desc:
        return jsonify({"error": "No description"}), 400
    cmd = f'generate "{desc}"'
    push_output(f"\n› {cmd}")
    def run():
        interp.execute_line(cmd, executor)
    threading.Thread(target=run).start()
    return jsonify({"ok": True, "started": True})

@app.route("/api/install", methods=["POST"])
def api_install():
    data = request.json or {}
    pkgs = data.get("packages", "").strip()
    if not pkgs: return jsonify({"error": "No packages"}), 400
    cmd = f"install {pkgs}"
    push_output(f"\n› {cmd}")
    def run(): interp.execute_line(cmd, executor)
    threading.Thread(target=run).start()
    return jsonify({"ok": True})

@app.route("/api/deploy", methods=["POST"])
def api_deploy():
    data   = request.json or {}
    target = data.get("target", "surge")
    cmd    = f"deploy {target}"
    push_output(f"\n› {cmd}")
    def run(): interp.execute_line(cmd, executor)
    threading.Thread(target=run).start()
    return jsonify({"ok": True})

@app.route("/api/save", methods=["POST"])
def api_save():
    data = request.json or {}
    msg  = data.get("message", "")
    cmd  = f'save "{msg}"' if msg else "save"
    push_output(f"\n› {cmd}")
    def run(): interp.execute_line(cmd, executor)
    threading.Thread(target=run).start()
    return jsonify({"ok": True})

@app.route("/api/note", methods=["POST"])
def api_note():
    data = request.json or {}
    text = data.get("text", "").strip()
    if not text: return jsonify({"error": "No text"}), 400
    cmd = f'note "{text}"'
    push_output(f"\n› {cmd}")
    interp.execute_line(cmd, executor)
    return jsonify({"ok": True, "notes": get_notes()})

@app.route("/api/template", methods=["POST"])
def api_template():
    data    = request.json or {}
    tpl     = data.get("template", "")
    project = data.get("project", tpl + "-project")
    if not tpl: return jsonify({"error": "No template"}), 400
    cmd = f'use template {tpl} as "{project}"'
    push_output(f"\n› {cmd}")
    def run(): interp.execute_line(cmd, executor)
    threading.Thread(target=run).start()
    return jsonify({"ok": True})

@app.route("/api/setkey", methods=["POST"])
def api_setkey():
    data = request.json or {}
    key  = data.get("key", "").strip()
    if not key: return jsonify({"error": "No key"}), 400
    cfg["anthropic_api_key"] = key
    save_config(cfg)
    executor.config["anthropic_api_key"] = key
    push_output("  ✓ Anthropic API key saved. AI features now active.")
    return jsonify({"ok": True})

@app.route("/api/config")
def api_config():
    safe = {k: v for k, v in cfg.items() if "key" not in k.lower()}
    safe["ai_ready"] = bool(cfg.get("anthropic_api_key") or os.environ.get("ANTHROPIC_API_KEY"))
    return jsonify(safe)

# ─────────────────────────────────────────────
# STARTUP
# ─────────────────────────────────────────────
if __name__ == "__main__":
    push_output("  ⬡ CCL 0.1 Dashboard Server starting …")
    push_output(f"  → Open: http://localhost:{PORT}")
    push_output("  → Type CCL commands in the terminal panel")
    push_output("  → All features live and connected\n")
    print(f"\n  \033[96m⬡ CCL Dashboard → http://localhost:{PORT}\033[0m\n")
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)
