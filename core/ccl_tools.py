#!/usr/bin/env python3
"""
CCL Power Tools v0.1 — CapeChain Labs
- ccl install  : smart package manager (pip + npm unified)
- ccl save     : one-command git (add + commit + push)
- ccl deploy   : real deploy to GitHub Pages / Vercel / IPFS
- ccl share    : P2P data sharing between CCL users (LAN + internet)
- ccl sync     : real-time project sync across devices
"""

import os, sys, json, time, hashlib, socket, threading, subprocess, shutil, urllib.request
from pathlib import Path
from datetime import datetime

class C:
    RESET="\033[0m"; BOLD="\033[1m"; CYAN="\033[96m"; GREEN="\033[92m"
    YELLOW="\033[93m"; RED="\033[91m"; MAGENTA="\033[95m"; DIM="\033[2m"

def ok(m):    print(f"{C.GREEN}  ✓ {m}{C.RESET}")
def info(m):  print(f"{C.CYAN}  → {m}{C.RESET}")
def warn(m):  print(f"{C.YELLOW}  ⚠ {m}{C.RESET}")
def err(m):   print(f"{C.RED}  ✗ {m}{C.RESET}")

def run_cmd(cmd: list, capture=True) -> tuple[int, str]:
    try:
        r = subprocess.run(cmd, capture_output=capture, text=True, timeout=120)
        return r.returncode, (r.stdout + r.stderr).strip()
    except FileNotFoundError:
        return 1, f"Command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 1, "Timeout"
    except Exception as e:
        return 1, str(e)

# ═══════════════════════════════════════════════════════
# 1. CCL INSTALL — Unified package manager
# ═══════════════════════════════════════════════════════
# Maps common package names to both pip + npm equivalents
NPM_PACKAGES  = {"react","vue","svelte","next","express","tailwind","vite","webpack","axios","socket.io","three","d3","lodash","typescript"}
PIP_PACKAGES  = {"flask","django","fastapi","requests","numpy","pandas","matplotlib","sqlalchemy","celery","redis","boto3","pillow","pydantic"}
BOTH_PACKAGES = {"prettier","eslint"}

def ccl_install(packages: list[str], flags: list[str] = None):
    """Smart install: auto-detects pip vs npm. Supports --global --dev."""
    if not packages:
        err("install: specify package name(s)")
        return

    flags = flags or []
    dev_flag    = "--dev" in flags or "-D" in flags
    global_flag = "--global" in flags or "-g" in flags

    pip_pkgs = []
    npm_pkgs = []

    for pkg in packages:
        p = pkg.lower().replace("-","").replace("_","")
        # Guess by known lists
        if pkg.lower() in PIP_PACKAGES:
            pip_pkgs.append(pkg)
        elif pkg.lower() in NPM_PACKAGES:
            npm_pkgs.append(pkg)
        else:
            # Try pip first if project has requirements.txt or .py files
            has_py  = any(Path(".").glob("*.py"))
            has_js  = any(Path(".").glob("*.js")) or Path("package.json").exists()
            if has_js and not has_py:
                npm_pkgs.append(pkg)
            else:
                pip_pkgs.append(pkg)

    results = []

    if pip_pkgs:
        info(f"Installing via pip: {', '.join(pip_pkgs)}")
        cmd = [sys.executable, "-m", "pip", "install", "--quiet", "--break-system-packages"] + pip_pkgs
        code, out = run_cmd(cmd, capture=True)
        if code == 0:
            for p in pip_pkgs:
                ok(f"{p} installed (Python)")
                results.append(p)
        else:
            err(f"pip failed: {out[:200]}")

    if npm_pkgs:
        if not shutil.which("npm"):
            warn("npm not found. Install Node.js from nodejs.org")
        else:
            info(f"Installing via npm: {', '.join(npm_pkgs)}")
            base_cmd = ["npm", "install"]
            if global_flag: base_cmd.append("-g")
            if dev_flag:    base_cmd.append("--save-dev")
            else:           base_cmd.append("--save")
            code, out = run_cmd(base_cmd + npm_pkgs, capture=True)
            if code == 0:
                for p in npm_pkgs:
                    ok(f"{p} installed (Node)")
                    results.append(p)
            else:
                err(f"npm failed: {out[:200]}")

    if results:
        # Log to .ccl project file if present
        ccl_file = Path(".ccl")
        if ccl_file.exists():
            meta = json.loads(ccl_file.read_text())
            deps = meta.get("dependencies", [])
            deps = list(set(deps + results))
            meta["dependencies"] = deps
            ccl_file.write_text(json.dumps(meta, indent=2))
            info(f"Saved to .ccl project config")

