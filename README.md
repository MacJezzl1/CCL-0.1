<p align="center">
  <img src="https://img.shields.io/badge/CCL-OMNIA-00f5c8?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMjAgM0wzNyAxMC41VjI5LjVMMjAgMzdMMyAyOS41VjEwLjVMMjAgM1oiIHN0cm9rZT0iIzAwZjVjOCIgc3Ryb2tlLXdpZHRoPSIyIi8+PC9zdmc+" alt="CCL"/>
  <img src="https://img.shields.io/badge/version-0.3-00bfff?style=for-the-badge" alt="Version"/>
  <img src="https://img.shields.io/badge/license-MIT-39ff87?style=for-the-badge" alt="License"/>
  <img src="https://img.shields.io/badge/AI-53%20Providers-df80ff?style=for-the-badge" alt="AI Providers"/>
</p>

<h1 align="center">⬡ CCL OMNIA</h1>
<h3 align="center">CapeChain Labs — AI-Native Terminal Operating System</h3>

<p align="center">
  <b>40+ built-in commands · 53 AI providers · 6 themes · Web dashboard · Web3 wallet · Todo · Notes · System monitor</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Flask-3.1-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask"/>
  <img src="https://img.shields.io/badge/Ollama-supported-00f5c8?style=flat-square" alt="Ollama"/>
  <img src="https://img.shields.io/badge/OpenAI-supported-412991?style=flat-square&logo=openai&logoColor=white" alt="OpenAI"/>
  <img src="https://img.shields.io/badge/Claude-supported-CC7833?style=flat-square&logo=anthropic&logoColor=white" alt="Claude"/>
  <img src="https://img.shields.io/badge/Gemini-supported-4285F4?style=flat-square&logo=googlegemini&logoColor=white" alt="Gemini"/>
</p>

---

## ✨ Features

### 🖥️ Terminal OS
- **6 Color Themes** — Cyber, Sunset, Matrix, Dragonskin, Deep Ocean, Midnight Aurora
- **Gradient ANSI Art Logo** — True-color gradient rendering on every startup
- **Live System Monitor** — CPU/RAM bars, load averages, date/time in the header
- **Boot Sequence** — Animated system checks with progress bars
- **Smart Prompt** — Git branch, wallet status, AI status, current time
- **Tab Completion** — All commands auto-complete with Tab

### 🤖 AI Engine
- **53 AI Providers** in a unified registry
- **Smart Routing** — auto-failover: local → free → paid tier
- **Local AI** — Ollama (llama3, phi3, mistral, etc.)
- **Free Tier** — Gemini, Groq, HuggingFace inference
- **Paid Tier** — OpenAI, Claude, DeepSeek, Mistral, Together, Fireworks, Perplexity, xAI Grok, Cohere, AI21, Replicate, OpenRouter (200+ models via one API), and more
- **Continuous Chat** — `chat "message"` for ongoing conversations
- **Code Generation** — `generate "build a todo app"` creates full files
- **Code Fixing** — `fix file.py` debugs with AI
- **Code Explanation** — `explain file.py` breaks down code

### 🔧 40+ Built-in Commands

| Category | Commands |
|----------|----------|
| **AI** | `ask`, `generate`, `fix`, `explain`, `agent`, `chat`, `setkey`, `ai` |
| **Utilities** | `calc`, `weather`, `sysinfo`, `neofetch`, `passwd`, `uuid`, `hash`, `base64`, `json`, `banner`, `colors`, `echo` |
| **Network** | `ip`, `ping`, `curl`, `dns`, `whois`, `search` |
| **Fun** | `fortune`, `matrix`, `cowsay`, `figlet`, `flip`, `roll`, `random`, `timer`, `todo` |
| **Project** | `create`, `build`, `install`, `deploy`, `save`, `status`, `log`, `run` |
| **System** | `theme`, `date`, `cal`, `uptime`, `note`, `open`, `delete`, `version` |
| **Web3** | `make wallet`, `show wallet` |

### 🌐 Web Dashboard
- **Desktop-like UI** — Start menu, taskbar, draggable windows
- **Terminal Window** — Full command execution with live output streaming via SSE
- **Todo Manager** — Add, complete, remove, clear tasks
- **Notes** — Save and browse notes
- **System Monitor** — CPU, RAM, disk, uptime gauges
- **File Manager** — Browse, create, read, write files
- **Project Manager** — Create and manage CCL projects
- **AI Provider Panel** — Set API keys, see provider status
- **Wallet** — Create and view CCL Web3 wallet
- **Settings** — Change theme, wallpaper, font size

