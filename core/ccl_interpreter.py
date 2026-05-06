#!/usr/bin/env python3
"""
CCL Interpreter v0.1 FULL — CapeChain Labs
All modules wired: AI generation, tools, templates, P2P share, deploy, git, packages.
"""

import os, sys, json, time, shutil, subprocess
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

class C:
    RESET="\033[0m"; BOLD="\033[1m"; CYAN="\033[96m"; GREEN="\033[92m"
    YELLOW="\033[93m"; RED="\033[91m"; MAGENTA="\033[95m"; DIM="\033[2m"

def ok(m):    print(f"{C.GREEN}  ✓ {m}{C.RESET}")
def info(m):  print(f"{C.CYAN}  → {m}{C.RESET}")
def warn(m):  print(f"{C.YELLOW}  ⚠ {m}{C.RESET}")
def error(m): print(f"{C.RED}  ✗ {m}{C.RESET}")
def ai(m):    print(f"{C.MAGENTA}  ◈ AI › {m}{C.RESET}")

KEYWORDS = {
    "create","build","run","ask","make","send","show","print","set","if","then",
    "else","end","define","deploy","delete","list","connect","import","export",
    "start","stop","install","help","clear","exit","with","to","from","as","and",
    "or","not","type","use","generate","fix","explain","save","receive","share",
    "sync","template","agent","setkey","status","log","call","open","note","version","aistatus","ai"
}

class Token:
    def __init__(self, kind, value): self.kind=kind; self.value=value
    def __repr__(self): return f"Token({self.kind},{self.value!r})"

def lex(line):
    tokens=[]; i=0; line=line.strip()
    if line.startswith("//") or line.startswith("#"): return []
    while i<len(line):
        ch=line[i]
        if ch in " \t": i+=1; continue
        if ch in ('"',"'"):
            q=ch; j=i+1
            while j<len(line) and line[j]!=q: j+=1
            tokens.append(Token("STRING",line[i+1:j])); i=j+1; continue
        if ch.isdigit() or (ch=='-' and i+1<len(line) and line[i+1].isdigit()):
            j=i
            if ch=='-': j+=1
            while j<len(line) and (line[j].isdigit() or line[j]=='.'): j+=1
            tokens.append(Token("NUMBER",float(line[i:j]))); i=j; continue
        # --flags like --dev --global --no-push
        if ch == '-' and i+1 < len(line) and line[i+1] == '-':
            j = i+2
            while j < len(line) and (line[j].isalnum() or line[j] == '-'): j+=1
            flag = line[i:j]   # e.g. "--dev"
            tokens.append(Token("IDENT", flag)); i = j; continue

        if ch in "=<>!{}()[].,;:":
            if ch=='=' and i+1<len(line) and line[i+1]=='=': tokens.append(Token("OP","==")); i+=2
            elif ch=='!' and i+1<len(line) and line[i+1]=='=': tokens.append(Token("OP","!=")); i+=2
            else: tokens.append(Token("OP",ch)); i+=1
            continue
        if ch.isalpha() or ch=='_':
            j=i
            while j<len(line) and (line[j].isalnum() or line[j] in '_-.'): j+=1
            word=line[i:j]
            tokens.append(Token("KEYWORD" if word.lower() in KEYWORDS else "IDENT", word.lower()))
            i=j; continue
        i+=1
    return tokens