# ═══════════════════════════════════════════════════════
# 2. CCL SAVE — One command git
# ═══════════════════════════════════════════════════════
def ccl_save(message: str = "", push: bool = True):
    """git add . + commit + push in one move."""
    if not shutil.which("git"):
        err("git not installed. Install from git-scm.com")
        return

    # Init if needed
    if not Path(".git").exists():
        info("Initialising git repo …")
        run_cmd(["git", "init"])
        run_cmd(["git", "branch", "-M", "main"])
        ok("Git repo initialised")

    # Stage all
    run_cmd(["git", "add", "."])

    # Auto-generate message if empty
    if not message:
        try:
            code, diff = run_cmd(["git", "diff", "--cached", "--stat"])
            lines      = [l.strip() for l in diff.splitlines() if l.strip()]
            changed    = lines[-1] if lines else "update"
            message    = f"CCL save: {changed}"
        except:
            message = f"CCL save @ {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    code, out = run_cmd(["git", "commit", "-m", message])
    if code != 0 and "nothing to commit" in out:
        warn("Nothing new to save.")
        return
    if code != 0:
        err(f"Commit failed: {out[:200]}")
        return
    ok(f"Saved: \"{message}\"")

    if push:
        code2, out2 = run_cmd(["git", "push"])
        if code2 == 0:
            ok("Pushed to remote.")
        else:
            warn("Push failed (no remote set?). To add one:")
            info("  git remote add origin https://github.com/YOU/REPO.git")
            info("  Then run: ccl save again")

def ccl_git_status():
    code, out = run_cmd(["git", "status", "--short"])
    if out:
        print(f"\n{C.CYAN}  Git status:{C.RESET}")
        for line in out.splitlines():
            colour = C.GREEN if line.startswith("M") else C.YELLOW if line.startswith("?") else C.RED
            print(f"  {colour}{line}{C.RESET}")
    else:
        ok("Working directory clean.")

def ccl_git_log(n: int = 5):
    code, out = run_cmd(["git", "log", f"--oneline", f"-{n}"])
    if out:
        print(f"\n{C.CYAN}  Recent saves:{C.RESET}")
        for line in out.splitlines():
            print(f"  {C.DIM}•{C.RESET} {line}")
    else:
        warn("No git history yet. Run: ccl save")

# ═══════════════════════════════════════════════════════
# 3. CCL DEPLOY — Real deploy to free platforms
# ═══════════════════════════════════════════════════════
def ccl_deploy(target: str = "auto", project: str = "."):
    """
    Deploy to:
    - github  : GitHub Pages (free)
    - vercel  : Vercel CLI (free)
    - surge   : Surge.sh (free, no account needed)
    - ipfs    : IPFS via web3.storage (decentralised)
    - auto    : detect best option
    """
    proj_path = Path(project)

    # Auto-detect
    if target == "auto":
        if Path("vercel.json").exists() or Path(".vercel").exists():
            target = "vercel"
        elif Path("CNAME").exists() or Path("index.html").exists():
            target = "surge"
        else:
            target = "surge"

    print(f"\n{C.CYAN}  ◈ Deploying to {target.upper()} …{C.RESET}\n")

    if target == "vercel":
        _deploy_vercel(proj_path)
    elif target == "surge":
        _deploy_surge(proj_path)
    elif target in ("github", "gh-pages"):
        _deploy_github_pages(proj_path)
    elif target == "ipfs":
        _deploy_ipfs_hint(proj_path)
    else:
        err(f"Unknown deploy target: {target}")
        info("Options: vercel | surge | github | ipfs | auto")

