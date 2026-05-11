#!/usr/bin/env python3
import os, sys, json, time, readline, random, shutil, subprocess, threading, math
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent))
from ccl_interpreter import CCLInterpreter, C, ok, info, warn, error

HISTORY_FILE = Path.home() / ".ccl_history"
THEMES_FILE = Path.home() / ".ccl_theme"

THEMES = {
    "cyber": {
        "name": "Neon Cyber", "bg": (5, 5, 25), "fg": (200, 216, 240),
        "accent1": (0, 245, 200), "accent2": (223, 128, 255), "accent3": (0, 191, 255),
        "dim": (80, 100, 130), "success": (57, 255, 135), "warn": (255, 215, 0),
        "prompt_symbol": "⬡"
    },
    "sunset": {
        "name": "Sunset Glow", "bg": (20, 8, 15), "fg": (240, 210, 200),
        "accent1": (255, 107, 107), "accent2": (255, 165, 0), "accent3": (255, 215, 0),
        "dim": (160, 110, 100), "success": (80, 255, 120), "warn": (255, 200, 50),
        "prompt_symbol": "✦"
    },
    "matrix": {
        "name": "Matrix Code", "bg": (0, 8, 0), "fg": (0, 220, 100),
        "accent1": (0, 255, 65), "accent2": (0, 200, 100), "accent3": (100, 255, 150),
        "dim": (0, 120, 50), "success": (0, 255, 128), "warn": (200, 255, 0),
        "prompt_symbol": "▶"
    },
    "dragonskin": {
        "name": "Dragonskin", "bg": (10, 5, 15), "fg": (230, 200, 220),
        "accent1": (255, 56, 128), "accent2": (180, 80, 255), "accent3": (100, 200, 255),
        "dim": (130, 80, 120), "success": (80, 255, 180), "warn": (255, 200, 60),
        "prompt_symbol": "◇"
    },
    "ocean": {
        "name": "Deep Ocean", "bg": (5, 10, 25), "fg": (190, 220, 240),
        "accent1": (0, 180, 216), "accent2": (72, 202, 228), "accent3": (144, 224, 239),
        "dim": (60, 100, 140), "success": (100, 255, 200), "warn": (255, 200, 100),
        "prompt_symbol": "~"
    },
    "midnight": {
        "name": "Midnight Aurora", "bg": (8, 8, 30), "fg": (210, 220, 240),
        "accent1": (0, 255, 170), "accent2": (100, 200, 255), "accent3": (200, 100, 255),
        "dim": (60, 80, 120), "success": (0, 255, 170), "warn": (255, 220, 50),
        "prompt_symbol": "⬡"
    }
}

def load_theme():
    try:
        if THEMES_FILE.exists():
            name = THEMES_FILE.read_text().strip()
            if name in THEMES: return THEMES[name]
    except: pass
    return THEMES["cyber"]

def save_theme(name):
    THEMES_FILE.write_text(name)

def tc(r, g, b, bg=False):
    return f"\033[{'48' if bg else '38'};2;{r};{g};{b}m"

def tcg(r1,g1,b1,r2,g2,b2,steps):
    return [tc(int(r1+(r2-r1)*i/steps),int(g1+(g2-g1)*i/steps),int(b1+(b2-b1)*i/steps)) for i in range(steps)]

class R:
    R="\033[0m"; B="\033[1m"; D="\033[2m"; I="\033[3m"; L="\033[5m"

def rgb(t, r, g, b): return f"{tc(r,g,b)}{t}{R.R}"
def grad_text(text, c1, c2):
    out = ""
    for i, ch in enumerate(text):
        r = int(c1[0] + (c2[0]-c1[0])*i/len(text))
        g = int(c1[1] + (c2[1]-c1[1])*i/len(text))
        b = int(c1[2] + (c2[2]-c1[2])*i/len(text))
        out += f"{tc(r,g,b)}{ch}"
    return out + R.R

