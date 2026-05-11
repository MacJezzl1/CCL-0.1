#!/usr/bin/env python3
"""
CCL AI Module v0.3 — OMNIA
CapeChain Labs — 50+ AI Providers · Smart Router · Auto Failover
"""

import json, os, sys, urllib.request, urllib.error, time, subprocess
from pathlib import Path

class C:
    RESET="\033[0m"; BOLD="\033[1m"; ITALIC="\033[3m"
    CYAN="\033[96m"; GREEN="\033[92m"; YELLOW="\033[93m"
    RED="\033[91m"; MAGENTA="\033[95m"; DIM="\033[2m"
    WHITE="\033[97m"; BLUE="\033[94m"; ORANGE="\033[38;5;214m"

def ok(m):    print(f"{C.GREEN}  ✓ {m}{C.RESET}")
def info(m):  print(f"{C.CYAN}  → {m}{C.RESET}")
def warn(m):  print(f"{C.YELLOW}  ⚠ {m}{C.RESET}")
def err(m):   print(f"{C.RED}  ✗ {m}{C.RESET}")
def ai(m):    print(f"{C.MAGENTA}  ◈ {m}{C.RESET}")

OLLAMA_URL = "http://localhost:11434"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

PROVIDERS = {
    "ollama":       {"name": "Ollama",        "type": "local",  "endpoint": "ollama",   "models": ["llama3.2", "llama3", "mistral", "phi3", "codellama", "gemma"]},
    "openai-gpt4o": {"name": "OpenAI GPT-4o", "type": "paid",   "endpoint": "openai",   "model": "gpt-4o", "key": "openai_api_key"},
    "openai-gpt4":  {"name": "OpenAI GPT-4",  "type": "paid",   "endpoint": "openai",   "model": "gpt-4-turbo", "key": "openai_api_key"},
    "openai-gpt35": {"name": "OpenAI GPT-3.5","type": "paid",   "endpoint": "openai",   "model": "gpt-3.5-turbo", "key": "openai_api_key"},
    "openai-o1":    {"name": "OpenAI o1",     "type": "paid",   "endpoint": "openai",   "model": "o1-preview", "key": "openai_api_key"},
    "openai-o3":    {"name": "OpenAI o3-mini","type": "paid",   "endpoint": "openai",   "model": "o3-mini", "key": "openai_api_key"},
    "claude-sonnet":{"name": "Claude Sonnet", "type": "paid",   "endpoint": "claude",   "model": "claude-sonnet-4-20250514", "key": "anthropic_api_key"},
    "claude-opus":  {"name": "Claude Opus",   "type": "paid",   "endpoint": "claude",   "model": "claude-opus-4-20250514", "key": "anthropic_api_key"},
    "claude-haiku": {"name": "Claude Haiku",  "type": "paid",   "endpoint": "claude",   "model": "claude-3-haiku-20240307", "key": "anthropic_api_key"},
    "gemini-flash": {"name": "Gemini 2.0 Flash","type":"free",  "endpoint": "gemini",   "model": "gemini-2.0-flash", "key": "gemini_api_key"},
    "gemini-pro":   {"name": "Gemini 2.0 Pro", "type": "free",  "endpoint": "gemini",   "model": "gemini-2.0-pro", "key": "gemini_api_key"},
    "gemini15-pro": {"name": "Gemini 1.5 Pro","type": "free",   "endpoint": "gemini",   "model": "gemini-1.5-pro", "key": "gemini_api_key"},
    "deepseek":     {"name": "DeepSeek V3",   "type": "paid",   "endpoint": "openai",   "model": "deepseek-chat", "base_url": "https://api.deepseek.com", "key": "deepseek_api_key"},
    "deepseek-r1":  {"name": "DeepSeek R1",   "type": "paid",   "endpoint": "openai",   "model": "deepseek-reasoner", "base_url": "https://api.deepseek.com", "key": "deepseek_api_key"},
    "mistral-large":{"name": "Mistral Large", "type": "paid",   "endpoint": "openai",   "model": "mistral-large-latest", "base_url": "https://api.mistral.ai/v1", "key": "mistral_api_key"},
    "mistral-small":{"name": "Mistral Small", "type": "paid",   "endpoint": "openai",   "model": "mistral-small-latest", "base_url": "https://api.mistral.ai/v1", "key": "mistral_api_key"},
    "codestral":    {"name": "Codestral",     "type": "paid",   "endpoint": "openai",   "model": "codestral-latest", "base_url": "https://api.mistral.ai/v1", "key": "mistral_api_key"},
    "groq-llama":   {"name": "Groq Llama 3",  "type": "free",   "endpoint": "openai",   "model": "llama3-70b-8192", "base_url": "https://api.groq.com/openai/v1", "key": "groq_api_key"},
    "groq-mixtral": {"name": "Groq Mixtral",  "type": "free",   "endpoint": "openai",   "model": "mixtral-8x7b-32768", "base_url": "https://api.groq.com/openai/v1", "key": "groq_api_key"},
    "groq-gemma":   {"name": "Groq Gemma 2",  "type": "free",   "endpoint": "openai",   "model": "gemma2-9b-it", "base_url": "https://api.groq.com/openai/v1", "key": "groq_api_key"},
    "groq-deepseek":{"name": "Groq DeepSeek", "type": "free",   "endpoint": "openai",   "model": "deepseek-r1-distill-llama-70b", "base_url": "https://api.groq.com/openai/v1", "key": "groq_api_key"},
    "together-llama":{"name":"Together Llama","type": "paid",   "endpoint": "openai",   "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo", "base_url": "https://api.together.xyz/v1", "key": "together_api_key"},
    "together-mistral":{"name":"Together Mistral","type":"paid","endpoint":"openai",    "model":"mistralai/Mixtral-8x22B-Instruct-v0.1","base_url":"https://api.together.xyz/v1","key":"together_api_key"},
    "fireworks-llama":{"name":"Fireworks Llama","type":"paid",  "endpoint":"openai",    "model":"accounts/fireworks/models/llama-v3p3-70b-instruct","base_url":"https://api.fireworks.ai/inference/v1","key":"fireworks_api_key"},
    "perplexity":   {"name": "Perplexity Sonar","type":"paid",  "endpoint":"openai",    "model":"sonar-pro","base_url":"https://api.perplexity.ai","key":"perplexity_api_key"},
    "perplexity-sonar":{"name":"Perplexity Sonar Deep","type":"paid","endpoint":"openai","model":"sonar-deep-research","base_url":"https://api.perplexity.ai","key":"perplexity_api_key"},
    "xai-grok":     {"name": "xAI Grok 2",    "type": "paid",   "endpoint": "openai",   "model": "grok-2-1212", "base_url": "https://api.x.ai/v1", "key": "xai_api_key"},
    "xai-grok-mini":{"name": "xAI Grok Mini", "type": "paid",   "endpoint": "openai",   "model": "grok-2-mini", "base_url": "https://api.x.ai/v1", "key": "xai_api_key"},
    "cohere-command":{"name":"Cohere Command R+","type":"paid", "endpoint":"cohere",    "model":"command-r-plus","key":"cohere_api_key"},
    "cohere-command-r":{"name":"Cohere Command R","type":"paid","endpoint":"cohere",    "model":"command-r","key":"cohere_api_key"},
    "ai21-jamba":   {"name": "AI21 Jamba 1.5","type": "paid",   "endpoint": "openai",   "model": "jamba-1.5-large", "base_url": "https://api.ai21.com/studio/v1", "key": "ai21_api_key"},
    "replicate-llama":{"name":"Replicate Llama","type":"paid",  "endpoint":"openai",    "model":"meta/meta-llama-3-70b-instruct","base_url":"https://api.replicate.com/v1","key":"replicate_api_key"},
    "huggingface":  {"name": "HuggingFace",   "type": "free",   "endpoint": "openai",   "model": "mistralai/Mistral-7B-Instruct-v0.3", "base_url": "https://api-inference.huggingface.co/v1", "key": "huggingface_api_key"},
    "deepinfra-llama":{"name":"DeepInfra Llama","type":"paid",  "endpoint":"openai",    "model":"meta-llama/Meta-Llama-3.1-70B-Instruct","base_url":"https://api.deepinfra.com/v1/openai","key":"deepinfra_api_key"},
    "deepinfra-mixtral":{"name":"DeepInfra Mixtral","type":"paid","endpoint":"openai",  "model":"mistralai/Mixtral-8x22B-Instruct-v0.1","base_url":"https://api.deepinfra.com/v1/openai","key":"deepinfra_api_key"},
    "anyscale":     {"name": "Anyscale",      "type": "paid",   "endpoint": "openai",   "model": "meta-llama/Llama-3.2-70B-Instruct", "base_url": "https://api.endpoints.anyscale.com/v1", "key": "anyscale_api_key"},
    "octoai":       {"name": "OctoAI",        "type": "paid",   "endpoint": "openai",   "model": "meta-llama-3.1-70b-instruct", "base_url": "https://text.octoai.run/v1", "key": "octoai_api_key"},
    "novita":       {"name": "Novita AI",     "type": "paid",   "endpoint": "openai",   "model": "meta-llama/llama-3.1-70b-instruct", "base_url": "https://api.novita.ai/v3/openai", "key": "novita_api_key"},
    "lepton":       {"name": "Lepton AI",     "type": "paid",   "endpoint": "openai",   "model": "llama3-70b", "base_url": "https://api.lepton.ai/v1", "key": "lepton_api_key"},
    "portkey":      {"name": "Portkey",       "type": "paid",   "endpoint": "openai",   "model": "gpt-4o", "base_url": "https://api.portkey.ai/v1", "key": "portkey_api_key"},
    "openrouter":   {"name": "OpenRouter",    "type": "paid",   "endpoint": "openrouter","model": "openai/gpt-4o", "key": "openrouter_api_key"},
    "openrouter-claude": {"name":"OpenRouter Claude","type":"paid","endpoint":"openrouter","model":"anthropic/claude-3.5-sonnet","key":"openrouter_api_key"},
    "openrouter-deepseek":{"name":"OpenRouter DeepSeek","type":"paid","endpoint":"openrouter","model":"deepseek/deepseek-chat","key":"openrouter_api_key"},
    "openrouter-gemini":{"name":"OpenRouter Gemini","type":"paid","endpoint":"openrouter","model":"google/gemini-2.0-flash-exp","key":"openrouter_api_key"},
    "openrouter-qwen":{"name":"OpenRouter Qwen","type":"paid",  "endpoint":"openrouter","model":"qwen/qwen-2.5-72b-instruct","key":"openrouter_api_key"},
    "openrouter-llama":{"name":"OpenRouter Llama","type":"paid","endpoint":"openrouter","model":"meta-llama/llama-3.3-70b-instruct","key":"openrouter_api_key"},
    "localai":      {"name": "LocalAI",       "type": "local",  "endpoint": "openai",   "model": "gpt-4", "base_url": "http://localhost:8080/v1"},
    "vllm":         {"name": "vLLM",          "type": "local",  "endpoint": "openai",   "model": "default", "base_url": "http://localhost:8000/v1"},
    "llamacpp":     {"name": "llama.cpp",     "type": "local",  "endpoint": "openai",   "model": "default", "base_url": "http://localhost:8080/v1"},
    "gpt4all":      {"name": "GPT4All",       "type": "local",  "endpoint": "openai",   "model": "default", "base_url": "http://localhost:4891/v1"},
    "textgen":      {"name": "Oobabooga",     "type": "local",  "endpoint": "openai",   "model": "default", "base_url": "http://localhost:5000/v1"},
    "kobold":       {"name": "KoboldCPP",     "type": "local",  "endpoint": "openai",   "model": "default", "base_url": "http://localhost:5001/v1"},
    "azure-openai": {"name": "Azure OpenAI",  "type": "paid",   "endpoint": "openai",   "model": "gpt-4o", "base_url": "https://YOUR_RESOURCE.openai.azure.com/v1", "key": "azure_api_key"},
}