def _deploy_vercel(path: Path):
    if not shutil.which("vercel"):
        warn("Vercel CLI not installed.")
        info("Install: ccl install vercel --global")
        info("Then run: ccl deploy vercel")
        return
    code, out = run_cmd(["vercel", "--prod", "--yes"], capture=False)
    if code == 0:
        ok("Deployed to Vercel!")
    else:
        err("Vercel deploy failed. Run 'vercel login' first.")

def _deploy_surge(path: Path):
    if not shutil.which("surge"):
        warn("Surge not installed.")
        info("Install: ccl install surge --global")
        return
    domain = f"{path.resolve().name.lower().replace(' ','-')}.surge.sh"
    info(f"Deploying to: {domain}")
    code, out = run_cmd(["surge", str(path), domain], capture=False)
    if code == 0:
        ok(f"Live at: https://{domain}")
    else:
        err(f"Surge failed: {out[:200]}")

def _deploy_github_pages(path: Path):
    if not shutil.which("git"):
        err("git required for GitHub Pages")
        return
    info("Pushing to gh-pages branch …")
    code, out = run_cmd(["git", "subtree", "push", "--prefix", ".", "origin", "gh-pages"])
    if code == 0:
        ok("Deployed to GitHub Pages!")
        info("Enable Pages in repo Settings → Pages → gh-pages branch")
    else:
        err(f"Deploy failed: {out[:200]}")
        info("Make sure your repo is on GitHub with a remote set.")

def _deploy_ipfs_hint(path: Path):
    info("IPFS deploy — upload your folder to:")
    print(f"  {C.CYAN}• web3.storage  {C.DIM}(free, drag-drop or CLI){C.RESET}")
    print(f"  {C.CYAN}• nft.storage   {C.DIM}(free, permanent){C.RESET}")
    print(f"  {C.CYAN}• fleek.co      {C.DIM}(free tier, CI/CD){C.RESET}")
    info(f"Your folder: {path.resolve()}")

# ═══════════════════════════════════════════════════════
# 4. CCL SHARE — P2P file/data transfer between CCL users
# ═══════════════════════════════════════════════════════
SHARE_PORT    = 9741        # CCL signature port
SHARE_VERSION = b"CCL01"   # handshake magic bytes

def _get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def ccl_share_send(filepath: str, pin: str = ""):
    """Send a file over LAN to another CCL user."""
    path = Path(filepath)
    if not path.exists():
        err(f"File not found: {filepath}")
        return

    # Generate PIN if not given
    if not pin:
        pin = hashlib.sha256(os.urandom(8)).hexdigest()[:6].upper()

    ip   = _get_local_ip()
    data = path.read_bytes()
    size = len(data)

    print(f"\n{C.CYAN}  ◈ CCL Share — Sending{C.RESET}")
    print(f"  {C.GREEN}File   : {path.name} ({size:,} bytes){C.RESET}")
    print(f"  {C.YELLOW}PIN    : {pin}{C.RESET}")
    print(f"  {C.CYAN}Your IP: {ip}:{SHARE_PORT}{C.RESET}")
    print(f"\n  Tell the receiver:")
    print(f"  {C.BOLD}  ccl receive {ip} {pin}{C.RESET}")
    print(f"\n{C.DIM}  Waiting for connection …{C.RESET}")

    pin_hash = hashlib.sha256(pin.encode()).hexdigest().encode()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", SHARE_PORT))
    server.listen(1)
    server.settimeout(120)

    try:
        conn, addr = server.accept()
        print(f"\n{C.GREEN}  ✓ Connected: {addr[0]}{C.RESET}")

        # Handshake
        conn.send(SHARE_VERSION)
        received_pin = conn.recv(64)
        if received_pin.strip() != pin_hash.strip():
            err("Wrong PIN. Connection rejected.")
            conn.close()
            return

        # Send metadata then data
        meta = json.dumps({
            "filename": path.name,
            "size":     size,
            "hash":     hashlib.sha256(data).hexdigest()
        }).encode()
        conn.send(len(meta).to_bytes(4, "big"))
        conn.send(meta)

        # Send file in chunks
        chunk = 65536
        sent  = 0
        for i in range(0, size, chunk):
            conn.send(data[i:i+chunk])
            sent += min(chunk, size - i)
            pct = int(sent / size * 40)
            bar = "█" * pct + "░" * (40 - pct)
            sys.stdout.write(f"\r  {C.CYAN}[{bar}]{C.RESET} {sent:,}/{size:,}")
            sys.stdout.flush()

        print(f"\n{C.GREEN}  ✓ Transfer complete!{C.RESET}")
        conn.close()
    except socket.timeout:
        err("Timeout — no receiver connected within 2 minutes.")
    except Exception as e:
        err(f"Share failed: {e}")
    finally:
        server.close()

