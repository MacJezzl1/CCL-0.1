#!/usr/bin/env python3
"""
CCL AI Module v0.1 — CapeChain Labs
Powered by Ollama (free, local, no API key needed).
Falls back to Anthropic API if key is set.
"""

import json, os, sys, urllib.request, urllib.error
from pathlib import Path
from datetime import datetime

class C:
    RESET="\033[0m"; BOLD="\033[1m"; CYAN="\033[96m"; GREEN="\033[92m"
    YELLOW="\033[93m"; RED="\033[91m"; MAGENTA="\033[95m"; DIM="\033[2m"

def ok(m):    print(f"{C.GREEN}  ✓ {m}{C.RESET}")
def info(m):  print(f"{C.CYAN}  → {m}{C.RESET}")
def warn(m):  print(f"{C.YELLOW}  ⚠ {m}{C.RESET}")
def err(m):   print(f"{C.RED}  ✗ {m}{C.RESET}")
def ai(m):    print(f"{C.MAGENTA}  ◈ {m}{C.RESET}")

OLLAMA_URL  = "http://localhost:11434"
CLAUDE_URL  = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL= "claude-sonnet-4-20250514"

# ─────────────────────────────────────────────
# OLLAMA HELPERS
# ─────────────────────────────────────────────
def ollama_running() -> bool:
    try:
        urllib.request.urlopen(OLLAMA_URL, timeout=2)
        return True
    except:
        return False

def ollama_models() -> list[str]:
    """Return list of installed model names."""
    try:
        r = urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=4)
        data = json.loads(r.read())
        return [m["name"] for m in data.get("models", [])]
    except:
        return []

def best_model() -> str | None:
    """Pick the best available Ollama model."""
    models = ollama_models()
    if not models:
        return None
    # Preference order
    preferred = ["llama3", "llama3.2", "llama3.1", "llama2", "mistral",
                 "codellama", "phi3", "gemma", "gemma2", "qwen2", "deepseek"]
    for pref in preferred:
        for m in models:
            if pref in m.lower():
                return m
    return models[0]  # whatever is installed

def ollama_chat(prompt: str, system: str = "", model: str = None) -> str | None:
    """Call Ollama chat API. Returns response text or None."""
    model = model or best_model()
    if not model:
        return None

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = json.dumps({
        "model":    model,
        "messages": messages,
        "stream":   False,
        "options":  {"temperature": 0.3, "num_predict": 2048}
    }).encode()

    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read())
            return data.get("message", {}).get("content", "").strip()
    except urllib.error.URLError:
        return None
    except Exception as e:
        err(f"Ollama error: {e}")
        return None

def parse_json_response(text: str) -> dict | None:
    """Strip markdown fences and parse JSON."""
    if not text:
        return None
    t = text.strip()
    # Remove ```json ... ``` fences
    if t.startswith("```"):
        lines = t.splitlines()
        t = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    # Find first { or [
    for i, ch in enumerate(t):
        if ch in "{[":
            try:
                return json.loads(t[i:])
            except json.JSONDecodeError:
                break
    # Try the whole thing
    try:
        return json.loads(t)
    except:
        return None

# ─────────────────────────────────────────────
# ANTHROPIC FALLBACK
# ─────────────────────────────────────────────
def get_api_key() -> str | None:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key: return key
    cfg = Path(__file__).parent.parent / "config" / "ccl_config.json"
    if cfg.exists():
        key = json.loads(cfg.read_text()).get("anthropic_api_key","")
        if key and key != "YOUR_KEY_HERE": return key
    return None

def save_api_key(key: str):
    cfg_path = Path(__file__).parent.parent / "config" / "ccl_config.json"
    cfg = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
    cfg["anthropic_api_key"] = key
    cfg_path.write_text(json.dumps(cfg, indent=2))