_term_lock = threading.Lock()
_anim_running = True

def make_logo(T):
    return f"""
{R.D}╔{'═'*66}{R.R}
{R.D}║{R.R}  {grad_text('██████╗ ██████╗ ██╗     ██████╗ ███████╗ █████╗  ██████╗██╗  ██╗', T['accent1'], T['accent2'])}  {R.D}║{R.R}
{R.D}║{R.R}  {grad_text('██╔════╝██╔═══██╗██║     ██╔══██╗██╔════╝██╔══██╗██╔════╝██║  ██║', T['accent2'], T['accent3'])}  {R.D}║{R.R}
{R.D}║{R.R}  {grad_text('██║     ██║   ██║██║     ██████╔╝█████╗  ███████║██║     ███████║', T['accent3'], T['accent1'])}  {R.D}║{R.R}
{R.D}║{R.R}  {grad_text('██║     ██║   ██║██║     ██╔═══╝ ██╔══╝  ██╔══██║██║     ██╔══██║', T['accent1'], T['accent2'])}  {R.D}║{R.R}
{R.D}║{R.R}  {grad_text('╚██████╗╚██████╔╝███████╗██║     ███████╗██║  ██║╚██████╗██║  ██║', T['accent2'], T['accent3'])}  {R.D}║{R.R}
{R.D}║{R.R}  {grad_text(' ╚═════╝ ╚═════╝ ╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝', T['accent3'], T['accent1'])}  {R.D}║{R.R}
{R.D}║{R.R}  {R.D}{'─'*62}{R.R}  {R.D}║{R.R}
{R.D}║{R.R}  {rgb(f'{R.L}{R.B}✦{R.R}', *T['accent1'])} {rgb('CAPECHAIN LABS', *T['accent1'])}  {rgb(f'{R.L}{R.B}⬡{R.R}', *T['accent2'])} {rgb('OMNIA', *T['accent2'])}  {rgb(f'{R.L}{R.B}❖{R.R}', *T['accent3'])} {rgb('AI-NATIVE OS', *T['accent3'])}  {rgb(f'{R.L}{R.B}◆{R.R}', *T['warn'])} {rgb('MULTIVERSE', *T['warn'])}  {R.D}║{R.R}
{R.D}╚{'═'*66}{R.R}"""

def draw_status_bar(T):
    w, _ = shutil.get_terminal_size((80, 24))
    bar_w = min(w - 4, 72)
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory().percent
        load = os.getloadavg()[0]
        cpu_c = T['success'] if cpu < 50 else T['warn'] if cpu < 80 else (255,80,80)
        mem_c = T['success'] if mem < 50 else T['warn'] if mem < 80 else (255,80,80)
        cpu_bar = f"{tc(*cpu_c)}{'█'*int(cpu/100*20)}{R.D}{'░'*(20-int(cpu/100*20))}{R.R}"
        mem_bar = f"{tc(*mem_c)}{'█'*int(mem/100*20)}{R.D}{'░'*(20-int(mem/100*20))}{R.R}"
        line = f"  CPU {cpu:5.1f}% {cpu_bar}   RAM {mem:5.1f}% {mem_bar}   LOAD {load:.2f}  "
    except:
        line = f"  {'─'*(bar_w-2)}  "
    pad = bar_w - len(line) + 4
    if pad > 0: line += " " * pad
    now = datetime.now().strftime("%H:%M:%S")
    d = datetime.now().strftime("%Y-%m-%d")
    right = f" {d}  {now} "
    line = line[:bar_w-len(right)] + right
    return f"{R.D}┌{line}{R.D}┐{R.R}"