def ccl_share_receive(sender_ip: str, pin: str, save_dir: str = "."):
    """Receive a file from another CCL user."""
    print(f"\n{C.CYAN}  ◈ CCL Share — Receiving from {sender_ip}{C.RESET}")

    pin_hash = hashlib.sha256(pin.encode()).hexdigest().encode()

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        sock.connect((sender_ip, SHARE_PORT))

        # Handshake
        magic = sock.recv(5)
        if magic != SHARE_VERSION:
            err("Not a CCL share server.")
            return
        sock.send(pin_hash)

        # Receive metadata
        meta_len = int.from_bytes(sock.recv(4), "big")
        meta     = json.loads(sock.recv(meta_len).decode())
        filename = meta["filename"]
        size     = meta["size"]
        expected = meta["hash"]

        info(f"Receiving: {filename} ({size:,} bytes)")

        # Receive file
        buffer = b""
        while len(buffer) < size:
            chunk = sock.recv(65536)
            if not chunk:
                break
            buffer += chunk
            pct = int(len(buffer) / size * 40)
            bar = "█" * pct + "░" * (40 - pct)
            sys.stdout.write(f"\r  {C.CYAN}[{bar}]{C.RESET} {len(buffer):,}/{size:,}")
            sys.stdout.flush()

        print()

        # Verify
        actual = hashlib.sha256(buffer).hexdigest()
        if actual != expected:
            err("Hash mismatch — file corrupted in transit!")
            return

        out = Path(save_dir) / filename
        out.write_bytes(buffer)
        ok(f"Received: {out}")
        sock.close()

    except ConnectionRefusedError:
        err(f"Cannot connect to {sender_ip}:{SHARE_PORT} — is sender waiting?")
    except socket.timeout:
        err("Connection timed out.")
    except Exception as e:
        err(f"Receive failed: {e}")

# ═══════════════════════════════════════════════════════
# 5. CCL SYNC — Watch + sync project across devices
# ═══════════════════════════════════════════════════════
def ccl_sync_start(project_dir: str = "."):
    """Watch for file changes and auto-save via git."""
    if not shutil.which("git"):
        err("git required for sync")
        return

    path = Path(project_dir)
    info(f"Sync started for: {path.resolve()}")
    info("Auto-saving changes every 30s. Ctrl+C to stop.")

    snapshots = {}
    def get_snapshot():
        snap = {}
        for f in path.rglob("*"):
            if f.is_file() and ".git" not in str(f):
                try:
                    snap[str(f)] = f.stat().st_mtime
                except:
                    pass
        return snap

    snapshots = get_snapshot()

    try:
        while True:
            time.sleep(30)
            new_snap = get_snapshot()
            changed  = [k for k, v in new_snap.items() if snapshots.get(k) != v]
            changed += [k for k in snapshots if k not in new_snap]

            if changed:
                msg = f"Auto-sync: {len(changed)} file(s) changed"
                info(msg)
                ccl_save(msg, push=True)
                snapshots = new_snap
            else:
                sys.stdout.write(f"\r{C.DIM}  Watching … {datetime.now().strftime('%H:%M:%S')}{C.RESET}")
                sys.stdout.flush()

    except KeyboardInterrupt:
        print(f"\n{C.DIM}  Sync stopped.{C.RESET}")
