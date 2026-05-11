# Contributing to CCL OMNIA

First off, thanks for taking the time to contribute! 🎉

## Code of Conduct

Be respectful, inclusive, and constructive. We're building something awesome together.

## How to Contribute

### 1. Fork & Clone
```bash
git clone https://github.com/your-username/CCL-0.1.git
cd CCL-0.1
git remote add upstream https://github.com/MacJezzl1/CCL-0.1.git
```

### 2. Create a Branch
```bash
git checkout -b feature/your-amazing-idea
```

### 3. Make Changes
- Follow existing code style (no comments, concise Python)
- Test your changes with `python3 core/ccl_terminal.py`
- Update README if adding new commands

### 4. Commit
```bash
git add .
git commit -m "feat: add your awesome feature"
```

### 5. Push & PR
```bash
git push origin feature/your-amazing-idea
# Open a Pull Request on GitHub
```

## Development Tips

- **New commands**: Add the method to `CCLExecutor` in `core/ccl_interpreter.py`, then register it in the `dispatch` dict in `execute_line()`
- **New themes**: Add to the `THEMES` dict in `core/ccl_terminal.py`
- **New providers**: Add to `PROVIDERS` dict in `core/ccl_ai.py`
- **Dashboard features**: Add API routes in `ccl_dashboard_server.py` and windows in `ccl_dashboard_ui.html`

## What Needs Help

- More AI providers
- More practical utility commands
- Better Web3 wallet integration
- Mobile-responsive dashboard
- Unit tests
- Documentation improvements
- Bug fixes

## Questions?

Open an issue or reach out on GitHub. Let's build the future of developer tools! 🚀