PARTICLES = "✦✧⋅⋆˙⋄∘○●◉◎⬡◆◇❖"
def animate_particles(duration=1.5, T=None):
    if not T: T = load_theme()
    if not sys.stdout.isatty(): return
    w, _ = shutil.get_terminal_size((80, 24))
    bw = min(w-4, 70)
    bh = 5
    start = time.time()
    parts = [{"x": random.randint(0, bw-1), "y": random.randint(0, bh-1),
              "c": random.choice(PARTICLES), "vx": random.uniform(-0.6, 0.6),
              "vy": random.uniform(-0.3, 0.1)} for _ in range(20)]
    try:
        while time.time() - start < duration:
            lines = [" " * bw for _ in range(bh)]
            for p in parts:
                p["x"] = (p["x"] + p["vx"]) % bw
                p["y"] = max(0, min(bh-1, p["y"] + p["vy"]))
                col = random.choice([T['accent1'], T['accent2'], T['accent3'], T['success']])
                l = list(lines[int(p["y"])])
                if 0 <= int(p["x"]) < len(l):
                    l[int(p["x"])] = f"{tc(*col)}{R.B}{p['c']}{R.R}"
                lines[int(p["y"])] = "".join(l)
            sys.stdout.write(f"\033[{bh}A")
            for line in lines:
                sys.stdout.write(f"  {line}\n")
            sys.stdout.flush()
            time.sleep(0.06)
    except: pass

def boot_sequence(T):
    checks = []
    try:
        import psutil
        checks.append(("CPU", True))
        checks.append(("Memory", True))
        checks.append(("Disk", True))
    except: pass
    try:
        from ccl_ai import ollama_running, best_ollama
        o = ollama_running() and best_ollama()
        checks.append(("Ollama AI", o is not None))
    except: checks.append(("AI Engine", False))
    try:
        import requests
        r = requests.get("http://localhost:11434", timeout=2)
        checks.append(("AI Provider", r.ok))
    except: checks.append(("AI Provider", False))
    checks.append(("Shell", True))
    checks.append(("Network", True))

    print(f"\n{R.D}  ════════════════════════════════════════════{R.R}")
    for i, (name, ok_) in enumerate(checks):
        bar_w = 18
        fill = bar_w if ok_ else 3
        empty = bar_w - fill
        col = T['success'] if ok_ else (255,80,80)
        bar = f"{tc(*col)}{'█'*fill}{R.D}{'░'*empty}{R.R}"
        icon = f"{tc(*T['success'])}◉{R.R}" if ok_ else f"{tc(255,80,80)}◉{R.R}"
        lbl = f"{tc(*T['accent1'])}{name:<16}{R.R}"
        sys.stdout.write(f"  {icon} {lbl} {bar}")
        if i < len(checks) - 1:
            sys.stdout.write("\n")
        time.sleep(0.08 + random.random()*0.05)
    print(f"\n{R.D}  ════════════════════════════════════════════{R.R}")