---

## 🚀 Quick Start

### One-Liner Install
```bash
pip install git+https://github.com/MacJezzl1/CCL-0.1.git
```

### Manual Install
```bash
# Clone the repo
git clone https://github.com/MacJezzl1/CCL-0.1.git
cd CCL-0.1

# Install dependencies
pip install -r requirements.txt

# Run the terminal
python3 core/ccl_terminal.py
```

### Launch Dashboard
```bash
python3 ccl_dashboard_server.py
# Open http://localhost:7741
```

---

## 🎮 Commands Reference

### AI & Code
```
ask "how do I deploy a Flask app?"    AI answers dev questions
generate "build a todo app in React"  AI generates complete code files
fix app.py ["error message"]          AI debugs and fixes code
explain app.py                        AI explains code in plain English
agent "plan a SaaS startup"           AI plans multi-step tasks
chat "hello, how are you?"            Continuous AI chat mode
setkey gemini YOUR_KEY                Save API key for AI provider
setkey openrouter YOUR_KEY            200+ models through one API
ai                                    Show all 53 AI provider status
```

### Utilities
```
calc 2+2*3                            Calculator (supports +-*/^ pi sqrt sin etc.)
weather London                        Weather forecast (works without API key)
sysinfo                               CPU, RAM, disk, network info
neofetch                              Colorful system info display
passwd 32                             Generate a strong password
uuid                                  Generate random UUID
hash hello                            MD5 + SHA1 + SHA256 of text
base64 encode hello                   Base64 encode
base64 decode aGVsbG8=                Base64 decode
json '{"name":"CCL"}'                 Format and validate JSON
banner CCL                            ASCII banner art
colors                                Show full ANSI color palette
echo Hello World                      Print text
```

### Network
```
ip                                    Show all IP addresses
ping google.com                       Ping a host
curl https://api.github.com           Fetch any URL
dns google.com                        DNS A record + reverse lookup
whois google.com                      Domain WHOIS information
search "how to center a div"          Web search URL
```

### Fun
```
fortune                               Random wisdom quote
matrix                                Matrix rain animation
cowsay Hello from CCL                 Cow says your text
figlet CCL                            Large ASCII text art
flip                                  Coin flip (HEADS/TAILS)
roll 20                               Dice roll (d20)
random 1 100                          Random number
timer 10                              Countdown timer (10 seconds)
timer start / timer stop              Stopwatch
todo add "buy groceries"              Add task
todo list                             List all tasks
todo done 1                           Mark task complete
todo clear                            Clear all tasks
```

### Projects & Git
```
create file app.py                    Create a new file
create folder my_project              Create a folder
create project MyApp                  Scaffold a full CCL project
build app MyAPI                       Scaffold an API project
build contract MyToken                Scaffold a Solidity contract
install flask react                   Install pip/npm packages
save "added feature"                  Git add + commit + push
status                                Git status
log 10                                Git log (last 10 commits)
deploy surge                          Deploy to Surge.sh
run script.ccl                        Execute .ccl or .py file
```

### System
```
theme list                            List available themes
theme sunset                          Change theme (cyber, sunset, matrix, dragonskin, ocean, midnight)
date                                  Show current date and time
cal                                   Show terminal calendar
uptime                                Show system uptime
note "meeting at 3pm"                Save a quick note
show notes                            Show saved notes
show wallet                           Show CCL Web3 wallet
show vars                             Show variables
show config                           Show configuration
list files                            List files in current directory
list projects                         List CCL projects
open https://github.com              Open URL in browser
delete app.py                         Delete file or folder
version                               Show CCL version
help                                  Show this help
clear                                 Clear screen
exit                                  Exit CCL
```

---

## 🤖 AI Providers Setup

CCL supports **53 AI providers** with automatic fallback. Set keys for the ones you want to use:

### Free (No Credit Card)
```bash
setkey gemini YOUR_API_KEY        # Google AI Studio — generous free tier
setkey groq YOUR_API_KEY          # Groq — free fast inference
```

