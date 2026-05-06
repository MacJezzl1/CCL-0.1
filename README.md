# CCL 0.1 — CapeChain Labs OS Shell
### The AI-Native Developer Environment

```
CCL_0.1/
├── core/
│   ├── ccl_interpreter.py     # CCL language parser + executor
│   ├── ccl_terminal.py        # Interactive terminal shell
│   ├── ccl_boot.py            # Boot screen + branding
│   └── ccl_ai.py              # AI assistant bridge
├── stdlib/
│   ├── fs.ccl                 # File system commands
│   ├── web3.ccl               # Wallet + chain commands
│   └── builder.ccl            # App builder commands
├── config/
│   └── ccl_config.json        # System config + branding
├── scripts/
│   └── hello_world.ccl        # Example CCL script
└── README.md
```

## Quick Start
```bash
python core/ccl_boot.py        # Launch CCL 0.1
python core/ccl_terminal.py    # Direct terminal access
python core/ccl_interpreter.py scripts/hello_world.ccl  # Run a script
```

## CCL Language Basics
```
// Create things
create file "app.py"
create project "MyApp" with type=web

// Build things  
build app "MyApp" with frontend=react backend=node

// AI assistant
ask "how do I center a div in CSS"
ask "write me a REST API in Python"

// Web3
make wallet
show wallet
send 0.1 SOL to "recipient_address"

// Variables
set name = "CapeChain"
set version = "0.1"

// Output
print "Hello from CCL"
print name

// Control flow
if version == "0.1" then
  print "Running CCL 0.1"
end
```

---
Built by CapeChain Labs | CCL 0.1 | 2025
