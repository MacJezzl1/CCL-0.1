#!/usr/bin/env python3
"""
CCL Boot v0.1
CapeChain Labs — Boot screen, system checks, terminal launcher.
Run this to start the full CCL 0.1 experience.
"""

import os
import sys
import time
import json
import shutil
from pathlib import Path

# ─────────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    CYAN    = "\033[96m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    MAGENTA = "\033[95m"
    BLUE    = "\033[94m"
    DIM     = "\033[2m"
    WHITE   = "\033[97m"

# ─────────────────────────────────────────────
# ASCII LOGO
# ─────────────────────────────────────────────
LOGO = f"""
{C.CYAN}{C.BOLD}
   ██████╗ ██████╗ ██╗         ██████╗        ██╗
  ██╔════╝██╔════╝ ██║        ██╔═████╗      ███║
  ██║     ██║      ██║        ██║██╔██║      ╚██║
  ██║     ██║      ██║        ████╔╝██║       ██║
  ╚██████╗╚██████╗ ███████╗   ╚██████╔╝  ██╗  ██║
   ╚═════╝ ╚═════╝ ╚══════╝    ╚═════╝   ╚═╝  ╚═╝
{C.RESET}{C.DIM}
        CapeChain Labs Operating Environment
             AI-Native · Web3-Ready · Open
{C.RESET}"""

TAGLINE_FRAMES = [
    "  Initialising CCL kernel …",
    "  Loading AI interface …",
    "  Mounting Web3 layer …",
    "  Preparing developer environment …",
    "  System ready.",
]

# ─────────────────────────────────────────────
# SYSTEM CHECKS
# ─────────────────────────────────────────────
def check_python() -> tuple[bool, str]:
    v = sys.version_info
    ok = v >= (3, 10)
    return ok, f"Python {v.major}.{v.minor}.{v.micro}"

def check_pip() -> tuple[bool, str]:
    found = shutil.which("pip3") or shutil.which("pip")
    return bool(found), "pip" if found else "pip not found"

def check_ollama() -> tuple[bool, str]:
    found = shutil.which("ollama")
    return bool(found), "Ollama (local AI)" if found else "Ollama not installed (optional)"

def check_git() -> tuple[bool, str]:
    found = shutil.which("git")
    return bool(found), "git" if found else "git not found"

def check_node() -> tuple[bool, str]:
    found = shutil.which("node")
    return bool(found), "Node.js" if found else "Node.js not installed (optional)"

CHECKS = [
    ("Python ≥ 3.10",   check_python),
    ("pip",             check_pip),
    ("git",             check_git),
    ("Ollama (AI)",     check_ollama),
    ("Node.js",         check_node),
]

def run_system_checks() -> bool:
    print(f"\n{C.BOLD}  System Checks{C.RESET}")
    print(f"  {'─'*44}")
    all_critical_ok = True
    for label, fn in CHECKS:
        ok_flag, detail = fn()
        icon  = f"{C.GREEN}✓{C.RESET}" if ok_flag else f"{C.YELLOW}⚠{C.RESET}"
        color = C.GREEN if ok_flag else C.YELLOW
        print(f"  {icon}  {color}{label:<22}{C.RESET}  {C.DIM}{detail}{C.RESET}")
        if label == "Python ≥ 3.10" and not ok_flag:
            all_critical_ok = False
    print(f"  {'─'*44}")
    return all_critical_ok

# ─────────────────────────────────────────────
# ANIMATED BOOT SEQUENCE
# ─────────────────────────────────────────────
def animate_boot(fast: bool = False):
    delay = 0.08 if fast else 0.18
    for line in TAGLINE_FRAMES:
        sys.stdout.write(f"\r{C.DIM}{line}{C.RESET}   ")
        sys.stdout.flush()
        time.sleep(delay)
    print()

def loading_bar(label: str = "Booting", width: int = 36, fast: bool = False):
    delay = 0.02 if fast else 0.05
    sys.stdout.write(f"\n  {C.DIM}{label}  [{C.RESET}")
    for i in range(width):
        filled = i < int(width * 0.85)
        char = "█" if filled else "▒"
        color = C.CYAN if filled else C.DIM
        sys.stdout.write(f"{color}{char}{C.RESET}")
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(f"{C.DIM}]{C.RESET}  {C.GREEN}100%{C.RESET}\n")

# ─────────────────────────────────────────────
# CONFIG LOADER / CREATOR
# ─────────────────────────────────────────────
DEFAULT_CONFIG = {
    "os_name":    "CCL",
    "version":    "0.1",
    "codename":   "Genesis",
    "author":     "CapeChain Labs",
    "build_date": "",
    "theme":      "dark-cyber",
    "ai_backend": "ollama",
    "ai_model":   "llama3",
    "chain":      "CCL-Devnet",
    "features": {
        "web3":       True,
        "ai_assist":  True,
        "sandbox":    True,
        "monetize":   False
    }
}

