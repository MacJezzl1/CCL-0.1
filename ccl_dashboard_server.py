#!/usr/bin/env python3
import os, sys, json, io, time, threading, hashlib, random, subprocess, shutil, socket
from pathlib import Path
from datetime import datetime
from contextlib import redirect_stdout

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "core"))

try:
    from flask import Flask, request, jsonify, Response, send_from_directory
except ImportError:
    print("\n  CCL: Installing Flask …")
    subprocess.run([sys.executable, "-m", "pip", "install", "flask", "--break-system-packages", "-q"])
    from flask import Flask, request, jsonify, Response, send_from_directory

from ccl_interpreter import CCLInterpreter, CCLExecutor, lex

app = Flask(__name__, static_folder=str(ROOT))
PORT = 7741
ANSI = __import__("re").compile(r'\033\[[0-9;]*m')

def load_config():
    p = ROOT / "config" / "ccl_config.json"
    return json.loads(p.read_text()) if p.exists() else {}

def save_config(cfg):
    p = ROOT / "config" / "ccl_config.json"
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(cfg, indent=2))

cfg = load_config()
interp = CCLInterpreter(cfg)
executor = interp.executor

_output_lines = []
_output_lock = threading.Lock()

def push_output(line: str):
    clean = ANSI.sub("", line)
    with _output_lock:
        _output_lines.append({"t": time.time(), "text": clean})
        if len(_output_lines) > 400:
            _output_lines.pop(0)

import builtins
_real_print = builtins.print
def _ccl_print(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    end = kwargs.get("end", "\n")
    text = sep.join(str(a) for a in args)
    push_output(text)
    _real_print(*args, **kwargs)
builtins.print = _ccl_print

def get_projects():
    projects = []
    for d in ROOT.iterdir():
        ccl_file = d / ".ccl"
        if d.is_dir() and ccl_file.exists():
            try:
                meta = json.loads(ccl_file.read_text())
                projects.append({"name": d.name, "type": meta.get("type", "unknown"),
                    "version": meta.get("version", "0.1"), "created": meta.get("created", ""),
                    "deps": meta.get("dependencies", [])})
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

def get_todos():
    tf = ROOT / ".ccl_todo.json"
    try: return json.loads(tf.read_text()) if tf.exists() else []
    except: return []

def get_wallet():
    return executor.wallet

def get_stats():
    projects = get_projects()
    has_key = any(k for k in cfg if "api_key" in k.lower() and cfg[k] and cfg[k] != "YOUR_KEY_HERE")
    return {
        "projects": len(projects),
        "files": len(list(ROOT.glob("*.py"))) + len(list(ROOT.glob("*.html"))),
        "notes": len(get_notes()),
        "todos": len(get_todos()),
        "ai_ready": has_key or bool(os.environ.get("ANTHROPIC_API_KEY")),
        "wallet": bool(executor.wallet),
        "version": cfg.get("version", "0.3"),
        "codename": cfg.get("codename", "OMNIA"),
        "chain": cfg.get("chain", "CCL-Net"),
        "themes": ["cyber", "sunset", "matrix", "dragonskin", "ocean", "midnight"],
    }

def get_sysinfo():
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.2)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net = psutil.net_io_counters()
        boot = datetime.fromtimestamp(psutil.boot_time())
        uptime = str(datetime.now() - boot).split('.')[0]
        return {
            "cpu": cpu, "cpu_cores": psutil.cpu_count(),
            "ram_used": round(mem.used / 1024**3, 1),
            "ram_total": round(mem.total / 1024**3, 1),
            "ram_pct": mem.percent,
            "disk_used": round(disk.used / 1024**3, 1),
            "disk_total": round(disk.total / 1024**3, 1),
            "disk_pct": disk.percent,
            "uptime": uptime,
            "hostname": os.uname().nodename,
            "python": sys.version.split()[0],
            "processes": len(psutil.pids()),
        }
    except: return {"error": "psutil not available"}