class CCLExecutor:
    def __init__(self, config=None):
        self.variables={}; self.config=config or {}
        self.wallet=None; self.notes=[]
        self._ai_mod=None; self._tools=None; self._tpls=None

    def _ai(self):
        if not self._ai_mod:
            try: import ccl_ai as m; self._ai_mod=m
            except ImportError: error("ccl_ai module not found"); return None
        return self._ai_mod

    def _tool(self):
        if not self._tools:
            try: import ccl_tools as m; self._tools=m
            except ImportError: error("ccl_tools module not found"); return None
        return self._tools

    def _tpl(self):
        if not self._tpls:
            try: import ccl_templates as m; self._tpls=m
            except ImportError: error("ccl_templates module not found"); return None
        return self._tpls

    def _resolve(self, t):
        if t.kind=="IDENT" and t.value in self.variables: return self.variables[t.value]
        return t.value
    def _strings(self, tokens): return [self._resolve(t) for t in tokens if t.kind in ("STRING","NUMBER","IDENT")]
    def _kvs(self, tokens):
        p={}; i=0
        while i<len(tokens)-2:
            if tokens[i].kind=="IDENT" and tokens[i+1].kind=="OP" and tokens[i+1].value=="=":
                p[tokens[i].value]=self._resolve(tokens[i+2]); i+=3
            else: i+=1
        return p

    def cmd_generate(self, tokens):
        m=self._ai()
        if not m: return
        parts=[t.value for t in tokens if t.kind in ("STRING","IDENT") and t.value!="into"]
        fi=next((i for i,t in enumerate(tokens) if t.value=="into"),None)
        out=tokens[fi+1].value if fi and fi+1<len(tokens) else "generated"
        desc=" ".join(parts[:fi] if fi else parts)
        if not desc: error("generate: describe what to build"); return
        m.generate(desc, out, api_key=self.config.get("anthropic_api_key"))

    def cmd_fix(self, tokens):
        m=self._ai()
        if not m: return
        s=[t.value for t in tokens if t.kind=="STRING"]
        if not s: error("fix: provide filename"); return
        m.fix_code(s[0], s[1] if len(s)>1 else "", api_key=self.config.get("anthropic_api_key"))

    def cmd_explain(self, tokens):
        m=self._ai()
        if not m: return
        s=[t.value for t in tokens if t.kind in ("STRING","IDENT")]
        if not s: error("explain: provide a file"); return
        m.explain_code(s[0], api_key=self.config.get("anthropic_api_key"))

    def cmd_agent(self, tokens):
        m=self._ai()
        if not m: return
        task=" ".join(t.value for t in tokens if t.kind in ("STRING","IDENT"))
        if not task: error("agent: describe the task"); return
        m.run_agent(task, api_key=self.config.get("anthropic_api_key"))

    def cmd_setkey(self, tokens):
        m=self._ai()
        if not m: return
        v=[t.value for t in tokens if t.kind in ("STRING","IDENT")]
        if not v: error("setkey: provide your Anthropic API key"); return
        m.setup_key(v[0]); self.config["anthropic_api_key"]=v[0]

    def cmd_install(self, tokens):
        t=self._tool()
        if not t: return
        flags=[x.value for x in tokens if x.kind=="IDENT" and x.value.startswith("--")]
        pkgs=[x.value for x in tokens if x.kind in ("STRING","IDENT") and not x.value.startswith("--")]
        if not pkgs: error("install: specify packages"); return
        t.ccl_install(pkgs, flags)

    def cmd_save(self, tokens):
        t=self._tool()
        if not t: return
        s=[x.value for x in tokens if x.kind=="STRING"]
        f=[x.value for x in tokens if x.kind=="IDENT"]
        t.ccl_save(s[0] if s else "", "--no-push" not in f)

    def cmd_status(self, tokens):
        t=self._tool()
        if t: t.ccl_git_status()

    def cmd_log(self, tokens):
        t=self._tool()
        if not t: return
        n=[x.value for x in tokens if x.kind=="NUMBER"]
        t.ccl_git_log(int(n[0]) if n else 5)

    def cmd_deploy(self, tokens):
        t=self._tool()
        if not t: return
        tgts=["vercel","surge","github","ipfs","auto","gh-pages"]
        tgt=next((x.value for x in tokens if x.value in tgts),"auto")
        prj=next((x.value for x in tokens if x.kind=="STRING"),".")
        t.ccl_deploy(tgt, prj)

    def cmd_share(self, tokens):
        t=self._tool()
        if not t: return
        s=[x.value for x in tokens if x.kind=="STRING"]
        if not s: error("share: provide a file path"); return
        t.ccl_share_send(s[0], s[1] if len(s)>1 else "")

    def cmd_receive(self, tokens):
        t=self._tool()
        if not t: return
        v=[x.value for x in tokens if x.kind in ("STRING","IDENT") and x.value!="into"]
        if len(v)<2: error("receive: usage  receive <ip> <pin>"); return
        folder=v[2] if len(v)>2 else "."
        t.ccl_share_receive(v[0], v[1], folder)

    def cmd_sync(self, tokens):
        t=self._tool()
        if not t: return
        s=[x.value for x in tokens if x.kind=="STRING"]
        t.ccl_sync_start(s[0] if s else ".")

    def cmd_use(self, tokens):
        tpl=self._tpl()
        if not tpl: return
        vals=[t.value for t in tokens if t.kind in ("STRING","IDENT") and t.value not in ("template","as","use")]
        if not vals or vals[0]=="template": vals=vals[1:] if vals else []
        if not vals: tpl.list_templates(); return
        tpl.use_template(vals[0], vals[1] if len(vals)>1 else vals[0]+"-project")

    def cmd_note(self, tokens):
        text=" ".join(str(self._resolve(t)) for t in tokens if t.kind in ("STRING","IDENT","NUMBER"))
        if not text: error("note: provide text"); return
        ts=datetime.now().strftime("%H:%M")
        self.notes.append({"time":ts,"text":text})
        nf=Path(".ccl_notes.json")
        try:
            ex=json.loads(nf.read_text()) if nf.exists() else []
            ex.append({"time":ts,"text":text}); nf.write_text(json.dumps(ex,indent=2))
        except: pass
        ok(f"Note saved [{ts}]")

    def cmd_open(self, tokens):
        v=[t.value for t in tokens if t.kind in ("STRING","IDENT")]
        if not v: error("open: provide a file or URL"); return
        opener="xdg-open" if sys.platform=="linux" else "open" if sys.platform=="darwin" else "start"
        try: subprocess.Popen([opener, v[0]]); ok(f"Opened: {v[0]}")
        except Exception as e: error(f"Cannot open: {e}")

    def cmd_version(self, _):
        print(f"\n  {C.CYAN}{C.BOLD}CCL {self.config.get('version','0.1')} \"{self.config.get('codename','Genesis')}\"{C.RESET}")
        print(f"  {C.DIM}CapeChain Labs · AI-Native OS Shell · God Mode{C.RESET}\n")

    def cmd_create(self, tokens):
        if not tokens: error("create: specify target"); return
        target=tokens[0].value
        names=[t.value for t in tokens[1:] if t.kind=="STRING"]
        opts=self._kvs(tokens[1:])
        if target=="file":
            n=names[0] if names else "untitled.txt"; Path(n).touch(); ok(f"Created → {n}")
        elif target in ("folder","directory","dir"):
            n=names[0] if names else "new_folder"; Path(n).mkdir(parents=True,exist_ok=True); ok(f"Created → {n}/")
        elif target=="project":
            n=names[0] if names else "my_project"; pt=opts.get("type","basic")
            pd=Path(n); pd.mkdir(exist_ok=True)
            (pd/"README.md").write_text(f"# {n}\nCreated by CCL 0.1 — CapeChain Labs\n")
            (pd/"main.py").write_text(f'print("Hello from {n} — CCL 0.1")\n')
            (pd/".ccl").write_text(json.dumps({"name":n,"type":pt,"version":"0.1","created":str(datetime.now())},indent=2))
            ok(f"Project '{n}' created (type={pt})")
            info("Files: README.md, main.py, .ccl")
        elif target=="wallet": self.cmd_make([])
        else: error(f"create: unknown target '{target}'")

    def cmd_build(self, tokens):
        if not tokens: error("build: specify target"); return
        target=tokens[0].value
        names=[t.value for t in tokens[1:] if t.kind=="STRING"]
        opts=self._kvs(tokens[1:])
        name=names[0] if names else "my_app"
        if target=="app":
            fe=opts.get("frontend","html"); be=opts.get("backend","python")
            info(f"Building '{name}' — fe={fe} be={be}")
            for s in [f"Scaffolding {fe} …","Setting up {be} …","Wiring routes …","Done!"]:
                print(f"  {C.DIM}  {s}{C.RESET}"); time.sleep(0.25)
            ap=Path(name); ap.mkdir(exist_ok=True)
            (ap/"index.html").write_text(f'<!DOCTYPE html><html><head><title>{name}</title></head><body><h1>{name}</h1><p>CCL 0.1</p></body></html>')
            (ap/"server.py").write_text(f'from flask import Flask,jsonify\napp=Flask(__name__)\n@app.route("/")\ndef i(): return jsonify({{"app":"{name}","ccl":"0.1"}})\nif __name__=="__main__": app.run(debug=True)\n')
            (ap/"requirements.txt").write_text("flask\n")
            (ap/".ccl").write_text(json.dumps({"name":name,"type":"app","frontend":fe,"backend":be},indent=2))
            ok(f"App '{name}' built!")
        elif target in ("api","backend"):
            Path(f"{name}_api.py").write_text(f'from flask import Flask,request,jsonify\napp=Flask(__name__)\nstore=[]\n@app.route("/api",methods=["GET"])\ndef get(): return jsonify({{"data":store}})\n@app.route("/api",methods=["POST"])\ndef post():\n    store.append(request.json); return jsonify({{"ok":True}}),201\nif __name__=="__main__": app.run(debug=True)\n')
            ok(f"API → {name}_api.py")
        elif target in ("contract","smart_contract"):
            cn=name.replace(" ","").replace("-","")
            Path(f"{name}.sol").write_text(f'// SPDX-License-Identifier: MIT\npragma solidity ^0.8.19;\ncontract {cn} {{\n    address public owner;\n    constructor() {{ owner=msg.sender; }}\n}}\n')
            ok(f"Contract → {name}.sol")
        else: error(f"build: unknown target '{target}'")

    def cmd_ask(self, tokens):
        query=" ".join(self._strings(tokens))
        if not query: error("ask: provide a question"); return
        m=self._ai()
        if m: m.ask(query, api_key=self.config.get("anthropic_api_key"))
        else: error("AI module not available")

    def cmd_aistatus(self, tokens):
        m=self._ai()
        if m: m.ai_status()
        else: error("AI module not available")

    def cmd_make(self, tokens):
        target=tokens[0].value if tokens and hasattr(tokens[0],"value") else "wallet"
        if target=="wallet":
            import hashlib,random
            addr="CCL"+hashlib.sha256(str(random.getrandbits(256)).encode()).hexdigest()[:40].upper()
            self.wallet={"address":addr,"balance":"0.0 CCL","chain":"CCL-Devnet","created":str(datetime.now())}
            ok("Wallet created!")
            info(f"Address : {C.CYAN}{addr}{C.RESET}")
            info("Chain   : CCL-Devnet (testnet)")
        else: error(f"make: unknown '{target}'")

    def cmd_show(self, tokens):
        t=tokens[0].value if tokens else "help"
        if t=="wallet":
            if not self.wallet: warn("No wallet. Run: make wallet"); return
            print(f"\n{C.CYAN}  ┌─ CCL Wallet ───────────────────────────┐{C.RESET}")
            for k,v in self.wallet.items(): print(f"  │  {C.BOLD}{k:<12}{C.RESET}{v}")
            print(f"{C.CYAN}  └────────────────────────────────────────┘{C.RESET}\n")
        elif t in ("vars","variables"):
            if not self.variables: info("No variables."); return
            for k,v in self.variables.items(): print(f"  {C.CYAN}{k}{C.RESET} = {v}")
        elif t=="notes":
            nf=Path(".ccl_notes.json")
            notes=json.loads(nf.read_text()) if nf.exists() else self.notes
            if not notes: info("No notes."); return
            for n in notes[-10:]: print(f"  {C.DIM}[{n['time']}]{C.RESET} {n['text']}")
        elif t=="version": self.cmd_version([])
        elif t in ("config","cfg"): print(json.dumps(self.config,indent=2))
        elif t=="templates":
            tpl=self._tpl()
            if tpl: tpl.list_templates()
        else: error(f"show: unknown '{t}'")

    def cmd_print(self, tokens):
        print("  "+" ".join(str(self._resolve(t)) for t in tokens))

    def cmd_set(self, tokens):
        if len(tokens)<3 or tokens[1].value!="=": error("set: usage  set <name> = <value>"); return
        self.variables[tokens[0].value]=self._resolve(tokens[2]); ok(f"'{tokens[0].value}' = {self._resolve(tokens[2])!r}")

    def cmd_list(self, tokens):
        t=tokens[0].value if tokens else "files"
        if t in ("files","file"):
            [print(f"  {C.CYAN}📄{C.RESET} {f.name}  {C.DIM}({f.stat().st_size}B){C.RESET}") for f in Path(".").iterdir() if f.is_file()]
        elif t in ("folders","folder","dir"):
            [print(f"  {C.BLUE}📁{C.RESET} {d.name}/") for d in Path(".").iterdir() if d.is_dir()]
        elif t in ("projects","project"):
            found=[d for d in Path(".").iterdir() if d.is_dir() and (d/".ccl").exists()]
            if not found: info("No CCL projects."); return
            for p in found:
                m=json.loads((p/".ccl").read_text())
                print(f"  {C.GREEN}⬡{C.RESET} {p.name}  {C.DIM}type={m.get('type','?')}{C.RESET}")
        elif t=="templates":
            tpl=self._tpl()
            if tpl: tpl.list_templates()
        elif t=="notes": self.cmd_show([Token("IDENT","notes")])

    def cmd_run(self, tokens):
        v=[t.value for t in tokens if t.kind in ("STRING","IDENT")]
        if not v: error("run: provide filename"); return
        path=Path(v[0])
        if not path.exists(): error(f"Not found: {v[0]}"); return
        if path.suffix==".ccl": CCLInterpreter(self.config).run_file(str(path),self)
        elif path.suffix==".py": subprocess.run([sys.executable,str(path)])
        else: error(f"Unsupported: {path.suffix}")

    def cmd_delete(self, tokens):
        v=[t.value for t in tokens if t.kind=="STRING"]
        if not v: error("delete: specify filename"); return
        p=Path(v[0])
        if not p.exists(): error(f"Not found: {v[0]}"); return
        shutil.rmtree(p) if p.is_dir() else p.unlink()
        ok(f"Deleted: {v[0]}")

    def cmd_help(self, _):
        sections=[
            ("AI FEATURES",""),
            ("generate \"build a todo app\"","AI creates full code files"),
            ("fix <file> [\"error\"]","AI debugs + fixes code"),
            ("explain <file>","AI explains what code does"),
            ("agent \"plan my SaaS\"","AI plans multi-step tasks"),
            ("ask \"how do I deploy\"","AI answers dev questions"),
            ("setkey <key>","Save Anthropic API key"),
            ("PACKAGE MANAGER",""),
            ("install flask react","Install pip/npm packages"),
            ("install express --dev","Dev dependency"),
            ("GIT + DEPLOY",""),
            ("save [\"message\"]","git add+commit+push"),
            ("status","Git status"),
            ("log [n]","Last N commits"),
            ("deploy surge|vercel|github","Deploy to free platform"),
            ("P2P SHARING",""),
            ("share <file> [pin]","Send file to CCL user"),
            ("receive <ip> <pin>","Receive from CCL user"),
            ("sync [folder]","Auto-sync via git"),
            ("TEMPLATES",""),
            ("use template <name> as <project>","Scaffold project"),
            ("list templates","Show all templates"),
            ("PROJECT",""),
            ("create project \"name\"","New project"),
            ("build app|api|contract","Scaffold code"),
            ("make wallet","Generate CCL wallet"),
            ("note <text>","Save quick note"),
            ("show wallet|vars|notes","Display info"),
            ("SYSTEM",""),
            ("run <file.ccl|.py>","Execute script"),
            ("open <file|url>","Open in default app"),
            ("delete <file>","Delete file/folder"),
            ("version","Show CCL version"),
            ("clear / exit","Clear / quit"),
        ]
        print(f"\n{C.BOLD}{C.CYAN}  ╔══ CCL 0.1 GOD MODE — CapeChain Labs ═══════╗{C.RESET}")
        for cmd,desc in sections:
            if desc=="": print(f"\n  {C.DIM}── {cmd} {'─'*(40-len(cmd))}{C.RESET}")
            else: print(f"  {C.GREEN}{cmd:<38}{C.RESET} {C.DIM}{desc}{C.RESET}")
        print(f"\n{C.CYAN}  ╚════════════════════════════════════════════╝{C.RESET}\n")