def print_welcome(config):
    T = load_theme()
    ver = config.get("version", "0.3")
    codename = config.get("codename", "OMNIA")
    chain = config.get("chain", "CCL-Net")
    logo = make_logo(T)
    if sys.stdout.isatty():
        sys.stdout.write(f"\033[2J\033[H")
        sys.stdout.write(f"{tc(*T['bg'], bg=True)}")
    sys.stdout.write(f"\n{logo}\n\n")
    if sys.stdout.isatty():
        draw_status_bar(T)
        animate_particles(1.0, T)
    else:
        print(f"  {R.D}{'─'*66}{R.R}")

    try:
        from ccl_ai import get_available_providers, ollama_running, best_ollama
        av = get_available_providers()
        local_c = sum(1 for _, p in av if p.get("type") == "local")
        free_c = sum(1 for _, p in av if p.get("type") == "free")
        paid_c = sum(1 for _, p in av if p.get("type") == "paid")
    except:
        local_c = free_c = paid_c = 0

    tname = T['name']
    sys.stdout.write(f"""
{R.D}  ╔{'═'*66}{R.R}
{R.D}  ║{R.R}  {tc(*T['accent1'])}SYSTEM{R.R}  {tc(*T['success'])}v{ver} "{codename}"{R.R}    {tc(*T['accent2'])}CHAIN{R.R}  {tc(*T['accent3'])}{chain}{R.R}       {tc(*T['accent1'])}THEME{R.R}  {tc(*T['accent2'])}{tname}{R.R}  {R.D}║{R.R}
{R.D}  ║{R.R}  {tc(*T['accent1'])}AI{R.R}     {tc(*T['success'])}{local_c} Local{R.R} · {tc(*T['success'])}{free_c} Free{R.R} · {tc(*T['warn'])}{paid_c} Paid{R.R}              {R.D}type{R.R} {tc(*T['accent1'])}help{R.R}                       {R.D}║{R.R}
{R.D}  ╚{'═'*66}{R.R}

{R.D}  quick: {R.R}{tc(*T['accent1'])}help{R.R}  {R.D}·{R.R}  {tc(*T['accent2'])}ai{R.R}  {R.D}·{R.R}  {tc(*T['accent3'])}calc 2+2{R.R}  {R.D}·{R.R}  {tc(*T['success'])}weather{R.R}  {R.D}·{R.R}  {tc(*T['warn'])}sysinfo{R.R}  {R.D}·{R.R}  {tc(*T['accent1'])}passwd{R.R}  {R.D}·{R.R}  {tc(*T['accent2'])}todo{R.R}
""" .lstrip())
    boot_sequence(T)
    print(f"\n{R.D}  ➜ System ready.{R.R}\n")

def get_prompt(ex):
    T = load_theme()
    cwd = Path.cwd().name or "/"
    w_icon = f"{tc(*T['accent2'])}{R.B}{T['prompt_symbol']}{R.R}" if ex.wallet else f"{R.D}{T['prompt_symbol']}{R.R}"
    now = datetime.now().strftime("%H:%M")
    addr = ex.wallet["address"][:8] + "…" if ex.wallet else "------"
    ai_ok = f"{tc(*T['success'])}{R.B}◉{R.R}"
    try:
        from ccl_ai import ollama_running
        if not ollama_running(): ai_ok = f"{R.D}◯{R.R}"
    except: pass
    git = ""
    try:
        branch = subprocess.check_output(["git", "branch", "--show-current"], stderr=subprocess.DEVNULL, text=True).strip()
        if branch: git = f" {tc(*T['dim'])}⎇ {branch}{R.R}"
    except: pass
    c1 = T['accent1']; c2 = T['accent2']; d = T['dim']
    user = os.environ.get("USER", "user")
    return (
        f"\n{tc(*d)}┌─({R.R}{tc(*c1)}{R.B}CCL{R.R}{tc(*d)})─({R.R}{tc(*T['success'])}{cwd}{R.R}{tc(*d)})─({R.R}"
        f"{tc(*c2)}{addr}{R.R}{tc(*d)})─({R.R}{ai_ok}{tc(*d)})─({R.R}{now}{tc(*d)}){git}{R.R}\n"
        f"{tc(*d)}└>{R.R}{w_icon} "
    )

COMPLETIONS = [
    "help", "clear", "exit", "version",
    "ai", "ask ", "chat ", "generate ", "agent ", "fix ", "explain ", "setkey ",
    "create file ", "create folder ", "create project ", "create wallet ",
    "build app ", "build api ", "build contract ",
    "show wallet", "show vars", "show config", "show version", "show ai", "show notes",
    "list files", "list folders", "list projects", "list templates", "list notes",
    "set ", "print ", "run ", "deploy ", "note ",
    "use template ", "install ", "save ", "status ", "log ",
    "open ", "delete ", "make wallet", "sync ",
    "calc ", "weather ", "sysinfo", "passwd ", "uuid", "hash ",
    "base64 encode ", "base64 decode ", "json ", "banner ",
    "matrix", "fortune", "colors", "ip", "date", "cal", "uptime",
    "echo ", "random ", "flip", "roll ", "timer ", "todo ",
    "ping ", "curl ", "search ", "whois ", "dns ",
    "theme ", "neofetch", "cowsay ", "figlet ",
]