### Paid
```bash
setkey openai sk-proj-...         # OpenAI GPT-4o, GPT-3.5
setkey claude sk-ant-...          # Claude Sonnet, Opus, Haiku
setkey deepseek YOUR_KEY          # DeepSeek V3, R1
setkey mistral YOUR_KEY           # Mistral Large, Small, Codestral
setkey openrouter YOUR_KEY        # 200+ models (GPT-4, Claude, Gemini, Llama)
setkey together YOUR_KEY          # Together AI
setkey fireworks YOUR_KEY         # Fireworks AI
setkey perplexity YOUR_KEY        # Perplexity Sonar
setkey xai YOUR_KEY               # xAI Grok
setkey cohere YOUR_KEY            # Cohere Command R+
```

### AI Routing Priority
1. **Local** — Ollama (runs on your machine, free, private)
2. **Free** — Gemini, Groq (no credit card needed)
3. **Paid** — OpenAI, Claude, etc. (API key required)

```bash
ask "explain quantum computing"     # Will try Ollama → Gemini → Groq → paid
```

---

## 🎨 Themes

| Theme | Preview |
|-------|---------|
| `cyber` | Neon cyan/magenta/blue on dark blue |
| `sunset` | Warm red/orange/gold on dark brown |
| `matrix` | Green-on-black Matrix aesthetic |
| `dragonskin` | Pink/purple/cyan on dark violet |
| `ocean` | Cool cyan/teal tones on dark blue |
| `midnight` | Green/blue/purple aurora on dark navy |

```bash
theme sunset        # Change theme
theme list          # List all themes
```

---

## 🌐 Web Dashboard

The web dashboard provides a full desktop experience in your browser:

```bash
python3 ccl_dashboard_server.py
# Open http://localhost:7741
```

**Features:**
- Welcome splash screen with animated loader
- Desktop icons for all apps
- Start menu for quick access
- Taskbar with running window indicators
- Draggable, resizable windows
- Real-time terminal output via SSE
- Todo manager with persistent storage
- Notes system
- Live system monitoring
- File browser and editor
- Project scaffolder
- AI provider key manager
- Wallet creator
- Theme and settings panel

---

## 📦 Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.8+ |
| Terminal | Pure Python (no curses/urwid) |
| Web Server | Flask 3.1 |
| Web UI | Vanilla JS + CSS3 (no frameworks) |
| AI Router | Custom provider registry with failover |
| Local AI | Ollama |
| SVG Particles | CSS3 animations |
| Window Manager | Custom JS drag system |
| SSE | Server-Sent Events for live terminal |

---

## 📁 Project Structure

```
CCL-0.1/
├── core/
│   ├── ccl_terminal.py        # Terminal with themes, gradients, animations
│   ├── ccl_interpreter.py     # Parser + executor (40+ commands)
│   ├── ccl_ai.py              # AI provider registry (53 providers) + smart router
│   ├── ccl_tools.py           # Git, deploy, package tools
│   └── ccl_templates.py       # Project templates
├── config/
│   └── ccl_config.json        # System configuration
├── ccl_dashboard_server.py    # Flask backend (SSE, APIs)
├── ccl_dashboard_ui.html      # Desktop-like web UI
├── requirements.txt           # Python dependencies
├── setup.py                   # pip install support
├── LICENSE                    # MIT License
└── README.md                  # This file
```

---

## 🛠️ Development

### Setup for Development
```bash
git clone https://github.com/MacJezzl1/CCL-0.1.git
cd CCL-0.1
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running Tests
```bash
python3 -c "
import sys; sys.path.insert(0, 'core')
from ccl_interpreter import CCLInterpreter
tests = ['calc 2+2', 'uuid', 'passwd', 'flip', 'roll', 'echo test', 'version', 'help']
i = CCLInterpreter({'version':'0.3'})
for t in tests:
    print(f'Testing: {t}')
    i.execute_line(t, i.executor)
print('All tests passed!')
"
```

---

## 📝 License

MIT License — see [LICENSE](LICENSE)

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

---

<p align="center">
  <sub>Built with ❤️ by <a href="https://github.com/MacJezzl1">MacJezzl</a> · CapeChain Labs</sub>
  <br>
  <sub>⬡ CCL OMNIA v0.3 — The AI-Native Terminal OS</sub>
</p>