class CCLInterpreter:
    def __init__(self, config=None):
        self.config=config or {}
        self.executor=CCLExecutor(config)

    def execute_line(self, line, executor=None):
        ex=executor or self.executor
        line=line.strip()
        if not line or line.startswith("//") or line.startswith("#"): return True
        tokens=lex(line)
        if not tokens: return True
        cmd=tokens[0].value; args=tokens[1:]
        dispatch={
            "generate":ex.cmd_generate,"fix":ex.cmd_fix,"explain":ex.cmd_explain,
            "agent":ex.cmd_agent,"setkey":ex.cmd_setkey,"aistatus":ex.cmd_aistatus,"install":ex.cmd_install,
            "save":ex.cmd_save,"status":ex.cmd_status,"log":ex.cmd_log,
            "deploy":ex.cmd_deploy,"share":ex.cmd_share,"receive":ex.cmd_receive,
            "sync":ex.cmd_sync,"use":ex.cmd_use,"note":ex.cmd_note,"open":ex.cmd_open,
            "version":ex.cmd_version,"create":ex.cmd_create,"build":ex.cmd_build,
            "ask":ex.cmd_ask,"make":ex.cmd_make,"show":ex.cmd_show,"print":ex.cmd_print,
            "set":ex.cmd_set,"list":ex.cmd_list,"run":ex.cmd_run,"delete":ex.cmd_delete,
            "help":ex.cmd_help,
            "clear":lambda _: os.system("clear" if os.name!="nt" else "cls"),
            "exit":lambda _: None,
        }
        if cmd=="exit": return False
        if cmd in dispatch:
            try: dispatch[cmd](args)
            except Exception as e: error(f"Error in '{cmd}': {e}")
        else: error(f"Unknown: '{cmd}' — type 'help'")
        return True

    def run_file(self, filepath, executor=None):
        ex=executor or self.executor
        try: lines=Path(filepath).read_text().splitlines()
        except FileNotFoundError: error(f"Not found: {filepath}"); return
        for line in lines:
            if not self.execute_line(line,ex): break

if __name__=="__main__":
    cfg={}
    p=Path("config/ccl_config.json")
    if p.exists(): cfg=json.loads(p.read_text())
    if len(sys.argv)>1: CCLInterpreter(cfg).run_file(sys.argv[1])
    else: print("Usage: python ccl_interpreter.py <script.ccl>\n       Or: python ccl_terminal.py")
