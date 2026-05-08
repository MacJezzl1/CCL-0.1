// CCL OS - Main JavaScript
// Handles mode switching, command execution, AI Council, and UI interactions

document.addEventListener('DOMContentLoaded', () => {
    // Initialize
    initModes();
    initCommandBar();
    initCouncilRoom();
    initTerminal();
    updateAICount();
});

// ===== Mode Switching =====
function initModes() {
    const modeButtons = document.querySelectorAll('.mode-btn');
    const panels = document.querySelectorAll('.mode-panel');

    modeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const mode = btn.dataset.mode;

            // Update active button
            modeButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Show corresponding panel
            panels.forEach(p => p.classList.remove('active'));
            const targetPanel = document.getElementById(`${mode}-mode`);
            if (targetPanel) {
                targetPanel.classList.add('active');
            }
        });
    });
}

// ===== Command Bar =====
function initCommandBar() {
    const commandInput = document.getElementById('commandInput');
    const commandBtn = document.getElementById('commandBtn');
    const commandOutput = document.getElementById('commandOutput');
    const outputContent = document.getElementById('outputContent');
    const closeOutput = document.getElementById('closeOutput');

    const executeCommand = () => {
        const command = commandInput.value.trim();
        if (!command) return;

        // Show output panel
        commandOutput.classList.add('active');

        // Process command
        const response = processCommand(command);
        outputContent.innerHTML = `<pre>${response}</pre>`;

        // Clear input
        commandInput.value = '';
    };

    commandBtn.addEventListener('click', executeCommand);
    commandInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') executeCommand();
    });

    closeOutput.addEventListener('click', () => {
        commandOutput.classList.remove('active');
    });
}

// ===== Command Processing =====
function processCommand(command) {
    const cmd = command.toLowerCase();

    // Create commands
    if (cmd.startsWith('create ')) {
        const task = command.substring(7);
        return `🌟 Dream-to-App Engine Activated

Task: ${task}

📋 Planning phase:
  - Analyzing requirements...
  - Selecting architecture...
  - Choosing tech stack...

🤖 AI Council is working on: ${task}

Status: Building... (This is a simulation. In production, this would build your app.)

Tip: Try "create a crypto wallet app" or "create a meme coin launcher"`;
    }

    // Fix commands
    if (cmd.startsWith('fix ')) {
        return `🔧 Codebase Doctor Activated

Scanning project for issues...
  ✓ Syntax errors: None found
  ⚠️  Performance: 2 suggestions
  ✓ Security: No critical issues

Recommendations:
  1. Add error handling to API calls
  2. Optimize database queries

Status: Ready to fix (Simulation mode)`;
    }

    // Deploy commands
    if (cmd.startsWith('deploy ')) {
        return `🚀 One-Click Deploy Activated

Preparing deployment...
  ✓ Building project...
  ✓ Running tests...
  ✓ Optimizing assets...

Deployment targets:
  1. Local machine
  2. VPS (Oracle Cloud)
  3. Docker container
  4. Static hosting

Status: Ready to deploy (Simulation mode)

Tip: Configure deployment in Settings > Deploy`;
    }

    // Explain commands
    if (cmd.startsWith('explain ')) {
        return `📚 Teacher AI Activated

${command.substring(8)}

Explanation:
This is a simplified explanation for learning purposes.
In production, AI would analyze your code and provide
step-by-step explanations.

Status: Ready to teach (Simulation mode)`;
    }

    // Tokenize commands
    if (cmd.startsWith('tokenize ')) {
        return `🪙 Token Creator Activated (Coming Soon)

Token: ${command.substring(10)}

In production, this will:
  ✓ Generate smart contract
  ✓ Create tokenomics
  ✓ Deploy to GenX
  ✓ Create landing page
  ✓ Generate whitepaper

Status: Coming Soon to GenX Mode`;
    }

    // Audit commands
    if (cmd.startsWith('audit ')) {
        return `🔒 Crypto Audit AI Activated (Coming Soon)

Scanning smart contract...
  ✓ Reentrancy: Safe
  ✓ Overflow: Safe
  ✓ Access control: Good

Status: Coming Soon to GenX Mode`;
    }

    // Help
    if (cmd === 'help') {
        return `CCL OS - Available Commands

CREATE - Build something new:
  create <description>
  Example: "create a crypto wallet with React"

FIX - Debug and repair:
  fix <issue or file>
  Example: "fix the login bug"

DEPLOY - Launch your project:
  deploy <target>
  Example: "deploy to VPS"

EXPLAIN - Learn and understand:
  explain <concept or code>
  Example: "explain how blockchain works"

TOKENIZE - Create tokens (Coming Soon):
  tokenize <token name>
  Example: "tokenize MyCoin"

AUDIT - Security check (Coming Soon):
  audit <contract or project>
  Example: "audit my smart contract"

DESIGN - UI/UX creation:
  design <description>

AUTOMATE - Workflow automation:
  automate <task>

Type a command above and press Enter or click Execute.`;
    }

    return `Command not recognized: ${command}

Type "help" for available commands.

Examples:
  - create a DeFi dashboard
  - fix the authentication bug
  - deploy to cloud
  - explain React hooks`;
}