TIER_ORDER = ["local", "free", "freemium", "paid"]

def get_cfg():
    p = Path(__file__).parent.parent / "config" / "ccl_config.json"
    return json.loads(p.read_text()) if p.exists() else {}

def save_cfg(c):
    p = Path(__file__).parent.parent / "config" / "ccl_config.json"
    p.write_text(json.dumps(c, indent=2))

def get_key(name):
    env_map = {
        "openai_api_key": "OPENAI_API_KEY", "anthropic_api_key": "ANTHROPIC_API_KEY",
        "gemini_api_key": "GEMINI_API_KEY", "deepseek_api_key": "DEEPSEEK_API_KEY",
        "mistral_api_key": "MISTRAL_API_KEY", "groq_api_key": "GROQ_API_KEY",
        "together_api_key": "TOGETHER_API_KEY", "fireworks_api_key": "FIREWORKS_API_KEY",
        "perplexity_api_key": "PERPLEXITY_API_KEY", "xai_api_key": "XAI_API_KEY",
        "cohere_api_key": "COHERE_API_KEY", "ai21_api_key": "AI21_API_KEY",
        "replicate_api_key": "REPLICATE_API_KEY", "huggingface_api_key": "HF_API_KEY",
        "deepinfra_api_key": "DEEPINFRA_API_KEY", "anyscale_api_key": "ANYSCALE_API_KEY",
        "octoai_api_key": "OCTOAI_API_KEY", "novita_api_key": "NOVITA_API_KEY",
        "lepton_api_key": "LEPTON_API_KEY", "portkey_api_key": "PORTKEY_API_KEY",
        "openrouter_api_key": "OPENROUTER_API_KEY", "azure_api_key": "AZURE_API_KEY",
    }
    env = env_map.get(name)
    if env and os.environ.get(env): return os.environ[env]
    c = get_cfg()
    v = c.get(name, "")
    return v if v and v != "YOUR_KEY_HERE" else None