def claude_chat(prompt: str, system: str, api_key: str, max_tokens=3000) -> str | None:
    payload = json.dumps({
        "model": CLAUDE_MODEL, "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()
    req = urllib.request.Request(CLAUDE_URL, data=payload, headers={
        "Content-Type":"application/json",
        "x-api-key": api_key,
        "anthropic-version":"2023-06-01"
    }, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())["content"][0]["text"].strip()
    except:
        return None

# ─────────────────────────────────────────────
# UNIFIED CALL — Ollama first, Claude fallback
# ─────────────────────────────────────────────
def ccl_ai_call(prompt: str, system: str, api_key: str = None,
                want_json: bool = True, max_tokens: int = 3000) -> dict | str | None:
    """
    Try Ollama first (free + local).
    Fall back to Claude API if key is available.
    """
    model = best_model()

    if ollama_running() and model:
        ai(f"Using Ollama ({model}) …")
        raw = ollama_chat(prompt, system, model)
        if raw:
            if want_json:
                result = parse_json_response(raw)
                if result: return result
                # Ollama sometimes adds explanation — retry with stricter prompt
                strict = system + "\n\nIMPORTANT: Respond with ONLY valid JSON. No text before or after."
                raw2 = ollama_chat(prompt, strict, model)
                if raw2:
                    result2 = parse_json_response(raw2)
                    if result2: return result2
            else:
                return raw
        warn("Ollama gave no usable response, trying Claude API …")

    # Claude API fallback
    key = api_key or get_api_key()
    if key:
        ai("Using Claude API …")
        raw = claude_chat(prompt, system, key, max_tokens)
        if raw:
            if want_json: return parse_json_response(raw)
            return raw

    _no_ai_found(model)
    return None

def _no_ai_found(model):
    if not ollama_running():
        warn("Ollama is not running.")
        print(f"""
  {C.CYAN}To start Ollama:{C.RESET}
  {C.GREEN}  ollama serve{C.RESET}          {C.DIM}# in a new terminal{C.RESET}
  {C.GREEN}  ollama pull llama3{C.RESET}    {C.DIM}# download model (~4GB){C.RESET}
  {C.GREEN}  ollama pull mistral{C.RESET}   {C.DIM}# smaller option (~4GB){C.RESET}
  {C.GREEN}  ollama pull phi3{C.RESET}      {C.DIM}# smallest option (~2GB){C.RESET}

  Or get a free Anthropic key: {C.CYAN}console.anthropic.com{C.RESET}
  Then run: {C.YELLOW}ccl setkey YOUR_KEY{C.RESET}
""")
    elif not model:
        warn("Ollama is running but no models installed.")
        print(f"""
  {C.CYAN}Install a model:{C.RESET}
  {C.GREEN}  ollama pull llama3{C.RESET}   {C.DIM}# recommended{C.RESET}
  {C.GREEN}  ollama pull mistral{C.RESET}  {C.DIM}# smaller{C.RESET}
  {C.GREEN}  ollama pull phi3{C.RESET}     {C.DIM}# smallest{C.RESET}
""")

# ─────────────────────────────────────────────
# SYSTEM PROMPTS
# ─────────────────────────────────────────────
SYS_GENERATE = """You are CCL-AI, the code generator inside CapeChain Labs OS.
Generate complete, working code files from a description.

Respond ONLY with valid JSON, no explanation outside JSON:
{
  "files": [
    {"name": "filename.ext", "content": "full file content"},
    {"name": "another.py",   "content": "full content here"}
  ],
  "summary": "one sentence: what was built",
  "run_cmd": "command to run it",
  "dependencies": ["flask", "requests"]
}

Rules:
- All imports included. Code runs immediately without changes.
- For web apps: include index.html + server file
- For APIs: include working routes + README
- Maximum quality. Production-ready code."""

SYS_AGENT = """You are CCL-Agent inside CapeChain Labs OS.
Break a task into clear steps and return a structured plan.

Respond ONLY with valid JSON:
{
  "task": "original task",
  "plan": ["Step 1: ...", "Step 2: ..."],
  "ccl_commands": ["create project \\"name\\"", "install flask"],
  "estimated_time": "~2 minutes",
  "summary": "What will be created"
}"""

SYS_FIX = """You are CCL-Fix, a code debugger inside CapeChain Labs OS.
Read the broken code and error, return the fixed version.

Respond ONLY with valid JSON:
{
  "fixed_code": "complete fixed code here",
  "explanation": "what was wrong",
  "changes": ["Changed X to Y", "Added missing import Z"]
}"""

SYS_EXPLAIN = """You are CCL-Explain inside CapeChain Labs OS.
Explain code clearly. Be concise and practical.

Respond ONLY with valid JSON:
{
  "summary": "one sentence overview",
  "breakdown": ["what line/block does X", "function Y does Z"],
  "concepts": ["concept1", "concept2"],
  "suggestions": ["improvement 1", "improvement 2"]
}"""

SYS_ASK = """You are CCL-AI, a developer assistant inside CapeChain Labs OS.
Answer the developer's question in 3-5 sentences. Be direct and practical.
Give a code example if helpful. No markdown formatting."""

# ─────────────────────────────────────────────
# PUBLIC FUNCTIONS
# ─────────────────────────────────────────────
def generate(description: str, output_dir: str = "generated", api_key: str = None) -> bool:
    print(f"\n{C.MAGENTA}  ◈ CCL-AI generating: \"{description}\"{C.RESET}")
    result = ccl_ai_call(description, SYS_GENERATE, api_key, want_json=True, max_tokens=4000)
    if not result or "files" not in result:
        err("No output received from AI.")
        return False

    from pathlib import Path
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for f in result.get("files", []):
        name    = f.get("name","output.txt")
        content = f.get("content","")
        fpath   = out / name
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(content)
        ok(f"Created: {name}")

    summary = result.get("summary","")
    run_cmd = result.get("run_cmd","")
    deps    = result.get("dependencies",[])

    if summary: print(f"\n{C.CYAN}  ◈ {summary}{C.RESET}")
    if deps:    info(f"Dependencies: {', '.join(deps)}")
    if run_cmd: print(f"{C.YELLOW}  ▶ Run: {run_cmd}{C.RESET}")
    return True

def run_agent(task: str, api_key: str = None) -> dict | None:
    print(f"\n{C.MAGENTA}  ◈ CCL-Agent: \"{task}\"{C.RESET}")
    result = ccl_ai_call(task, SYS_AGENT, api_key, want_json=True, max_tokens=1024)
    if not result:
        return None

    plan = result.get("plan", [])
    cmds = result.get("ccl_commands", [])
    eta  = result.get("estimated_time", "")

    print(f"\n{C.CYAN}  ◈ Plan: {result.get('summary','')}{C.RESET}")
    if eta: print(f"{C.DIM}  Estimated: {eta}{C.RESET}\n")
    for i, step in enumerate(plan, 1):
        print(f"  {C.YELLOW}{i}.{C.RESET} {step}")
    if cmds:
        print(f"\n{C.DIM}  CCL commands:{C.RESET}")
        for c in cmds: print(f"  {C.GREEN}  › {c}{C.RESET}")
    return result

def fix_code(filepath: str, error_msg: str = "", api_key: str = None) -> bool:
    path = Path(filepath)
    if not path.exists():
        err(f"File not found: {filepath}"); return False

    code   = path.read_text()
    prompt = f"File: {filepath}\n\nCode:\n{code}\n\nError:\n{error_msg or 'Review and improve this code'}"

    print(f"\n{C.MAGENTA}  ◈ CCL-Fix: {filepath}{C.RESET}")
    result = ccl_ai_call(prompt, SYS_FIX, api_key, want_json=True, max_tokens=3000)
    if not result: return False

    fixed = result.get("fixed_code","")
    if fixed:
        backup = path.with_suffix(path.suffix + ".bak")
        backup.write_text(code)
        path.write_text(fixed)
        ok(f"Fixed! Original backed up → {backup.name}")

    if result.get("explanation"): print(f"{C.CYAN}  ◈ {result['explanation']}{C.RESET}")
    for c in result.get("changes",[]): print(f"{C.DIM}    • {c}{C.RESET}")
    return True

def explain_code(filepath_or_code: str, api_key: str = None):
    p = Path(filepath_or_code)
    code  = p.read_text() if p.exists() else filepath_or_code
    label = filepath_or_code if p.exists() else "code snippet"

    print(f"\n{C.MAGENTA}  ◈ CCL-Explain: {label}{C.RESET}")
    result = ccl_ai_call(code, SYS_EXPLAIN, api_key, want_json=True, max_tokens=1024)
    if not result: return

    if result.get("summary"): print(f"\n{C.CYAN}  ◈ {result['summary']}{C.RESET}")
    for b in result.get("breakdown",[]): print(f"  {C.DIM}• {b}{C.RESET}")
    concepts = result.get("concepts",[])
    if concepts: print(f"\n{C.YELLOW}  Concepts: {', '.join(concepts)}{C.RESET}")
    for s in result.get("suggestions",[]): print(f"  {C.GREEN}↑ {s}{C.RESET}")

def ask(question: str, api_key: str = None):
    print(f"\n{C.MAGENTA}  ◈ CCL-AI thinking …{C.RESET}")
    result = ccl_ai_call(question, SYS_ASK, api_key, want_json=False, max_tokens=512)
    if result:
        print(f"\n{C.MAGENTA}  ◈ {result}{C.RESET}\n")
    else:
        # static hints if no AI
        hints = {
            "deploy":   "Run: deploy surge   (free, no account needed)",
            "install":  "Run: install <package>   (pip + npm unified)",
            "api":      "Flask: @app.route('/') def fn(): return jsonify({...})",
            "wallet":   "Run: make wallet   then: show wallet",
            "error":    "Read the traceback bottom-up — last line is the root cause.",
            "git":      "Run: save \"message\"   (add + commit + push in one command)",
            "center":   "CSS: display:flex; justify-content:center; align-items:center",
        }
        for kw, hint in hints.items():
            if kw in question.lower():
                ai(hint); return
        ai("Start Ollama: ollama serve  then: ollama pull llama3")

def setup_key(key: str):
    save_api_key(key)
    ok("API key saved.")
    info("AI features now use Claude API as backup to Ollama.")

# ─────────────────────────────────────────────
# STATUS CHECK — call from terminal
# ─────────────────────────────────────────────
def ai_status():
    running = ollama_running()
    models  = ollama_models() if running else []
    key     = get_api_key()

    print(f"\n{C.CYAN}  ◈ AI Status{C.RESET}")
    print(f"  {'─'*36}")
    print(f"  Ollama running : {C.GREEN+'Yes' if running else C.RED+'No'}{C.RESET}")
    if running:
        print(f"  Models         : {C.CYAN}{', '.join(models) if models else 'none installed'}{C.RESET}")
        if models:
            print(f"  Active model   : {C.GREEN}{best_model()}{C.RESET}")
    print(f"  Claude API key : {C.GREEN+'Set ✓' if key else C.DIM+'Not set (optional)'}{C.RESET}")
    print(f"  {'─'*36}")

    if not running:
        print(f"""
  {C.YELLOW}To enable free AI:{C.RESET}

  {C.DIM}# Open a NEW terminal and run:{C.RESET}
  {C.GREEN}  ollama serve{C.RESET}

  {C.DIM}# Then install a model (pick one):{C.RESET}
  {C.GREEN}  ollama pull llama3{C.RESET}   {C.DIM}← recommended (4GB){C.RESET}
  {C.GREEN}  ollama pull phi3{C.RESET}     {C.DIM}← smaller (2GB){C.RESET}
  {C.GREEN}  ollama pull mistral{C.RESET}  {C.DIM}← also good (4GB){C.RESET}

  {C.DIM}# Then come back here and try:{C.RESET}
  {C.GREEN}  generate "a todo app"{C.RESET}
""")
    elif not models:
        print(f"\n  {C.YELLOW}Pull a model:{C.RESET} {C.GREEN}ollama pull llama3{C.RESET}\n")
