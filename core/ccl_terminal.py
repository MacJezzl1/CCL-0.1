#!/usr/bin/env python3
"""
CCL Terminal v0.1
CapeChain Labs — Interactive AI-Native Shell
Run this file to enter the CCL interactive environment.
"""

import os
import sys
import json
import time
import readline  # enables arrow keys + history in input()
from pathlib import Path
from datetime import datetime

# Add parent dir to path so we can import interpreter
sys.path.insert(0, str(Path(__file__).parent))
from ccl_interpreter import CCLInterpreter, C, ok, info, warn, error

# ─────────────────────────────────────────────
# HISTORY — persist command history across sessions
# ─────────────────────────────────────────────
HISTORY_FILE = Path.home() / ".ccl_history"

def load_history():
    try:
        if HISTORY_FILE.exists():
            readline.read_history_file(str(HISTORY_FILE))
    except Exception:
        pass

def save_history():
    try:
        readline.write_history_file(str(HISTORY_FILE))
    except Exception:
        pass

# ─────────────────────────────────────────────
# TAB COMPLETION
# ─────────────────────────────────────────────
COMPLETIONS = [
    "create file ", "create folder ", "create project ",
    "build app ", "build api ", "build contract ",
    "ask ", "make wallet", "show wallet", "show vars",
    "show version", "show config", "list files", "list folders",
    "list projects", "set ", "print ", "run ", "deploy ",
    "help", "clear", "exit"
]

def completer(text, state):
    options = [c for c in COMPLETIONS if c.startswith(text)]
    if state < len(options):
        return options[state]
    return None

readline.set_completer(completer)
readline.parse_and_bind("tab: complete")

# ─────────────────────────────────────────────
# STATUS BAR
# ─────────────────────────────────────────────
def status_bar(executor):
    cwd     = Path.cwd().name
    wallet  = "◎ " + executor.wallet["address"][:12] + "…" if executor.wallet else "no wallet"
    now     = datetime.now().strftime("%H:%M")
    varcount = len(executor.variables)
    return (
        f"{C.DIM}┤ {C.CYAN}ccl{C.RESET}{C.DIM}@{C.RESET}"
        f"{C.GREEN}{cwd}{C.DIM} │ {C.MAGENTA}{wallet}"
        f"{C.DIM} │ vars:{varcount} │ {now} ├{C.RESET}"
    )

# ─────────────────────────────────────────────
# PROMPT
# ─────────────────────────────────────────────
def get_prompt(executor):
    cwd  = Path.cwd().name
    wl   = f"{C.MAGENTA}◎{C.RESET} " if executor.wallet else ""
    return (
        f"\n{wl}{C.CYAN}{C.BOLD}CCL{C.RESET}"
        f"{C.DIM}@{C.RESET}{C.GREEN}{cwd}{C.RESET}"
        f"{C.YELLOW} ›{C.RESET} "
    )

# ─────────────────────────────────────────────
# MULTILINE BLOCK — handle if/define blocks
# ─────────────────────────────────────────────
BLOCK_STARTERS = ("if ", "define ")
BLOCK_ENDER    = "end"