@app.route("/")
def index():
    return send_from_directory(str(ROOT), "ccl_dashboard_ui.html")

@app.route("/api/stats")
def api_stats():
    return jsonify(get_stats())

@app.route("/api/sysinfo")
def api_sysinfo():
    return jsonify(get_sysinfo())

@app.route("/api/projects")
def api_projects():
    return jsonify(get_projects())

@app.route("/api/files")
def api_files():
    return jsonify(get_files())

@app.route("/api/notes")
def api_notes():
    return jsonify(get_notes())

@app.route("/api/todos")
def api_todos():
    return jsonify(get_todos())

@app.route("/api/wallet")
def api_wallet():
    return jsonify(executor.wallet or {})

@app.route("/api/wallet/create", methods=["POST"])
def api_wallet_create():
    seed = str(random.getrandbits(256)).encode()
    address = "CCL" + hashlib.sha256(seed).hexdigest()[:40].upper()
    executor.wallet = {"address": address, "balance": "0.0 CCL", "chain": "CCL-Devnet", "created": str(datetime.now())}
    push_output(f"  ✓ Wallet created: {address}")
    return jsonify(executor.wallet)

@app.route("/api/todo", methods=["POST"])
def api_todo():
    data = request.json or {}
    action = data.get("action", "list")
    text = data.get("text", "")
    tf = ROOT / ".ccl_todo.json"
    todos = json.loads(tf.read_text()) if tf.exists() else []
    if action == "add" and text:
        todos.append({"text": text, "done": False, "time": datetime.now().strftime("%H:%M")})
        tf.write_text(json.dumps(todos, indent=2))
        push_output(f"  ✓ Todo added: {text}")
    elif action == "done":
        idx = int(data.get("index", -1))
        if 0 <= idx < len(todos):
            todos[idx]["done"] = True
            tf.write_text(json.dumps(todos, indent=2))
    elif action == "remove":
        idx = int(data.get("index", -1))
        if 0 <= idx < len(todos):
            todos.pop(idx)
            tf.write_text(json.dumps(todos, indent=2))
    elif action == "clear":
        tf.write_text("[]")
        todos = []
    return jsonify(todos)

@app.route("/api/run", methods=["POST"])
def api_run():
    data = request.json or {}
    cmd = data.get("command", "").strip()
    if not cmd: return jsonify({"error": "No command provided"}), 400
    push_output(f"\n› {cmd}")
    def run():
        try: interp.execute_line(cmd, executor)
        except Exception as e: push_output(f"  ✗ Error: {e}")
    t = threading.Thread(target=run)
    t.start(); t.join(timeout=60)
    return jsonify({"ok": True, "command": cmd})

@app.route("/api/output")
def api_output():
    since = float(request.args.get("since", 0))
    def generate():
        last_sent = since
        while True:
            with _output_lock:
                new = [l for l in _output_lines if l["t"] > last_sent]
            if new:
                for line in new:
                    yield f"data: {json.dumps(line)}\n\n"
                last_sent = new[-1]["t"]
            else: yield ": ping\n\n"
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
    if not desc: return jsonify({"error": "No description"}), 400
    cmd = f'generate "{desc}"'
    push_output(f"\n› {cmd}")
    def run(): interp.execute_line(cmd, executor)
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
    data = request.json or {}
    target = data.get("target", "surge")
    cmd = f"deploy {target}"
    push_output(f"\n› {cmd}")
    def run(): interp.execute_line(cmd, executor)
    threading.Thread(target=run).start()
    return jsonify({"ok": True})