def comp(text, state):
    o = [c for c in COMPLETIONS if c.startswith(text)]
    if state < len(o): return o[state]
    return None

readline.set_completer(comp)
readline.parse_and_bind("tab: complete")

BLOCK_STARTERS = ("if ", "define ", "for ")
BLOCK_ENDER = "end"

def collect_block(first_line):
    T = load_theme()
    lines = [first_line]
    print(f"  {tc(*T['dim'])}⋮ block mode — type 'end' to finish{R.R}")
    while True:
        try: cont = input(f"  {tc(*T['dim'])}⋮  {R.R}").strip()
        except (EOFError, KeyboardInterrupt): break
        lines.append(cont)
        if cont.lower() == BLOCK_ENDER: break
    return lines

def execute_block(lines, interp):
    from ccl_interpreter import lex, Token
    ex = interp.executor
    h = lines[0].strip()
    t = lex(h)
    if t and t[0].value == "if":
        try: lhs_t = t[1]; op_t = t[2]; rhs_t = t[3]
        except IndexError: error("if <a> == <b> then"); return
        lhs = ex._resolve(lhs_t); rhs = ex._resolve(rhs_t); op = op_t.value
        cond = {"==": str(lhs) == str(rhs), "!=": str(lhs) != str(rhs)}.get(op, False)
        bi, be, ie = [], [], False
        for l in lines[1:]:
            s = l.strip()
            if s.lower() == "else": ie = True
            elif s.lower() == "end": break
            elif ie: be.append(s)
            else: bi.append(s)
        for l in (bi if cond else be): interp.execute_line(l, ex)
    elif t and t[0].value == "define":
        n = t[1].value if len(t) > 1 else "unnamed"
        b = [l.strip() for l in lines[1:] if l.strip().lower() not in ("end", "{", "}")]
        ex.variables[f"__macro_{n}"] = b
        ok(f"Macro '{n}' defined ({len(b)} steps)")

def set_bg():
    T = load_theme()
    sys.stdout.write(f"{tc(*T['bg'], bg=True)}")
    sys.stdout.flush()

def run_terminal():
    config = {}
    cfg = Path(__file__).parent.parent / "config" / "ccl_config.json"
    if cfg.exists(): config = json.loads(cfg.read_text())
    interp = CCLInterpreter(config)
    ex = interp.executor
    ex.config = config
    try: readline.read_history_file(str(HISTORY_FILE))
    except: pass
    set_bg()
    print_welcome(config)
    while True:
        try:
            set_bg()
            raw = input(get_prompt(ex)).strip()
        except KeyboardInterrupt: print(f"\n{R.D}  (Ctrl+C){R.R}"); continue
        except EOFError: break
        if not raw: continue
        if any(raw.lower().startswith(s) for s in BLOCK_STARTERS):
            execute_block(collect_block(raw), interp); continue
        if raw.lower().startswith("call "):
            mn = raw[5:].strip(); k = f"__macro_{mn}"
            if k in ex.variables:
                for s in ex.variables[k]: interp.execute_line(s, ex)
            else: error(f"Macro '{mn}' not defined")
            continue
        if raw.lower() in ("exit", "quit"):
            try: readline.write_history_file(str(HISTORY_FILE))
            except: pass
            print(f"\n{tc(*load_theme()['accent1'])}{R.B}  ⬡ CCL OMNIA — till next time. {R.R}\n")
            break
        if raw.lower() == "clear":
            os.system("clear" if os.name != "nt" else "cls")
            set_bg()
            continue
        if not interp.execute_line(raw, ex): break
    try: readline.write_history_file(str(HISTORY_FILE))
    except: pass

if __name__ == "__main__":
    run_terminal()