def load_or_create_config() -> dict:
    cfg_dir  = Path(__file__).parent.parent / "config"
    cfg_path = cfg_dir / "ccl_config.json"
    cfg_dir.mkdir(exist_ok=True)

    if cfg_path.exists():
        return json.loads(cfg_path.read_text())

    from datetime import datetime
    config = DEFAULT_CONFIG.copy()
    config["build_date"] = datetime.now().strftime("%Y-%m-%d")
    cfg_path.write_text(json.dumps(config, indent=2))
    print(f"  {C.DIM}Config created → {cfg_path}{C.RESET}")
    return config

# ─────────────────────────────────────────────
# MOTD — message of the day
# ─────────────────────────────────────────────
MOTD = [
    "Build things. Own them. Monetise them.",
    "The OS that thinks with you.",
    "Code is conversation. CCL is listening.",
    "Decentralised by design. Powerful by default.",
    "Create first. Consume never.",
]

def print_motd():
    import random
    msg = random.choice(MOTD)
    width = max(len(msg) + 6, 46)
    print(f"\n{C.DIM}  ┌{'─'*width}┐")
    print(f"  │  {C.RESET}{C.ITALIC if hasattr(C,'ITALIC') else ''}{msg}{C.RESET}{C.DIM}  {'':>{width - len(msg) - 4}}│")
    print(f"  └{'─'*width}┘{C.RESET}")

# ─────────────────────────────────────────────
# FIRST-RUN SETUP
# ─────────────────────────────────────────────
def first_run_setup():
    print(f"\n{C.CYAN}{C.BOLD}  Welcome to CCL 0.1 — First Run Setup{C.RESET}")
    print(f"  {'─'*42}")

    name = input(f"  {C.GREEN}Your name{C.RESET} (press Enter to skip): ").strip()
    if name:
        print(f"  {C.DIM}Welcome, {name}!{C.RESET}")

    print(f"""
  {C.DIM}Quick tip: Start with these commands:
    {C.RESET}{C.GREEN}create project "MyFirstApp"{C.RESET}{C.DIM}
    {C.RESET}{C.GREEN}make wallet{C.RESET}{C.DIM}
    {C.RESET}{C.GREEN}ask "how do I build a web app"{C.RESET}{C.DIM}
    {C.RESET}{C.GREEN}help{C.RESET}{C.DIM}  ← full command list{C.RESET}
""")

# ─────────────────────────────────────────────
# HEADER INFO
# ─────────────────────────────────────────────
def print_header(config: dict):
    ver      = config.get("version",   "0.1")
    codename = config.get("codename",  "Genesis")
    chain    = config.get("chain",     "CCL-Devnet")
    theme    = config.get("theme",     "dark-cyber")
    print(f"""
{C.DIM}  ┌──────────────────────────────────────────────┐
  │  Version   {C.RESET}{C.BOLD}CCL {ver} "{codename}"{C.RESET}{C.DIM}              │
  │  Chain     {C.RESET}{C.CYAN}{chain:<34}{C.RESET}{C.DIM}│
  │  Theme     {C.RESET}{theme:<34}{C.DIM}│
  │  Author    {C.RESET}CapeChain Labs{C.DIM}                        │
  └──────────────────────────────────────────────┘{C.RESET}""")

# ─────────────────────────────────────────────
# MAIN BOOT ENTRY
# ─────────────────────────────────────────────
def boot(fast: bool = False, skip_checks: bool = False):
    # Clear screen
    os.system("clear" if os.name != "nt" else "cls")

    # Logo
    print(LOGO)

    # Config
    config = load_or_create_config()
    print_header(config)

    # Animated boot
    print()
    animate_boot(fast=fast)
    loading_bar(fast=fast)

    # System checks
    if not skip_checks:
        ok_flag = run_system_checks()
        if not ok_flag:
            print(f"\n  {C.RED}✗ Critical check failed. Install Python 3.10+{C.RESET}")
            sys.exit(1)

    # MOTD
    print_motd()

    # First-run detection
    marker = Path.home() / ".ccl_first_run"
    if not marker.exists():
        first_run_setup()
        marker.touch()

    print(f"\n{C.GREEN}{C.BOLD}  ⬡ CCL 0.1 ready. Entering terminal …{C.RESET}\n")
    time.sleep(0.8 if not fast else 0.1)

    # Launch terminal
    sys.path.insert(0, str(Path(__file__).parent))
    from ccl_terminal import run_terminal
    run_terminal()


# ─────────────────────────────────────────────
if __name__ == "__main__":
    fast_mode    = "--fast"   in sys.argv
    skip_checks  = "--no-check" in sys.argv
    boot(fast=fast_mode, skip_checks=skip_checks)