@app.route("/api/save", methods=["POST"])
def api_save():
    data = request.json or {}
    msg = data.get("message", "")
    cmd = f'save "{msg}"' if msg else "save"
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
    data = request.json or {}
    tpl = data.get("template", "")
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
    provider = data.get("provider", "").strip()
    key = data.get("key", "").strip()
    if not provider or not key: return jsonify({"error": "Provider and key required"}), 400
    key_map = {
        "openai": "openai_api_key", "claude": "anthropic_api_key", "anthropic": "anthropic_api_key",
        "gemini": "gemini_api_key", "deepseek": "deepseek_api_key", "mistral": "mistral_api_key",
        "groq": "groq_api_key", "together": "together_api_key", "fireworks": "fireworks_api_key",
        "perplexity": "perplexity_api_key", "xai": "xai_api_key", "cohere": "cohere_api_key",
        "huggingface": "huggingface_api_key", "openrouter": "openrouter_api_key",
        "replicate": "replicate_api_key",
    }
    kn = key_map.get(provider.lower())
    if kn:
        cfg[kn] = key; save_config(cfg)
        push_output(f"  ✓ {provider.title()} API key saved.")
    else:
        cfg[f"{provider}_api_key"] = key; save_config(cfg)
        push_output(f"  ✓ API key saved for {provider}.")
    return jsonify({"ok": True})

@app.route("/api/config")
def api_config():
    safe = {k: v for k, v in cfg.items() if "key" not in k.lower()}
    safe["ai_ready"] = any(k for k in cfg if "api_key" in k.lower() and cfg[k] and cfg[k] != "YOUR_KEY_HERE")
    safe["providers"] = {
        "openai": bool(cfg.get("openai_api_key")),
        "claude": bool(cfg.get("anthropic_api_key")),
        "gemini": bool(cfg.get("gemini_api_key")),
        "groq": bool(cfg.get("groq_api_key")),
        "deepseek": bool(cfg.get("deepseek_api_key")),
        "openrouter": bool(cfg.get("openrouter_api_key")),
    }
    return jsonify(safe)

@app.route("/api/file/read", methods=["POST"])
def api_file_read():
    data = request.json or {}
    path = data.get("path", "")
    fp = ROOT / path
    if not fp.exists() or not fp.is_file():
        return jsonify({"error": "File not found"}), 404
    try:
        content = fp.read_text()
        return jsonify({"name": fp.name, "content": content, "size": fp.stat().st_size})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/file/write", methods=["POST"])
def api_file_write():
    data = request.json or {}
    path = data.get("path", "")
    content = data.get("content", "")
    fp = ROOT / path
    try:
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(content)
        push_output(f"  ✓ File saved: {path}")
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/file/delete", methods=["POST"])
def api_file_delete():
    data = request.json or {}
    path = data.get("path", "")
    fp = ROOT / path
    if not fp.exists(): return jsonify({"error": "Not found"}), 404
    try:
        if fp.is_dir(): shutil.rmtree(fp)
        else: fp.unlink()
        push_output(f"  ✓ Deleted: {path}")
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/create/project", methods=["POST"])
def api_create_project():
    data = request.json or {}
    name = data.get("name", "my_project")
    ptype = data.get("type", "basic")
    pd = ROOT / name
    try:
        pd.mkdir(exist_ok=True)
        (pd / "README.md").write_text(f"# {name}\nCreated by CCL — CapeChain Labs\n")
        (pd / "main.py").write_text(f'print("Hello from {name} — CCL")\n')
        (pd / ".ccl").write_text(json.dumps({"name": name, "type": ptype, "version": "0.3", "created": str(datetime.now())}, indent=2))
        push_output(f"  ✓ Project created: {name}")
        return jsonify({"ok": True, "name": name})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def main():
    push_output("  ⬡ CCL OMNIA Dashboard Server starting …")
    push_output(f"  → Open: http://localhost:{PORT}")
    push_output("  → Terminal, Todo, File Manager, and AI ready")
    push_output("  → Type CCL commands or use the web interface\n")
    print(f"\n  \033[96m⬡ CCL OMNIA Dashboard → http://localhost:{PORT}\033[0m\n")
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)

if __name__ == "__main__":
    main()
