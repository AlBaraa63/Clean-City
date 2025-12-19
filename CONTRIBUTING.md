# Contributing to CleanCity Agent

Thank you for your interest in contributing to CleanCity Agent! 🌍

## 🎯 Project Vision

CleanCity Agent aims to make environmental action accessible through AI-powered trash detection and cleanup planning. We welcome contributions that align with this mission.

## 🚀 Quick Start

1. **Fork the repository**
2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/CleanCity-Agent.git
   cd CleanCity-Agent
   ```
3. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📝 Development Guidelines

### Code Style

- Follow **PEP 8** Python style guide
- Use **type hints** for function parameters and returns
- Add **docstrings** to all functions and classes
- Keep functions small and focused (single responsibility)

### Testing Your Changes

Before submitting a PR:

1. **Test the Gradio app:**
   ```bash
   python app.py
   ```
   
2. **Test the MCP server:**
   ```bash
   python mcp_server.py
   ```

3. **Verify all tabs work:**
   - Analysis tab
   - History tab
   - Impact & Examples tab
   - Chat tab

4. **Test with different LLM providers:**
   - Set `LLM_PROVIDER=offline` (default)
   - Test with real API keys if available

### Commit Messages

Use clear, descriptive commit messages:

```
✅ Good:
- "Add GPS auto-detection feature"
- "Fix model path resolution for deployed environments"
- "Improve error handling in trash detection"

❌ Bad:
- "Update stuff"
- "Fix bug"
- "WIP"
```

## 🎨 Areas for Contribution

### High Priority

- **Real YOLOv8 Model Integration** - Replace mock detector with trained model
- **Mobile Responsiveness** - Improve UI for smartphones
- **Multilingual Support** - Add i18n for global reach
- **Performance Optimization** - Faster image processing
- **Accessibility** - ARIA labels, keyboard navigation, screen reader support

### Feature Ideas

- **Gamification** - Points/badges for cleanup reporting
- **Community Features** - Team cleanup coordination
- **Advanced Analytics** - Trend analysis, predictive hotspots
- **Integration with City Services** - API for municipal waste management
- **Offline Mode Enhancement** - PWA with offline detection

### Documentation

- Additional usage examples
- Tutorial videos
- API documentation improvements
- Translation of docs to other languages

## 🐛 Reporting Bugs

Found a bug? Help us fix it!

1. **Check existing issues** to avoid duplicates
2. **Create a new issue** with:
   - Clear title describing the problem
   - Steps to reproduce
   - Expected vs. actual behavior
   - Screenshots if applicable
   - Your environment (OS, Python version, browser)

**Template:**
```markdown
## Bug Description
[What went wrong?]

## Steps to Reproduce
1. Go to...
2. Click on...
3. See error...

## Expected Behavior
[What should happen?]

## Actual Behavior
[What actually happens?]

## Environment
- OS: [e.g., Windows 11, macOS 14]
- Python: [e.g., 3.11.5]
- Browser: [e.g., Chrome 120]
```

## 💡 Feature Requests

Have an idea? We'd love to hear it!

1. **Open an issue** with the `enhancement` label
2. **Describe the feature:**
   - What problem does it solve?
   - Who would benefit?
   - How should it work?
3. **Optional:** Include mockups, diagrams, or code sketches

## 🔀 Pull Request Process

1. **Ensure your code works** (see Testing section above)
2. **Update documentation** if you changed functionality
3. **Update README.md** if you added features
4. **Create a pull request:**
   - Descriptive title
   - Summary of changes
   - Link to related issues
   - Screenshots if UI changed

### PR Checklist

- [ ] Code follows PEP 8 style
- [ ] Added type hints
- [ ] Added/updated docstrings
- [ ] Tested locally (app runs without errors)
- [ ] Updated relevant documentation
- [ ] No sensitive data (API keys, passwords) committed

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for everyone.

### Expected Behavior

- **Be respectful** and considerate in all interactions
- **Be constructive** when giving feedback
- **Be patient** with newcomers
- **Focus on the mission** - cleaner cities and environmental action

### Unacceptable Behavior

- Harassment, discrimination, or personal attacks
- Trolling or inflammatory comments
- Spam or self-promotion unrelated to the project

**Violations:** Contact project maintainers. Violators may be banned.

## 🏆 Recognition

Contributors will be:
- Listed in README acknowledgments
- Credited in release notes
- Given proper attribution in commits

## ❓ Questions?

- **GitHub Issues:** For bugs and features
- **Discussions:** For questions and ideas
- **Email:** [Contact project maintainer if email available]

---

**Thank you for helping make CleanCity Agent better! 🌱**

Your contributions help communities worldwide take action against litter and pollution.