// ===== AI Council Room =====
function initCouncilRoom() {
    const councilBtn = document.getElementById('councilBtn');
    const councilModal = document.getElementById('councilModal');
    const closeCouncil = document.getElementById('closeCouncil');
    const councilGrid = document.getElementById('councilGrid');

    const aiMembers = [
        { name: 'Architect AI', icon: '🏗️', role: 'Planning' },
        { name: 'Coder AI', icon: '💻', role: 'Coding' },
        { name: 'Debugger AI', icon: '🐛', role: 'Debugging' },
        { name: 'Security AI', icon: '🔒', role: 'Security' },
        { name: 'UI/UX AI', icon: '🎨', role: 'Design' },
        { name: 'Blockchain AI', icon: '⛓️', role: 'Web3' },
        { name: 'Database AI', icon: '🗄️', role: 'Storage' },
        { name: 'DevOps AI', icon: '🚀', role: 'Deployment' },
    ];

    // Populate council grid
    councilGrid.innerHTML = aiMembers.map(member => `
        <div class="council-member" data-ai="${member.name}">
            <div class="member-icon">${member.icon}</div>
            <div class="member-name">${member.name}</div>
            <div class="member-status">Ready</div>
        </div>
    `).join('');

    councilBtn.addEventListener('click', () => {
        councilModal.classList.add('active');
        simulateCouncilDiscussion();
    });

    closeCouncil.addEventListener('click', () => {
        councilModal.classList.remove('active');
    });

    // Close on outside click
    councilModal.addEventListener('click', (e) => {
        if (e.target === councilModal) {
            councilModal.classList.remove('active');
        }
    });
}

function simulateCouncilDiscussion() {
    const members = document.querySelectorAll('.council-member');
    const output = document.getElementById('councilOutput');

    members.forEach((member, index) => {
        setTimeout(() => {
            member.classList.add('thinking');
            const status = member.querySelector('.member-status');
            status.textContent = 'Thinking...';

            setTimeout(() => {
                member.classList.remove('thinking');
                status.textContent = 'Done ✓';
            }, 2000 + Math.random() * 2000);
        }, index * 500);
    });

    setTimeout(() => {
        output.querySelector('.consensus-box').innerHTML = `
            <h3>Final Consensus</h3>
            <p><strong>✓ Architecture:</strong> MERN Stack (MongoDB, Express, React, Node.js)</p>
            <p><strong>✓ Security:</strong> Input validation, JWT auth, rate limiting</p>
            <p><strong>✓ Performance:</strong> Code splitting, lazy loading, caching</p>
            <p><strong>✓ Deployment:</strong> Docker + Oracle Cloud VPS</p>
            <p style="margin-top: 15px; color: var(--neon-teal);">
                <strong>All AIs agree - Ready to build!</strong>
            </p>
        `;
    }, members.length * 500 + 3000);
}

// ===== Terminal Emulator =====
function initTerminal() {
    const terminalInput = document.getElementById('terminalInput');
    const terminalOutput = document.getElementById('terminalOutput');

    if (!terminalInput) return;

    terminalInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const command = terminalInput.value.trim();
            if (!command) return;

            // Add command line
            addTerminalLine(`$ ${command}`, 'command');

            // Process command
            const output = processTerminalCommand(command);
            if (output) {
                addTerminalLine(output, 'output');
            }

            terminalInput.value = '';
            terminalOutput.scrollTop = terminalOutput.scrollHeight;
        }
    });
}

function addTerminalLine(text, type) {
    const terminalOutput = document.getElementById('terminalOutput');
    const line = document.createElement('p');
    line.className = `terminal-line ${type}`;
    line.textContent = text;
    terminalOutput.appendChild(line);
}

function processTerminalCommand(cmd) {
    const command = cmd.toLowerCase();

    if (command === 'help') {
        return `CCL Terminal Commands:

  help          - Show this help
  clear         - Clear terminal
  ls            - List files
  pwd           - Show current directory
  echo <text>   - Print text
  date          - Show current date
  whoami        - Show current user
  ccl status    - Show CCL OS status
  ccl ai        - List AI providers
  ccl connect   - Connect to GenX node

Type a command and press Enter.`;
    }

    if (command === 'clear') {
        const terminalOutput = document.getElementById('terminalOutput');
        terminalOutput.innerHTML = '';
        return null;
    }

    if (command === 'ls') {
        return 'README.md  src/  package.json  node_modules/  docs/';
    }

    if (command === 'pwd') {
        return '/home/user/CCL_0.1';
    }

    if (command === 'date') {
        return new Date().toString();
    }

    if (command === 'whoami') {
        return 'user@ccl-os';
    }

    if (command === 'ccl status') {
        return `CCL OS Status:

  Version: 0.2.0
  Mode: GenX Mode
  AIs Connected: 18
  Node Status: Online
  Block Height: 1,247,892
  Memory Usage: 2.3 GB / 24 GB
  CPU Usage: 12%`;
    }

    if (command === 'ccl ai') {
        return `AI Providers:

  ✓ Ollama (Local) - 5 models
  ✓ LM Studio (Local) - 1 model
  ✗ OpenAI - Not configured
  ✗ Anthropic Claude - Not configured
  ✗ Google Gemini - Not configured
  ✗ Groq - Not configured

Configure API keys in Settings > AI Providers`;
    }

    if (command.startsWith('echo ')) {
        return cmd.substring(5);
    }

    return `Command not found: ${cmd}. Type 'help' for available commands.`;
}

// ===== Update AI Count =====
function updateAICount() {
    const aiStatus = document.getElementById('aiStatus');
    if (aiStatus) {
        const enabledCount = 18; // Simulate 18 AIs (local + cloud)
        aiStatus.textContent = `● ${enabledCount} AIs Connected`;
    }
}

// ===== Export for use in other modules =====
window.CCLOS = {
    processCommand,
    processTerminalCommand,
    updateAICount,
};
