// Smart Contract Forge - JavaScript
// Handles contract generation, audit, and deployment (simulated)

document.addEventListener('DOMContentLoaded', () => {
    initAiAssistModal();
    initDeployButton();
    initContractTypeSelector();
});

// ===== AI Assist Modal =====
function initAiAssistModal() {
    const aiBtn = document.getElementById('aiAssistBtn');
    const modal = document.getElementById('aiAssistModal');
    const closeBtn = document.getElementById('closeAiAssist');

    aiBtn.addEventListener('click', () => {
        modal.classList.add('active');
    });

    closeBtn.addEventListener('click', () => {
        modal.classList.remove('active');
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
}

// ===== Deploy Button =====
function initDeployButton() {
    const deployBtn = document.getElementById('deployBtn');
    
    deployBtn.addEventListener('click', () => {
        alert('🚀 Deployment feature coming soon!\n\nThis will deploy your smart contract to:\n- GenX Testnet\n- GenX Mainnet\n- Ethereum\n- Polygon\n\nWith automatic verification and explorer links.');
    });
}

// ===== Contract Type Selector =====
function initContractTypeSelector() {
    const select = document.getElementById('contractType');
    const desc = document.getElementById('contractDesc');
    
    const contractDescriptions = {
        'ERC-20 Token': 'Create a standard fungible token with configurable supply, name, symbol, and decimals. Supports minting, burning, and transfer restrictions.',
        'ERC-721 NFT': 'Create a non-fungible token contract with minting, metadata URI, and enumeration support. Includes base URI configuration.',
        'ERC-1155 Multi-Token': 'Create a multi-token standard contract that supports both fungible and non-fungible tokens in a single contract.',
        'DAO Governor': 'Create a governance contract with voting power, proposal creation, voting period, and execution. Includes timelock controller.',
        'Staking Contract': 'Create a staking contract with rewards distribution, lock periods, and early withdrawal penalties.',
        'Vesting Contract': 'Create a token vesting contract with cliff periods, linear vesting, and beneficiary management.',
        'Escrow Contract': 'Create an escrow contract with dispute resolution, arbitrator role, and automatic release conditions.',
        'Marketplace': 'Create a marketplace contract for buying and selling NFTs or tokens with royalties and auction support.'
    };

    select.addEventListener('change', () => {
        const selected = select.value;
        if (contractDescriptions[selected]) {
            desc.placeholder = `AI will generate: ${contractDescriptions[selected]}\n\nDescribe any custom requirements...`;
        }
    });
}

// ===== Simulate Contract Generation =====
function generateContract() {
    const contractType = document.getElementById('contractType').value;
    const contractName = document.getElementById('contractName').value || 'MyContract';
    const description = document.getElementById('contractDesc').value;

    if (!description) {
        alert('Please describe your contract requirements.');
        return;
    }

    // Simulate AI generation
    const output = `
🤖 AI Contract Generation Started...

Contract Type: ${contractType}
Contract Name: ${contractName}

📋 Generating Solidity code...
⚙️  Configuring parameters...
🔒 Adding security features...
📄 Generating documentation...
🧪 Creating test suite...
📊 Calculating gas estimates...

✅ Contract generated successfully!

Next steps:
1. Review the generated code
2. Run AI security audit
3. Optimize gas usage
4. Deploy to testnet
5. Verify on explorer

Note: This is a simulation. Full functionality coming soon to CCL OS GenX Mode.
    `;

    alert(output);
}

// ===== Simulate Audit =====
function runAudit() {
    const auditItems = document.querySelectorAll('.audit-item');
    
    auditItems.forEach((item, index) => {
        setTimeout(() => {
            item.classList.remove('pending');
            
            // Simulate random pass/fail
            const passed = Math.random() > 0.2;
            item.classList.add(passed ? 'passed' : 'failed');
            
            const icon = item.querySelector('.audit-icon');
            icon.textContent = passed ? '✓' : '✗';
            
            const text = item.querySelector('span:last-child');
            if (!passed) {
                text.textContent += ' (Issue found)';
            }
        }, index * 1000);
    });

    setTimeout(() => {
        alert('🔒 AI Audit Complete!\n\nResults:\n✓ Reentrancy: Passed\n✓ Overflow: Passed\n⚠️  Access Control: 1 Issue Found\n✓ Gas Optimization: Passed\n✓ External Calls: Passed\n\nRecommendation: Review access control in function transfer().');
    }, auditItems.length * 1000 + 500);
}

// ===== Export for use in HTML onclick =====
window.SmartContractForge = {
    generateContract,
    runAudit,
};
