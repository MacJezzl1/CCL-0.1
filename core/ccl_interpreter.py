#!/usr/bin/env python3
import os, sys, json, time, shutil, subprocess, hashlib, base64, uuid, random, math, socket, struct, textwrap, threading
from pathlib import Path
from datetime import datetime, date
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
    "sync","template","agent","setkey","status","log","call","open","note","version","aistatus","ai",
    "calc","weather","sysinfo","passwd","uuid","hash","base64","json","banner","matrix",
    "fortune","colors","ip","date","cal","uptime","echo","random","flip","roll",
    "timer","todo","ping","curl","search","whois","dns","theme","neofetch","cowsay","figlet","chat"
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
        if ch == '-' and i+1 < len(line) and line[i+1] == '-':
            j = i+2
            while j < len(line) and (line[j].isalnum() or line[j] == '-'): j+=1
            tokens.append(Token("IDENT", line[i:j])); i = j; continue
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
        self._timer_start=None; self._timer_running=False; self._chat_history=[]
        self._todo_file = Path(".ccl_todo.json")

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
        if len(v) < 2: error("setkey: usage: setkey openai|claude|gemini <key>"); return
        m.setup_key(v[0], v[1])

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
            (pd/"README.md").write_text(f"# {n}\nCreated by CCL — CapeChain Labs\n")
            (pd/"main.py").write_text(f'print("Hello from {n} — CCL")\n')
            (pd/".ccl").write_text(json.dumps({"name":n,"type":pt,"version":"0.3","created":str(datetime.now())},indent=2))
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
            (ap/"index.html").write_text(f'<!DOCTYPE html><html><head><title>{name}</title></head><body><h1>{name}</h1><p>CCL</p></body></html>')
            (ap/"server.py").write_text(f'from flask import Flask,jsonify\napp=Flask(__name__)\n@app.route("/")\ndef i(): return jsonify({{"app":"{name}","ccl":"0.3"}})\nif __name__=="__main__": app.run(debug=True)\n')
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
    def cmd_ai(self, tokens):
        self.cmd_aistatus(tokens)

    def cmd_chat(self, tokens):
        msg = " ".join(self._strings(tokens))
        if not msg:
            if self._chat_history:
                print(f"\n  {C.CYAN}Chat session ended ({len(self._chat_history)} messages){C.RESET}\n")
                self._chat_history = []
            else: info("chat <message>  or  chat  to end session")
            return
        m = self._ai()
        if not m: return
        self._chat_history.append({"role": "user", "content": msg})
        prompt = "\n".join(f"{h['role']}: {h['content']}" for h in self._chat_history[-10:])
        system = "You are CCL Chat, a helpful AI assistant. Be concise and practical."
        print(f"\n{C.MAGENTA}  ◈ CCL Chat …{C.RESET}")
        r = m.smart_ask(prompt, system, want_json=False, max_tokens=1024)
        if r:
            self._chat_history.append({"role": "assistant", "content": r})
            print(f"\n{C.CYAN}  ◈ {r}{C.RESET}\n")
        else: error("No AI response. Set a key: setkey gemini <key>")

    def cmd_make(self, tokens):
        target=tokens[0].value if tokens and hasattr(tokens[0],"value") else "wallet"
        if target=="wallet":
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

    def cmd_calc(self, tokens, raw_text=""):
        expr = raw_text or " ".join(str(self._resolve(t)) for t in tokens)
        if not expr: error("calc: provide expression (e.g. calc 2+2*3)"); return
        clean = expr.replace("^", "**").replace("×", "*").replace("÷", "/")
        from math import pi, sqrt, sin, cos, tan, log, floor, ceil, pow, radians, degrees, e, exp, factorial as fact
        namespace = {"pi": pi, "e": e, "sqrt": sqrt, "sin": sin, "cos": cos, "tan": tan, "log": log, "floor": floor, "ceil": ceil, "pow": pow, "radians": radians, "degrees": degrees, "exp": exp, "abs": abs, "fact": fact}
        try:
            result = eval(clean, {"__builtins__": {}}, namespace)
            if isinstance(result, float) and result == int(result): result = int(result)
            print(f"  {C.CYAN}= {result}{C.RESET}")
        except Exception as e:
            error(f"calc: {e}")

    def cmd_weather(self, tokens):
        city = " ".join(str(self._resolve(t)) for t in tokens) or ""
        try:
            import requests
            url = f"https://wttr.in/{city.replace(' ', '+')}?format=4&m"
            r = requests.get(url, timeout=10, headers={"User-Agent": "curl/8.0"})
            if r.ok and r.text.strip():
                print(f"  {C.CYAN}⛅ {r.text.strip()}{C.RESET}")
            else:
                url2 = f"https://wttr.in/{city.replace(' ', '+')}?format=%l:+%t+%h+%w&m"
                r2 = requests.get(url2, timeout=10, headers={"User-Agent": "curl/8.0"})
                if r2.ok and r2.text.strip():
                    print(f"  {C.CYAN}⛅ {r2.text.strip()}{C.RESET}")
                else: error("Weather unavailable")
        except Exception as e:
            error(f"Weather: {e}")

    def cmd_sysinfo(self, tokens):
        try:
            import psutil
            cpu_pct = psutil.cpu_percent(interval=0.3)
            cpu_count = psutil.cpu_count()
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net = psutil.net_io_counters()
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            days = uptime.days
            hours = uptime.seconds // 3600
            mins = (uptime.seconds % 3600) // 60
            load = os.getloadavg()
            print(f"""
  {C.CYAN}CPU:{C.RESET}       {cpu_pct}% used ({cpu_count} cores)  load: {load[0]:.1f} {load[1]:.1f} {load[2]:.1f}
  {C.GREEN}RAM:{C.RESET}      {mem.used/1024**3:.1f}GB / {mem.total/1024**3:.1f}GB ({mem.percent}%)
  {C.YELLOW}DISK:{C.RESET}     {disk.used/1024**3:.1f}GB / {disk.total/1024**3:.1f}GB ({disk.percent}%)
  {C.MAGENTA}NET:{C.RESET}      ↓ {net.bytes_recv/1024**2:.1f}MB  ↑ {net.bytes_sent/1024**2:.1f}MB
  {C.CYAN}UPTIME:{C.RESET}    {days}d {hours}h {mins}m
  {C.GREEN}PROCESSES:{C.RESET} {len(psutil.pids())}
  {C.DIM}Host: {os.uname().nodename}  Python: {sys.version.split()[0]}{C.RESET}""")
        except ImportError:
            error("sysinfo requires psutil (pip install psutil)")

    def cmd_passwd(self, tokens):
        length = 16
        if tokens and tokens[0].kind == "NUMBER": length = int(tokens[0].value)
        length = max(8, min(128, length))
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{}|;:,.<>?"
        pw = "".join(random.choice(chars) for _ in range(length))
        strength = "weak"
        checks = sum([any(c.islower() for c in pw), any(c.isupper() for c in pw), any(c.isdigit() for c in pw), any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in pw)])
        strength = ["weak", "fair", "good", "strong", "very strong"][checks]
        print(f"  {C.CYAN}🔑 {pw}{C.RESET}")
        print(f"  {C.DIM}  {length} chars | {strength}{C.RESET}")

    def cmd_uuid(self, tokens):
        print(f"  {C.CYAN}🆔 {uuid.uuid4()}{C.RESET}")

    def cmd_hash(self, tokens):
        text = " ".join(str(self._resolve(t)) for t in tokens)
        if not text: error("hash: provide text"); return
        print(f"  {C.CYAN}MD5:    {hashlib.md5(text.encode()).hexdigest()}{C.RESET}")
        print(f"  {C.GREEN}SHA1:   {hashlib.sha1(text.encode()).hexdigest()}{C.RESET}")
        print(f"  {C.YELLOW}SHA256: {hashlib.sha256(text.encode()).hexdigest()}{C.RESET}")

    def cmd_base64(self, tokens):
        if not tokens: error("base64: usage: base64 encode|decode <text>"); return
        op = tokens[0].value
        rest = " ".join(str(self._resolve(t)) for t in tokens[1:])
        if not rest: error("base64: provide text"); return
        try:
            if op in ("encode", "enc"):
                result = base64.b64encode(rest.encode()).decode()
            elif op in ("decode", "dec"):
                result = base64.b64decode(rest).decode()
            else:
                error("base64: use encode or decode"); return
            print(f"  {C.CYAN}{result}{C.RESET}")
        except Exception as e:
            error(f"base64: {e}")

    def cmd_json(self, tokens):
        text = " ".join(str(self._resolve(t)) for t in tokens)
        if not text:
            error("json: provide JSON string or pipe file content"); return
        try:
            parsed = json.loads(text)
            print(f"  {C.GREEN}✓ Valid JSON{C.RESET}")
            print(f"  {C.CYAN}{json.dumps(parsed, indent=2)}{C.RESET}")
        except json.JSONDecodeError as e:
            error(f"Invalid JSON: {e}")

    def cmd_banner(self, tokens):
        text = " ".join(str(self._resolve(t)) for t in tokens)
        if not text: error("banner: provide text"); return
        for ch in text.upper():
            bits = {
                'A': [" ██╗  "," ██╔╝  "," █████╗"," ╚══██║"," █████║"," ╚════╝"],
                'B': ["████╗  ","██╔═╝  ","████╗  ","██╔═╝  ","████╗  ","╚═══╝  "],
                'C': [" █████╗","██╔════╝","██║     ","██║     ","╚██████╗"," ╚═════╝"],
                'D': ["████╗  ","██╔═╝  ","██║    ","██║    ","████╗  ","╚═══╝  "],
                'E': ["██████╗","██╔════╝","█████╗ ","██╔══╝ ","██████╗","╚═════╝"],
                'F': ["██████╗","██╔════╝","█████╗ ","██╔══╝ ","██║    ","╚═╝    "],
                'L': ["██║    ","██║    ","██║    ","██║    ","██████╗","╚═════╝"],
                'M': ["███╗   ██╗","████╗  ██║","██╔██╗ ██║","██║╚██╗██║","██║ ╚████║","╚═╝  ╚═══╝"],
                'N': ["███╗   ██╗","████╗  ██║","██╔██╗ ██║","██║╚██╗██║","██║ ╚████║","╚═╝  ╚═══╝"],
                'O': [" █████╗ ","██╔══██╗","██║  ██║","██║  ██║","╚██████║"," ╚═════╝"],
                'P': ["██████╗ ","██╔══██╗","██████╔╝","██╔═══╝ ","██║     ","╚═╝     "],
                'R': ["██████╗ ","██╔══██╗","██████╔╝","██╔══██╗","██║  ██║","╚═╝  ╚═╝"],
                'S': [" ██████╗","██╔════╝","╚█████╗ "," ╚═══██╗","██████╔╝","╚═════╝ "],
                'T': ["████████╗","╚══██╔══╝","   ██║   ","   ██║   ","   ██║   ","   ╚═╝   "],
                'U': ["██╗  ██╗","██║  ██║","██║  ██║","██║  ██║","╚██████║"," ╚═════╝"],
                'X': ["██╗  ██╗","╚██╗██╔╝"," ╚███╔╝ "," ██╔██╗ ","██╔╝ ██╗","╚═╝  ╚═╝"],
            }
            default = ["      ","      ","      ","      ","      ","      "]
            lines = bits.get(ch.upper(), default)
            for i, l in enumerate(lines):
                if i == 0: print(f"  {C.CYAN}{l}{C.RESET}", end="")
                else: print(f"  {l}", end="")
            print("  ", end="")
        print()

    def cmd_matrix(self, tokens):
        try:
            cols = shutil.get_terminal_size((80, 24)).columns
            for _ in range(60):
                line = ""
                for _ in range(cols):
                    line += random.choice(["0", "1"]) if random.random() > 0.5 else " "
                colors = [f"\033[38;2;0;{200+random.randint(0,55)};0m", f"\033[38;2;0;{150+random.randint(0,55)};50m"]
                print(f"{random.choice(colors)}{line}{C.RESET}", end="\r")
                time.sleep(0.04)
            print(C.RESET)
        except: pass

    def cmd_fortune(self, tokens):
        quotes = [
            ("The best way to predict the future is to invent it.", "Alan Kay"),
            ("Any fool can write code that a computer can understand. Good programmers write code that humans can understand.", "Martin Fowler"),
            ("First, solve the problem. Then, write the code.", "John Johnson"),
            ("It's not a bug — it's an undocumented feature.", "Anonymous"),
            ("Code is like humor. When you have to explain it, it's bad.", "Cory House"),
            ("Make it work, make it right, make it fast.", "Kent Beck"),
            ("The only way to do great work is to love what you do.", "Steve Jobs"),
            ("Talk is cheap. Show me the code.", "Linus Torvalds"),
            ("Software is a great combination of art and engineering.", "Bill Gates"),
            ("Debugging is twice as hard as writing the code in the first place.", "Brian Kernighan"),
            ("Simplicity is the ultimate sophistication.", "Leonardo da Vinci"),
            ("In the middle of difficulty lies opportunity.", "Albert Einstein"),
            ("The impediment to action advances action. What stands in the way becomes the way.", "Marcus Aurelius"),
            ("We are what we repeatedly do. Excellence, then, is not an act, but a habit.", "Aristotle"),
            ("Do or do not. There is no try.", "Yoda"),
            ("The unexamined life is not worth living.", "Socrates"),
            ("It does not matter how slowly you go as long as you do not stop.", "Confucius"),
            ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
            ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt"),
            ("The only limit to our realization of tomorrow will be our doubts of today.", "Franklin D. Roosevelt"),
            ("Courage is not the absence of fear, but rather the judgment that something is more important than fear.", "Ambrose Redmoon"),
            ("You miss 100% of the shots you don't take.", "Wayne Gretzky"),
            ("The best time to plant a tree was 20 years ago. The second best time is now.", "Chinese Proverb"),
            ("Type 'help' to see available commands.", "CCL OS"),
            ("Try 'weather' for today's forecast.", "CCL OS"),
            ("Set an AI key with: setkey gemini YOUR_KEY", "CCL OS"),
            ("Create something amazing today.", "CCL OS"),
        ]
        q, a = random.choice(quotes)
        print(f"\n  {C.CYAN}\"{q}\"{C.RESET}")
        print(f"  {C.DIM}— {a}{C.RESET}\n")

    def cmd_colors(self, tokens):
        print(f"\n  {C.BOLD}ANSI Color Palette:{C.RESET}\n")
        for i in range(0, 16):
            print(f"  \033[48;5;{i}m  \033[0m ", end="")
        print("\n")
        for i in range(16, 232, 36):
            for j in range(36):
                if i + j < 232:
                    print(f"  \033[48;5;{i+j}m  \033[0m ", end="")
            print()
        print(f"\n  {C.DIM}256 colors available via ANSI escape codes{C.RESET}\n")

    def cmd_ip(self, tokens):
        hostname = socket.gethostname()
        print(f"  {C.CYAN}Hostname:{C.RESET} {hostname}")
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            print(f"  {C.GREEN}Public IP:{C.RESET} {s.getsockname()[0]}")
            s.close()
        except: pass
        try:
            import subprocess
            r = subprocess.check_output(["hostname", "-I"], text=True).strip()
            if r:
                ips = r.split()
                for ip in ips:
                    if not ip.startswith("127."):
                        print(f"  {C.YELLOW}LAN IP:{C.RESET} {ip}")
        except: pass
        try:
            r = subprocess.check_output(["curl", "-s", "ifconfig.me"], timeout=5, text=True).strip()
            if r: print(f"  {C.MAGENTA}External:{C.RESET} {r}")
        except: pass

    def cmd_date(self, tokens):
        now = datetime.now()
        print(f"  {C.CYAN}{now.strftime('%A, %B %d, %Y')}{C.RESET}")
        print(f"  {C.GREEN}{now.strftime('%I:%M:%S %p')}{C.RESET}")
        print(f"  {C.DIM}Timezone: {time.tzname}{C.RESET}")

    def cmd_cal(self, tokens):
        try:
            import calendar
            cal = calendar.TextCalendar()
            lines = cal.formatmonth(datetime.now().year, datetime.now().month).splitlines()
            print(f"  {C.CYAN}{lines[0]}{C.RESET}")
            for l in lines[1:]:
                print(f"  {l}")
        except: pass

    def cmd_uptime(self, tokens):
        try:
            with open("/proc/uptime", "r") as f:
                uptime_seconds = float(f.read().split()[0])
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            mins = int((uptime_seconds % 3600) // 60)
            print(f"  {C.CYAN}⏱ {days}d {hours}h {mins}m{C.RESET}")
        except:
            import psutil
            bt = datetime.fromtimestamp(psutil.boot_time())
            delta = datetime.now() - bt
            print(f"  {C.CYAN}⏱ {delta.days}d {delta.seconds//3600}h {(delta.seconds%3600)//60}m{C.RESET}")

    def cmd_echo(self, tokens):
        print("  " + " ".join(str(self._resolve(t)) for t in tokens))

    def cmd_random(self, tokens):
        if len(tokens) >= 2 and tokens[0].kind == "NUMBER" and tokens[1].kind == "NUMBER":
            a, b = int(tokens[0].value), int(tokens[1].value)
            print(f"  {C.CYAN}{random.randint(min(a,b), max(a,b))}{C.RESET}")
        elif tokens and tokens[0].kind == "NUMBER":
            print(f"  {C.CYAN}{random.randint(0, int(tokens[0].value))}{C.RESET}")
        else:
            print(f"  {C.CYAN}{random.randint(0, 100)}{C.RESET}")

    def cmd_flip(self, tokens):
        result = random.choice(["HEADS", "TAILS"])
        art = {"HEADS": "  ┌─────────┐\n  │  █████  │\n  │ ███████ │\n  │ ███████ │\n  │  █████  │\n  └─────────┘",
               "TAILS": "  ┌─────────┐\n  │ ███████ │\n  │█████████│\n  │█████████│\n  │ ███████ │\n  └─────────┘"}
        print(f"\n  {C.CYAN}{art[result]}{C.RESET}")
        print(f"  {C.GREEN}→ {result}!{C.RESET}\n")

    def cmd_roll(self, tokens):
        sides = int(tokens[0].value) if tokens and tokens[0].kind == "NUMBER" else 6
        sides = max(2, min(1000, sides))
        result = random.randint(1, sides)
        print(f"  {C.CYAN}🎲 d{sides} = {result}{C.RESET}")
        bar = "█" * int(result / sides * 20) + "░" * (20 - int(result / sides * 20))
        print(f"  {C.DIM}{bar}{C.RESET}")

    def cmd_timer(self, tokens):
        text = " ".join(str(self._resolve(t)) for t in tokens)
        parts = text.split()
        if not parts:
            if self._timer_running:
                elapsed = time.time() - self._timer_start
                print(f"  {C.CYAN}⏱ {elapsed:.1f}s elapsed{C.RESET}")
            else: info("timer <seconds> | timer stop | timer start")
            return
        if parts[0] == "stop":
            if self._timer_running:
                elapsed = time.time() - self._timer_start
                self._timer_running = False
                print(f"  {C.YELLOW}⏱ Stopped at {elapsed:.1f}s{C.RESET}")
            else: info("No timer running")
            return
        if parts[0] == "start":
            self._timer_start = time.time()
            self._timer_running = True
            print(f"  {C.GREEN}⏱ Timer started{C.RESET}")
            return
        if parts[0] == "status":
            if self._timer_running:
                elapsed = time.time() - self._timer_start
                print(f"  {C.CYAN}⏱ {elapsed:.1f}s{C.RESET}")
            else: info("No timer running")
            return
        try:
            seconds = float(parts[0])
            print(f"  {C.CYAN}⏱ Countdown: {seconds}s{C.RESET}")
            for remaining in range(int(seconds), 0, -1):
                bar = "█" * int(remaining / seconds * 20) + "░" * (20 - int(remaining / seconds * 20))
                sys.stdout.write(f"\r  {C.GREEN}{bar}{C.RESET} {C.DIM}{remaining}s{C.RESET}  ")
                sys.stdout.flush()
                time.sleep(1)
            print(f"\r  {C.GREEN}{'█'*20}{C.RESET} {C.GREEN}Done! ⏰{C.RESET}  ")
        except ValueError:
            error("timer: provide seconds, 'start', 'stop', or 'status'")

    def cmd_todo(self, tokens):
        todos = []
        if self._todo_file.exists():
            try: todos = json.loads(self._todo_file.read_text())
            except: todos = []
        text = " ".join(str(self._resolve(t)) for t in tokens)
        parts = text.split(maxsplit=1)
        if not parts or parts[0] == "list":
            if not todos: info("No todos. Use: todo add <task>")
            else:
                print(f"  {C.CYAN}📋 Todos:{C.RESET}")
                for i, t in enumerate(todos, 1):
                    done = t.get("done", False)
                    icon = f"{C.GREEN}✓{C.RESET}" if done else f"{C.DIM}○{C.RESET}"
                    print(f"  {icon} {i}. {t['text']}  {C.DIM}[{t.get('time','')}]{C.RESET}")
        elif parts[0] == "add" and len(parts) > 1:
            todo = {"text": parts[1], "done": False, "time": datetime.now().strftime("%H:%M")}
            todos.append(todo)
            self._todo_file.write_text(json.dumps(todos, indent=2))
            ok(f"Todo added: {parts[1]}")
        elif parts[0] == "done" and len(parts) > 1:
            try:
                idx = int(parts[1]) - 1
                if 0 <= idx < len(todos):
                    todos[idx]["done"] = True
                    self._todo_file.write_text(json.dumps(todos, indent=2))
                    ok(f"Done: {todos[idx]['text']}")
                else: error(f"No todo #{parts[1]}")
            except ValueError: error("todo done <number>")
        elif parts[0] == "clear":
            todos = []
            self._todo_file.write_text("[]")
            ok("Todos cleared")
        elif parts[0] == "remove" and len(parts) > 1:
            try:
                idx = int(parts[1]) - 1
                if 0 <= idx < len(todos):
                    removed = todos.pop(idx)
                    self._todo_file.write_text(json.dumps(todos, indent=2))
                    ok(f"Removed: {removed['text']}")
                else: error(f"No todo #{parts[1]}")
            except ValueError: error("todo remove <number>")
        else: info("todo add <task> | list | done <n> | remove <n> | clear")

    def cmd_ping(self, tokens):
        host = " ".join(str(self._resolve(t)) for t in tokens)
        if not host: error("ping: provide a host"); return
        try:
            r = subprocess.run(["ping", "-c", "4", "-W", "3", host],
                             capture_output=True, text=True, timeout=15)
            for line in r.stdout.splitlines():
                if "time=" in line or "ttl=" in line or "statistics" in line or "rtt" in line:
                    print(f"  {C.CYAN}{line}{C.RESET}")
                elif "PING" in line:
                    print(f"  {C.DIM}{line}{C.RESET}")
            if r.returncode != 0:
                error(f"Ping failed: {host}")
        except subprocess.TimeoutExpired:
            error("Ping timed out")
        except FileNotFoundError:
            error("ping command not available")
        except Exception as e:
            error(f"Ping: {e}")

    def cmd_curl(self, tokens):
        url = " ".join(str(self._resolve(t)) for t in tokens)
        if not url: error("curl: provide a URL"); return
        if not url.startswith("http"): url = "https://" + url
        try:
            import requests
            r = requests.get(url, timeout=15, headers={"User-Agent": "CCL-Curl/1.0"})
            print(f"  {C.DIM}HTTP {r.status_code} ({len(r.content)} bytes){C.RESET}")
            ct = r.headers.get("content-type", "")
            if "json" in ct:
                try: print(f"  {C.CYAN}{json.dumps(r.json(), indent=2)[:2000]}{C.RESET}")
                except: print(f"  {r.text[:2000]}")
            elif "text" in ct or "html" in ct:
                text = r.text[:1500]
                print(f"  {C.GREEN}{text}{C.RESET}")
            else:
                print(f"  {C.YELLOW}Content-Type: {ct}{C.RESET}")
                print(f"  {C.DIM}(binary, {len(r.content)} bytes){C.RESET}")
        except Exception as e:
            error(f"curl: {e}")

    def cmd_search(self, tokens):
        query = " ".join(str(self._resolve(t)) for t in tokens)
        if not query: error("search: provide a query"); return
        url = f"https://google.com/search?q={query.replace(' ', '+')}"
        print(f"  {C.CYAN}🔍 Search: {query}{C.RESET}")
        print(f"  {C.GREEN}→ {url}{C.RESET}")
        print(f"  {C.DIM}Open in browser: open \"{url}\"{C.RESET}")

    def cmd_whois(self, tokens):
        domain = " ".join(str(self._resolve(t)) for t in tokens)
        if not domain: error("whois: provide a domain"); return
        try:
            r = subprocess.run(["whois", domain], capture_output=True, text=True, timeout=15)
            lines = r.stdout.splitlines()
            important = []
            for kw in ["Domain Name", "Registrar", "Creation Date", "Expir", "Name Server", "Status", "DNSSEC", "Registrant", "Admin", "Tech"]:
                for l in lines:
                    if kw.lower() in l.lower() and l.strip():
                        important.append(l.strip())
            if important:
                for l in important[:20]:
                    print(f"  {C.CYAN}{l}{C.RESET}")
            else:
                for l in lines[:15]:
                    print(f"  {C.DIM}{l}{C.RESET}")
        except FileNotFoundError:
            try:
                import requests
                r = requests.get(f"https://whois.freeaiapi.com/?domain={domain}", timeout=10)
                if r.ok:
                    data = r.json()
                    for k, v in data.items():
                        print(f"  {C.CYAN}{k}:{C.RESET} {v}")
                else: error("whois service unavailable")
            except: error("whois: install whois package or check connectivity")
        except subprocess.TimeoutExpired: error("whois timed out")
        except Exception as e: error(f"whois: {e}")

    def cmd_dns(self, tokens):
        host = " ".join(str(self._resolve(t)) for t in tokens)
        if not host: error("dns: provide a hostname"); return
        try:
            import socket
            ip = socket.gethostbyname(host)
            print(f"  {C.CYAN}A record:{C.RESET} {host} → {ip}")
            try:
                hostname, aliases, _ = socket.gethostbyaddr(ip)
                print(f"  {C.GREEN}PTR:{C.RESET} {ip} → {hostname}")
            except: pass
        except Exception as e:
            error(f"dns: {e}")
        try:
            r = subprocess.run(["nslookup", host], capture_output=True, text=True, timeout=10)
            lines = r.stdout.splitlines()
            for l in lines:
                if "name = " in l.lower() or "canonical name" in l.lower() or "mail" in l.lower():
                    print(f"  {C.DIM}{l.strip()}{C.RESET}")
        except: pass

    def cmd_theme(self, tokens):
        name = tokens[0].value if tokens else ""
        if not name or name == "list":
            print(f"\n  {C.CYAN}Available themes:{C.RESET}")
            themes = ["cyber", "sunset", "matrix", "dragonskin", "ocean", "midnight"]
            current = ""
            try:
                if Path.home().exists():
                    tf = Path.home() / ".ccl_theme"
                    if tf.exists(): current = tf.read_text().strip()
            except: pass
            for t in themes:
                mark = f"{C.GREEN}◉ active{C.RESET}" if t == current else ""
                print(f"  {C.CYAN}⬡ {t:<15}{C.RESET} {mark}")
            print(f"\n  {C.DIM}Usage: theme <name>{C.RESET}")
            return
        valid = ["cyber", "sunset", "matrix", "dragonskin", "ocean", "midnight"]
        if name in valid:
            try:
                tf = Path.home() / ".ccl_theme"
                tf.write_text(name)
                print(f"  {C.GREEN}✓ Theme set to '{name}'{C.RESET}")
                print(f"  {C.DIM}Restart terminal or run 'clear' to apply{C.RESET}")
            except Exception as e: error(f"Cannot save theme: {e}")
        else:
            error(f"Theme '{name}' not found. Try: theme list")

    def cmd_neofetch(self, tokens):
        try:
            import psutil, platform
            cpu = platform.processor() or "Unknown CPU"
            cores = psutil.cpu_count()
            mem = psutil.virtual_memory()
            kernel = platform.uname().release
            shell = "CCL OMNIA"
            hostname = os.uname().nodename
            user = os.environ.get("USER", "user")
            logo = f"""
  {C.CYAN}       ██████╗ ██████╗ ██╗
  {C.CYAN}      ██╔════╝██╔═══██╗██║
  {C.CYAN}      ██║     ██║   ██║██║
  {C.CYAN}      ██║     ██║   ██║██║
  {C.CYAN}      ╚██████╗╚██████╔╝███████╗
  {C.CYAN}       ╚═════╝ ╚═════╝ ╚══════╝{C.RESET}"""
            print(logo)
            print(f"  {C.DIM}────────────────────────{C.RESET}")
            print(f"  {C.CYAN}OS:{C.RESET}       {platform.system()} {platform.release()}")
            print(f"  {C.GREEN}Host:{C.RESET}     {user}@{hostname}")
            print(f"  {C.YELLOW}Kernel:{C.RESET}   {kernel}")
            print(f"  {C.MAGENTA}Shell:{C.RESET}    {shell}")
            print(f"  {C.CYAN}CPU:{C.RESET}      {cpu} ({cores} cores)")
            print(f"  {C.GREEN}RAM:{C.RESET}      {mem.used/1024**3:.1f}GB / {mem.total/1024**3:.1f}GB")
            print(f"  {C.YELLOW}Python:{C.RESET}   {sys.version.split()[0]}")
            print(f"  {C.DIM}────────────────────────{C.RESET}\n")
        except ImportError:
            error("neofetch requires psutil")

    def cmd_cowsay(self, tokens):
        text = " ".join(str(self._resolve(t)) for t in tokens)
        if not text: error("cowsay: provide text"); return
        lines = textwrap.wrap(text, 40) if len(text) > 40 else [text]
        max_w = max(len(l) for l in lines)
        top = " " + "_" * (max_w + 2)
        bottom = " " + "-" * (max_w + 2)
        print(f"\n  {top}")
        if len(lines) == 1:
            print(f"  < {lines[0]:<{max_w}} >")
        else:
            print(f"  / {lines[0]:<{max_w}} \\")
            for l in lines[1:-1]:
                print(f"  | {l:<{max_w}} |")
            print(f"  \\ {lines[-1]:<{max_w}} /")
        print(f"  {bottom}")
        print(f"        \\   ^__^")
        print(f"         \\  (oo)\\_______")
        print(f"            (__)\\       )\\/\\")
        print(f"                ||----w |")
        print(f"                ||     ||\n")

    def cmd_figlet(self, tokens):
        text = " ".join(str(self._resolve(t)) for t in tokens)
        if not text: error("figlet: provide text"); return
        try:
            r = subprocess.run(["figlet", text], capture_output=True, text=True, timeout=5)
            if r.returncode == 0:
                for line in r.stdout.splitlines():
                    print(f"  {C.CYAN}{line}{C.RESET}")
            else: self._fallback_banner(text)
        except FileNotFoundError:
            self._fallback_banner(text)

    def _fallback_banner(self, text):
        for ch in text.upper():
            lines = ["█" * 8 for _ in range(6)]
            for i, l in enumerate(lines):
                if i == 0: print(f"  {C.CYAN}{l}{C.RESET}", end="  ")
                else: print(f"  {l}{C.RESET}", end="  ")
            print()

    def cmd_help(self, _):
        sections = [
            ("AI & CODE", ""),
            ("ask \"question\"","AI answers dev questions"),
            ("generate \"app idea\"","AI generates code files"),
            ("fix <file>","AI debugs and fixes code"),
            ("explain <file>","AI explains code"),
            ("agent \"task\"","AI plans multi-step tasks"),
            ("chat \"message\"","Continuous AI chat mode"),
            ("setkey <provider> <key>","Set API key (gemini, openai, etc.)"),
            ("ai","Show AI provider status"),
            ("", ""),
            ("UTILITIES", ""),
            ("calc <expression>","Calculator (e.g. calc 2+2*3)"),
            ("weather [city]","Weather forecast"),
            ("sysinfo","System info (CPU, RAM, disk)"),
            ("neofetch","Colorful system info display"),
            ("passwd [length]","Generate secure password"),
            ("uuid","Generate UUID"),
            ("hash <text>","MD5 / SHA1 / SHA256 hash"),
            ("base64 encode|decode <t>","Base64 encode/decode"),
            ("json <text>","Format/validate JSON"),
            ("banner <text>","ASCII banner art"),
            ("colors","Show ANSI color palette"),
            ("echo <text>","Print text"),
            ("", ""),
            ("NETWORK", ""),
            ("ip","Show IP addresses"),
            ("ping <host>","Ping a host"),
            ("curl <url>","Fetch a URL"),
            ("dns <host>","DNS lookup"),
            ("whois <domain>","Domain WHOIS lookup"),
            ("search \"query\"","Web search URL"),
            ("", ""),
            ("FUN", ""),
            ("fortune","Random wisdom quote"),
            ("matrix","Matrix rain effect"),
            ("cowsay <text>","Cow says your text"),
            ("figlet <text>","Large ASCII text"),
            ("flip","Coin flip"),
            ("roll [sides]","Dice roll"),
            ("random [min] [max]","Random number"),
            ("timer <sec>|start|stop","Countdown / stopwatch"),
            ("todo add|list|done|clear","Task manager"),
            ("", ""),
            ("PROJECT & GIT", ""),
            ("create file|folder|project","Create files/folders/projects"),
            ("build app|api|contract","Scaffold projects"),
            ("install <pkg>","Install pip/npm packages"),
            ("save [\"msg\"]","Git add + commit + push"),
            ("status","Git status"),
            ("log [n]","Git log"),
            ("deploy <target>","Deploy to surge/vercel/github"),
            ("", ""),
            ("SYSTEM", ""),
            ("theme <name>","Change theme: cyber, sunset, matrix..."),
            ("date","Show date and time"),
            ("cal","Show calendar"),
            ("uptime","System uptime"),
            ("run <file>","Execute .ccl or .py file"),
            ("open <file|url>","Open in default app"),
            ("delete <file>","Delete file/folder"),
            ("note <text>","Save a quick note"),
            ("show wallet|vars|notes|config","Display info"),
            ("list files|folders|projects","List filesystem"),
            ("version","Show CCL version"),
            ("clear / exit","Clear screen / quit"),
        ]
        print(f"\n  {C.MAGENTA}{C.BOLD}╔══ CCL OMNIA — CapeChain Labs ═══════════════════════╗{C.RESET}")
        for cmd, desc in sections:
            if desc == "": 
                if cmd: print(f"  {C.DIM}── {cmd} {'─'*(48-len(cmd))}{C.RESET}")
            else:
                print(f"  {C.CYAN}{cmd:<42}{C.RESET} {C.DIM}{desc}{C.RESET}")
        print(f"  {C.MAGENTA}╚══════════════════════════════════════════════════════════╝{C.RESET}\n")

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
        raw_args = line[len(cmd):].strip()
        dispatch={
            "generate":ex.cmd_generate,"fix":ex.cmd_fix,"explain":ex.cmd_explain,
            "agent":ex.cmd_agent,"setkey":ex.cmd_setkey,"aistatus":ex.cmd_aistatus,"install":ex.cmd_install,
            "save":ex.cmd_save,"status":ex.cmd_status,"log":ex.cmd_log,
            "deploy":ex.cmd_deploy,"share":ex.cmd_share,"receive":ex.cmd_receive,
            "sync":ex.cmd_sync,"use":ex.cmd_use,"note":ex.cmd_note,"open":ex.cmd_open,
            "version":ex.cmd_version,"create":ex.cmd_create,"build":ex.cmd_build,
            "ask":ex.cmd_ask,"ai":ex.cmd_ai,"chat":ex.cmd_chat,"make":ex.cmd_make,"show":ex.cmd_show,"print":ex.cmd_print,
            "set":ex.cmd_set,"list":ex.cmd_list,"run":ex.cmd_run,"delete":ex.cmd_delete,
            "help":ex.cmd_help,
            "calc":lambda t: ex.cmd_calc(t, raw_args),"weather":ex.cmd_weather,"sysinfo":ex.cmd_sysinfo,
            "passwd":ex.cmd_passwd,"uuid":ex.cmd_uuid,"hash":ex.cmd_hash,
            "base64":ex.cmd_base64,"json":ex.cmd_json,"banner":ex.cmd_banner,
            "matrix":ex.cmd_matrix,"fortune":ex.cmd_fortune,"colors":ex.cmd_colors,
            "ip":ex.cmd_ip,"date":ex.cmd_date,"cal":ex.cmd_cal,"uptime":ex.cmd_uptime,
            "echo":ex.cmd_echo,"random":ex.cmd_random,"flip":ex.cmd_flip,"roll":ex.cmd_roll,
            "timer":ex.cmd_timer,"todo":ex.cmd_todo,"ping":ex.cmd_ping,"curl":ex.cmd_curl,
            "search":ex.cmd_search,"whois":ex.cmd_whois,"dns":ex.cmd_dns,
            "theme":ex.cmd_theme,"neofetch":ex.cmd_neofetch,"cowsay":ex.cmd_cowsay,"figlet":ex.cmd_figlet,
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