def collect_block(first_line: str) -> list[str]:
    """Collect lines until 'end' for block commands."""
    lines = [first_line]
    print(f"  {C.DIM}(block mode — type 'end' to finish){C.RESET}")
    while True:
        try:
            cont = input(f"  {C.DIM}…  {C.RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            break
        lines.append(cont)
        if cont.lower() == BLOCK_ENDER:
            break
    return lines

# ─────────────────────────────────────────────
# BLOCK EXECUTOR — handle if/then/else/end
# ─────────────────────────────────────────────
def execute_block(lines: list[str], interp: CCLInterpreter):
    """Execute a collected if/else/end block."""
    from ccl_interpreter import lex, Token
    ex = interp.executor

    header = lines[0].strip()
    tokens = lex(header)

    # --- IF block ---
    if tokens and tokens[0].value == "if":
        # Extract: if <lhs> <op> <rhs> then
        try:
            lhs_tok = tokens[1]
            op_tok  = tokens[2]
            rhs_tok = tokens[3]
        except IndexError:
            error("if: usage is  if <a> == <b> then")
            return

        lhs = ex._resolve(lhs_tok)
        rhs = ex._resolve(rhs_tok)
        op  = op_tok.value

        cond = {
            "==": str(lhs) == str(rhs),
            "!=": str(lhs) != str(rhs),
            "<":  float(lhs) <  float(rhs) if _is_num(lhs, rhs) else False,
            ">":  float(lhs) >  float(rhs) if _is_num(lhs, rhs) else False,
        }.get(op, False)

        # Split into if-body and else-body
        body_if   = []
        body_else = []
        in_else   = False
        for line in lines[1:]:
            stripped = line.strip()
            if stripped.lower() == "else":
                in_else = True
            elif stripped.lower() == "end":
                break
            elif in_else:
                body_else.append(stripped)
            else:
                body_if.append(stripped)

        branch = body_if if cond else body_else
        for l in branch:
            interp.execute_line(l, ex)

    # --- DEFINE block (macro) ---
    elif tokens and tokens[0].value == "define":
        name = tokens[1].value if len(tokens) > 1 else "unnamed"
        body = [l.strip() for l in lines[1:] if l.strip().lower() not in ("end", "{", "}")]
        ex.variables[f"__macro_{name}"] = body
        ok(f"Macro '{name}' defined ({len(body)} steps)")


def _is_num(*vals):
    try:
        [float(v) for v in vals]
        return True
    except (ValueError, TypeError):
        return False

# ─────────────────────────────────────────────
# WELCOME BANNER (compact — no boot needed)
# ─────────────────────────────────────────────
def print_welcome():
    print(f"""
{C.CYAN}{C.BOLD}  ╔══════════════════════════════════════════╗
  ║  ⬡  CCL Terminal  v0.1                  ║
  ║     CapeChain Labs OS Shell              ║
  ╚══════════════════════════════════════════╝{C.RESET}
{C.DIM}  Type {C.RESET}{C.GREEN}help{C.RESET}{C.DIM} to see commands.
  Tab-completion and history (↑↓) enabled.{C.RESET}
""")

# ─────────────────────────────────────────────
# MAIN REPL LOOP
# ─────────────────────────────────────────────
def run_terminal():
    # Load config
    config = {}
    cfg = Path(__file__).parent.parent / "config" / "ccl_config.json"
    if cfg.exists():
        config = json.loads(cfg.read_text())

    interp = CCLInterpreter(config)
    ex     = interp.executor

    load_history()
    print_welcome()

    while True:
        try:
            prompt = get_prompt(ex)
            raw    = input(prompt).strip()
        except KeyboardInterrupt:
            print(f"\n{C.DIM}  (Ctrl+C — type 'exit' to quit){C.RESET}")
            continue
        except EOFError:
            break

        if not raw:
            continue

        # Multi-line block detection
        if any(raw.lower().startswith(s) for s in BLOCK_STARTERS):
            block = collect_block(raw)
            execute_block(block, interp)
            continue

        # Macro invocation: call <name>
        if raw.lower().startswith("call "):
            macro_name = raw[5:].strip()
            key = f"__macro_{macro_name}"
            if key in ex.variables:
                info(f"Running macro '{macro_name}' …")
                for step in ex.variables[key]:
                    interp.execute_line(step, ex)
            else:
                error(f"Macro '{macro_name}' not defined. Use: define {macro_name} {{ ... end }}")
            continue

        # Normal single-line execution
        keep_going = interp.execute_line(raw, ex)
        if not keep_going:
            save_history()
            print(f"\n{C.CYAN}  Goodbye. — CapeChain Labs ⬡{C.RESET}\n")
            sys.exit(0)

    save_history()


# ─────────────────────────────────────────────
if __name__ == "__main__":
    run_terminal()
