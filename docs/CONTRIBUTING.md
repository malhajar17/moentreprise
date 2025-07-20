# 🤝 Contributing to Moentreprise

Thank you for your interest in contributing to Moentreprise! This guide will help you get started with contributing to our AI business automation platform.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Contributions](#making-contributions)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Submitting Changes](#submitting-changes)
- [Community](#community)

## 📜 Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please read and follow our Code of Conduct:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Respect differing viewpoints and experiences
- Show empathy towards other community members

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.8 or higher
- Node.js 16+ and npm
- Git
- A GitHub account
- Basic understanding of AI/ML concepts
- Familiarity with WebSocket protocols

### Understanding the Project

1. **Read the Documentation**
   - [README.md](../README.md) - Project overview
   - [ARCHITECTURE.md](ARCHITECTURE.md) - Technical design
   - [QUICKSTART.md](QUICKSTART.md) - Setup guide

2. **Explore the Codebase**
   - Run the demo to understand user flow
   - Review the orchestrator implementations
   - Understand the persona system

3. **Check Existing Issues**
   - Look for issues labeled `good first issue`
   - Check if your idea is already being discussed
   - Comment on issues you'd like to work on

## 🛠️ Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/moentreprise.git
cd moentreprise

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/moentreprise.git
```

### 2. Create Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available
```

### 3. Configure Environment

```bash
cp env.example .env
# Edit .env with your API keys
```

### 4. Run Tests

```bash
# Run existing tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src tests/
```

## 🔨 Making Contributions

### Types of Contributions

#### 1. Bug Fixes
- Reproduce the bug
- Write a test that fails
- Fix the bug
- Ensure test passes

#### 2. New Features
- Discuss in an issue first
- Design the feature
- Implement with tests
- Update documentation

#### 3. Documentation
- Fix typos or clarify existing docs
- Add examples
- Improve API documentation
- Create tutorials

#### 4. Performance Improvements
- Profile the code
- Identify bottlenecks
- Implement optimization
- Benchmark improvements

### Development Workflow

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-number-description
   ```

2. **Make Changes**
   - Write clean, readable code
   - Follow existing patterns
   - Add comments for complex logic
   - Update tests

3. **Test Your Changes**
   ```bash
   # Run the application
   cd examples
   python web_demo.py
   
   # Test specific functionality
   # Write and run unit tests
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add new persona configuration option"
   # Use conventional commits: feat:, fix:, docs:, style:, refactor:, test:, chore:
   ```

## 📝 Coding Standards

### Python Style Guide

Follow PEP 8 with these additions:

```python
# Good: Descriptive names
async def process_audio_chunks(self, audio_data: bytes) -> List[AudioChunk]:
    """Process raw audio data into chunks for streaming.
    
    Args:
        audio_data: Raw PCM16 audio bytes
        
    Returns:
        List of AudioChunk objects ready for streaming
    """
    pass

# Good: Type hints
from typing import Optional, List, Dict, Any

def create_persona_config(
    name: str,
    voice: str = "alloy",
    temperature: float = 0.7
) -> PersonaConfig:
    pass
```

### JavaScript/Frontend Style

```javascript
// Good: Clear function names and ES6+ features
class AudioStreamPlayer {
    constructor() {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        this.chunkQueue = [];
    }
    
    async scheduleChunk(chunkData) {
        // Implementation
    }
}
```

### Commit Message Format

Use conventional commits:

```
feat: add LinkedIn image customization options
fix: resolve audio timing issue in Safari
docs: update API reference for new personas
style: format code with black
refactor: extract audio processing to separate module
test: add unit tests for orchestrator phases
chore: update dependencies
```

## 🧪 Testing Guidelines

### Unit Tests

```python
# tests/test_orchestrator.py
import pytest
from src.simple_orchestrator import SimpleOrchestrator

class TestSimpleOrchestrator:
    @pytest.fixture
    def orchestrator(self):
        # Setup
        return SimpleOrchestrator(personas=[], config={})
    
    def test_persona_selection(self, orchestrator):
        # Test implementation
        assert orchestrator.current_persona_index == 0
```

### Integration Tests

```python
# tests/test_integration.py
async def test_full_conversation_flow():
    """Test complete conversation from start to finish."""
    # Test the entire workflow
    pass
```

### Testing Checklist

- [ ] Unit tests for new functions
- [ ] Integration tests for workflows
- [ ] Edge case handling
- [ ] Error scenarios
- [ ] Performance benchmarks (if applicable)

## 📤 Submitting Changes

### 1. Update Your Branch

```bash
git fetch upstream
git rebase upstream/main
```

### 2. Push Your Changes

```bash
git push origin feature/your-feature-name
```

### 3. Create Pull Request

1. Go to GitHub and create a PR
2. Use a clear, descriptive title
3. Fill out the PR template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

### 4. Code Review Process

- Respond to feedback constructively
- Make requested changes
- Re-request review when ready
- Be patient - reviews take time

## 🏗️ Architecture Guidelines

### Adding New Personas

1. Create persona configuration:
```python
PersonaConfig(
    name="NewPersona",
    voice="sage",
    instructions="...",
    temperature=0.8,
    tools=[custom_tools]
)
```

2. If needed, create specialized module:
```python
# src/personas/new_persona.py
class NewPersonaHandler:
    def __init__(self):
        # Initialization
        
    async def handle_special_action(self):
        # Implementation
```

3. Update phase logic if necessary

### Extending Orchestrators

```python
class CustomOrchestrator(SimpleOrchestrator):
    """Extended orchestrator with custom functionality."""
    
    async def custom_phase_logic(self):
        # Implementation
```

## 🐛 Debugging Tips

### Common Issues

1. **WebSocket Connection Failures**
   - Check API keys
   - Verify network connectivity
   - Review error logs

2. **Audio Playback Issues**
   - Ensure FFmpeg is installed
   - Check browser compatibility
   - Verify audio format

3. **Persona Response Errors**
   - Check prompt formatting
   - Verify function call syntax
   - Review temperature settings

### Debugging Tools

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug prints
logger.debug(f"Current phase: {self.phase}")
logger.debug(f"Audio chunks: {len(self.audio_chunks)}")
```

## 🌟 Best Practices

### 1. Code Quality
- Write self-documenting code
- Add meaningful comments
- Keep functions focused
- Avoid deep nesting

### 2. Performance
- Use async/await properly
- Minimize blocking operations
- Profile before optimizing
- Consider memory usage

### 3. Security
- Never commit API keys
- Validate all inputs
- Handle errors gracefully
- Follow OWASP guidelines

### 4. Documentation
- Update docs with code changes
- Include examples
- Explain complex concepts
- Keep README current

## 🤝 Community

### Getting Help

- **Discord**: Join our community server
- **GitHub Discussions**: Ask questions
- **Issues**: Report bugs or request features
- **Email**: support@legml.ai

### Ways to Contribute

Beyond code:
- Answer questions in discussions
- Improve documentation
- Create tutorials or blog posts
- Share the project
- Report bugs
- Suggest features

## 📅 Release Process

1. **Version Numbering**: Semantic versioning (MAJOR.MINOR.PATCH)
2. **Release Notes**: Document all changes
3. **Testing**: Full regression testing
4. **Documentation**: Update all docs
5. **Announcement**: Notify community

## 🙏 Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes
- Project website
- Community announcements

---

Thank you for contributing to Moentreprise! Your efforts help make AI business automation accessible to everyone. 💜

Remember: Every contribution, no matter how small, is valuable and appreciated! 