def ollama_running():
    try: urllib.request.urlopen(OLLAMA_URL, timeout=2); return True
    except: return False

def ollama_models():
    try:
        r = urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=4)
        return [m["name"] for m in json.loads(r.read()).get("models", [])]
    except: return []

def best_ollama():
    models = ollama_models()
    if not models: return None
    for p in ["llama3.2", "llama3", "phi3", "mistral", "codellama", "gemma", "qwen2", "deepseek"]:
        for m in models:
            if p in m.lower(): return m
    return models[0]

def ollama_chat(prompt, system="", model=None):
    model = model or best_ollama()
    if not model: return None
    msgs = []
    if system: msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    req = urllib.request.Request(f"{OLLAMA_URL}/api/chat",
        data=json.dumps({"model": model, "messages": msgs, "stream": False,
                         "options": {"temperature": 0.3, "num_predict": 2048}}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read()).get("message", {}).get("content", "").strip()
    except: return None

def openai_chat(prompt, system="", model="gpt-4o", base_url="https://api.openai.com/v1", api_key=None, max_tokens=3000):
    if not api_key: return None
    msgs = []
    if system: msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    url = f"{base_url.rstrip('/')}/chat/completions"
    req = urllib.request.Request(url,
        data=json.dumps({"model": model, "messages": msgs, "max_tokens": max_tokens, "temperature": 0.3}).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        if e.code in (429, 401, 403, 404): return None
        body = e.read().decode()
        return None
    except: return None

def claude_chat(prompt, system="", model="claude-sonnet-4-20250514", api_key=None, max_tokens=3000):
    if not api_key: return None
    payload = json.dumps({"model": model, "max_tokens": max_tokens, "system": system,
                          "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=payload,
        headers={"Content-Type": "application/json", "x-api-key": api_key, "anthropic-version": "2023-06-01"},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())["content"][0]["text"].strip()
    except: return None

def gemini_chat(prompt, system="", model="gemini-2.0-flash", api_key=None, max_tokens=3000):
    if not api_key: return None
    contents = []
    if system: contents.append({"role": "user", "parts": [{"text": f"[System: {system}]"}]})
    contents.append({"role": "user", "parts": [{"text": prompt}]})
    payload = json.dumps({"contents": contents,
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": max_tokens}}).encode()
    gemini_model = model.replace("gemini-", "").replace(".", "-")
    base = model if "/" in model else f"models/{model}"
    url = f"https://generativelanguage.googleapis.com/v1beta/{base}:generateContent?key={api_key}"
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.loads(r.read())
            return d.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
    except: return None

def openrouter_chat(prompt, system="", model="openai/gpt-4o", api_key=None, max_tokens=3000):
    if not api_key: return None
    msgs = []
    if system: msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    req = urllib.request.Request(OPENROUTER_URL,
        data=json.dumps({"model": model, "messages": msgs, "max_tokens": max_tokens, "temperature": 0.3}).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}",
                 "HTTP-Referer": "https://ccl.capechainlabs.io", "X-Title": "CCL OS"},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"].strip()
    except: return None

def parse_json(t):
    if not t: return None
    if t.startswith("```"):
        lines = t.splitlines()
        t = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    for i, ch in enumerate(t):
        if ch in "{[":
            try: return json.loads(t[i:])
            except: break
    try: return json.loads(t)
    except: return None

def resolve_provider(provider_id):
    if provider_id in PROVIDERS:
        return PROVIDERS[provider_id]
    return None

def chat_with_provider(provider_id, prompt, system="", max_tokens=3000):
    p = resolve_provider(provider_id)
    if not p: return None
    endpoint = p.get("endpoint")
    model = p.get("model", "default")
    key_name = p.get("key")
    base_url = p.get("base_url", "")
    api_key = get_key(key_name) if key_name else None

    if endpoint == "ollama":
        return ollama_chat(prompt, system, model if model != "default" else None)
    elif endpoint == "claude":
        return claude_chat(prompt, system, model, api_key, max_tokens)
    elif endpoint == "gemini":
        return gemini_chat(prompt, system, model, api_key, max_tokens)
    elif endpoint == "openrouter":
        return openrouter_chat(prompt, system, model, api_key, max_tokens)
    elif endpoint == "openai":
        url = base_url or "https://api.openai.com/v1"
        return openai_chat(prompt, system, model, url, api_key, max_tokens)
    return None

def get_available_providers():
    available = []
    for pid, p in PROVIDERS.items():
        ptype = p.get("type", "paid")
        key_name = p.get("key")
        has_key = bool(get_key(key_name)) if key_name else (
            (p.get("endpoint") == "ollama" and ollama_running() and best_ollama())
        )
        if has_key or ptype in ("local", "free"):
            if ptype == "local":
                if p.get("endpoint") == "ollama" and (ollama_running() and best_ollama()):
                    available.append((pid, p))
            else:
                available.append((pid, p))
    return available

def smart_ask(prompt, system="", want_json=False, max_tokens=3000):
    providers = get_available_providers()
    tier_order = {"local": 0, "free": 1, "freemium": 2, "paid": 3}
    providers.sort(key=lambda x: tier_order.get(x[1].get("type", "paid"), 99))

    for pid, p in providers:
        pname = p.get("name", pid)
        ai(f"{pname} …")
        raw = chat_with_provider(pid, prompt, system, max_tokens)
        if raw:
            if want_json:
                result = parse_json(raw)
                if result: return result
                ai(f"{pname} retry (JSON)…")
                raw2 = chat_with_provider(pid, prompt,
                    system + "\n\nIMPORTANT: Respond with ONLY valid JSON.", max_tokens)
                if raw2:
                    r2 = parse_json(raw2)
                    if r2: return r2
            else:
                return raw
        warn(f"{pname} unavailable, trying next…")
    return None

SYS_GENERATE = """You are CCL-AI, the code generator inside CapeChain Labs OS.
Generate complete, working code files from a description.
Respond ONLY with valid JSON:
{
  "files": [{"name": "filename.ext", "content": "full file content"}],
  "summary": "what was built",
  "run_cmd": "command to run it",
  "dependencies": ["flask"]
}"""

SYS_AGENT = """You are CCL-Agent inside CapeChain Labs OS.
Break a task into clear steps. Respond ONLY with valid JSON:
{
  "task": "original task",
  "plan": ["Step 1: ..."],
  "ccl_commands": ["create project \\"name\\""],
  "estimated_time": "~2 minutes",
  "summary": "What will be created"
}"""

SYS_FIX = """You are CCL-Fix, code debugger. Return ONLY JSON:
{"fixed_code": "...", "explanation": "...", "changes": [...]}"""

SYS_EXPLAIN = """You are CCL-Explain. Return ONLY JSON:
{"summary": "...", "breakdown": [...], "concepts": [...], "suggestions": [...]}"""

SYS_ASK = "You are CCL-AI developer assistant. Answer concisely with code examples."

def generate(description, output_dir="generated", api_key=None):
    print(f"\n{C.MAGENTA}  ◈ Generating: \"{description}\"{C.RESET}")
    result = smart_ask(description, SYS_GENERATE, want_json=True, max_tokens=4000)
    if not result or "files" not in result: err("No output."); return False
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    for f in result.get("files", []):
        fp = out / f.get("name", "out.txt")
        fp.parent.mkdir(parents=True, exist_ok=True); fp.write_text(f.get("content", ""))
        ok(f"Created: {fp.name}")
    if result.get("summary"): print(f"\n{C.CYAN}  ◈ {result['summary']}{C.RESET}")
    if result.get("dependencies"): info(f"Deps: {', '.join(result['dependencies'])}")
    if result.get("run_cmd"): print(f"{C.YELLOW}  ▶ {result['run_cmd']}{C.RESET}")
    return True

def run_agent(task, api_key=None):
    print(f"\n{C.MAGENTA}  ◈ Agent: \"{task}\"{C.RESET}")
    r = smart_ask(task, SYS_AGENT, want_json=True, max_tokens=1024)
    if not r: return None
    print(f"\n{C.CYAN}  ◈ {r.get('summary','')}{C.RESET}")
    if r.get("estimated_time"): print(f"{C.DIM}  ETA: {r['estimated_time']}{C.RESET}\n")
    for i, s in enumerate(r.get("plan", []), 1): print(f"  {C.YELLOW}{i}.{C.RESET} {s}")
    for c in r.get("ccl_commands", []): print(f"  {C.GREEN}  › {c}{C.RESET}")
    return r

def fix_code(filepath, error_msg="", api_key=None):
    p = Path(filepath)
    if not p.exists(): err(f"Not found: {filepath}"); return False
    code = p.read_text()
    prompt = f"File: {filepath}\n\nCode:\n{code}\n\nError:\n{error_msg or 'Review and improve'}"
    print(f"\n{C.MAGENTA}  ◈ Fix: {filepath}{C.RESET}")
    r = smart_ask(prompt, SYS_FIX, want_json=True, max_tokens=3000)
    if not r: return False
    fixed = r.get("fixed_code", "")
    if fixed:
        p.with_suffix(p.suffix + ".bak").write_text(code)
        p.write_text(fixed); ok(f"Fixed! Backup: {p.name}.bak")
    if r.get("explanation"): print(f"{C.CYAN}  ◈ {r['explanation']}{C.RESET}")
    for c in r.get("changes", []): print(f"{C.DIM}    • {c}{C.RESET}")
    return True

def explain_code(filepath_or_code, api_key=None):
    p = Path(filepath_or_code)
    c = p.read_text() if p.exists() else filepath_or_code
    l = filepath_or_code if p.exists() else "snippet"
    print(f"\n{C.MAGENTA}  ◈ Explain: {l}{C.RESET}")
    r = smart_ask(c, SYS_EXPLAIN, want_json=True, max_tokens=1024)
    if not r: return
    if r.get("summary"): print(f"\n{C.CYAN}  ◈ {r['summary']}{C.RESET}")
    for b in r.get("breakdown", []): print(f"  {C.DIM}• {b}{C.RESET}")
    if r.get("concepts"): print(f"\n{C.YELLOW}  Concepts: {', '.join(r['concepts'])}{C.RESET}")
    for s in r.get("suggestions", []): print(f"  {C.GREEN}↑ {s}{C.RESET}")

def ask(question, api_key=None):
    print(f"\n{C.MAGENTA}  ◈ Thinking …{C.RESET}")
    r = smart_ask(question, SYS_ASK, want_json=False, max_tokens=512)
    if r: print(f"\n{C.MAGENTA}  ◈ {r}{C.RESET}\n")
    else:
        hints = {"deploy": "deploy surge", "install": "install <pkg>",
                 "wallet": "make wallet", "git": "save \"msg\"",
                 "center": "flexbox: center", "api": "Flask route"}
        for kw, h in hints.items():
            if kw in question.lower(): ai(h); return
        ai("Get a free Gemini key at aistudio.google.com, then: setkey gemini YOUR_KEY")

def setup_key(provider, key):
    pid = provider.lower().replace("-", "_")
    if pid in PROVIDERS:
        kn = PROVIDERS[pid].get("key")
        if kn:
            c = get_cfg(); c[kn] = key; save_cfg(c)
            ok(f"{PROVIDERS[pid]['name']} key saved!")
            return
    c = get_cfg()
    key_map = {
        "openai": "openai_api_key", "claude": "anthropic_api_key", "anthropic": "anthropic_api_key",
        "gemini": "gemini_api_key", "deepseek": "deepseek_api_key", "mistral": "mistral_api_key",
        "groq": "groq_api_key", "together": "together_api_key", "fireworks": "fireworks_api_key",
        "perplexity": "perplexity_api_key", "xai": "xai_api_key", "cohere": "cohere_api_key",
        "huggingface": "huggingface_api_key", "openrouter": "openrouter_api_key",
        "replicate": "replicate_api_key",
    }
    kn = key_map.get(pid)
    if kn: c[kn] = key; save_cfg(c); ok(f"{pid.title()} key saved!")
    else: err(f"Unknown provider: {provider}. Try: openai, claude, gemini, groq, deepseek, mistral, openrouter")

def ai_status():
    av = get_available_providers()
    total = len(PROVIDERS)
    ready = sum(1 for pid, p in av if p.get("type") != "local") + sum(1 for pid, p in av if p.get("type") == "local")
    local = [p for pid, p in av if p.get("type") == "local"]
    free = [p for pid, p in av if p.get("type") == "free"]
    paid = [p for pid, p in av if p.get("type") == "paid"]

    print(f"\n{C.CYAN}{C.BOLD}  ╔══ CCL OMNIA — AI PROVIDER HUB ═══════════════════╗{C.RESET}")
    print(f"  ║{C.RESET}")
    print(f"  ║  {C.CYAN}Available: {len(av)}/{total} providers{C.RESET}")
    print(f"  ║{C.RESET}")
    if local:
        print(f"  ║  {C.GREEN}◉ LOCAL (private, free){C.RESET}")
        for p in local:
            m = best_ollama() if p.get("endpoint") == "ollama" else "running"
            print(f"  ║    {C.GREEN}⬡{C.RESET} {p['name']:30} {C.DIM}{m}{C.RESET}")
    if free:
        print(f"  ║  {C.CYAN}◉ FREE TIER{C.RESET}")
        for p in free[:8]:
            kn = "✓" if p.get("key") and get_key(p["key"]) else "no key"
            print(f"  ║    {C.CYAN}⬡{C.RESET} {p['name']:30} {C.DIM}{kn}{C.RESET}")
    if paid:
        print(f"  ║  {C.YELLOW}◉ PAID API{C.RESET}")
        for p in paid[:10]:
            kn = get_key(p["key"]) if p.get("key") else None
            icon = "🟢" if kn else "⚪"
            print(f"  ║    {icon} {p['name']:30} {C.DIM}{p.get('model','')[:30]}{C.RESET}")
    if len(paid) > 10 or len(free) > 8:
        print(f"  ║    {C.DIM}... and {len(paid)+len(free)-18} more{C.RESET}")
    print(f"  ║{C.RESET}")
    print(f"  ║  {C.YELLOW}Set keys:{C.RESET}  setkey openai|claude|gemini|groq|deepseek|mistral|openrouter <key>")
    print(f"  ║  {C.DIM}OpenRouter = 200+ models through 1 API{C.RESET}")
    print(f"  ║  {C.DIM}Gemini has a free tier: aistudio.google.com{C.RESET}")
    print(f"  ║  {C.DIM}Groq is free: console.groq.com{C.RESET}")
    print(f"  ║")
    print(f"  {C.CYAN}  ╚══════════════════════════════════════════════════════╝{C.RESET}\n")
