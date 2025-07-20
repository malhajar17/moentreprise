# 🚀 Moentreprise Quick Start Guide

Welcome to Moentreprise! This guide will get you up and running with your AI business automation platform in just a few minutes.

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.8 or higher
- [ ] Node.js 16+ and npm
- [ ] Git installed
- [ ] OpenAI API key with Realtime API access
- [ ] LinkedIn Developer account (optional, for marketing features)
- [ ] FFmpeg installed
- [ ] A modern web browser (Chrome, Firefox, Safari, Edge)

## 🛠️ Step-by-Step Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/moentreprise.git
cd moentreprise
```

### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 3: Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

### Step 4: Configure Environment Variables

```bash
# Copy the example environment file
cp env.example .env

# Edit .env with your favorite editor
nano .env  # or vim, code, etc.
```

Add your credentials:
```env
# Required
OPENAI_API_KEY=sk-...your-openai-api-key...

# Optional (for LinkedIn marketing)
LINKEDIN_ACCESS_TOKEN=...
LINKEDIN_AUTHOR_ID=...
LINKEDIN_ORG_ID=lelefleurfrance_hackathon
```

### Step 5: Clear Any Blocked Ports

```bash
python clear_ports.py
```

This ensures ports 3000, 3001, and 5173 are available.

### Step 6: Launch Moentreprise

```bash
cd examples
python web_demo.py
```

You should see:
```
🚀 MOENTREPRISE - AI BUSINESS AUTOMATION PLATFORM
🤖 Intelligent team collaboration with real-time execution
📱 Access: http://localhost:3001
🎯 Experience: Complete business automation from idea to launch
💼 Features: Requirements gathering → Development → Marketing automation
```

### Step 7: Open Your Browser

Navigate to: `http://localhost:3001`

## 🎮 Using Moentreprise

### Starting Your First Project

1. **Click "Launch AI Business Team"**
   - Marcus (Project Manager) will greet you
   - The team will be ready to help

2. **The Interview Process**
   - Sarah will ask 6 questions about your project
   - Answer naturally - she understands context
   - Example answers:
     - Target audience: "Flower lovers in Paris"
     - Pages needed: "Home, catalog, about, contact"
     - Color palette: "Purple and white, elegant"

3. **Watch the Magic Happen**
   - Maya researches competitor websites
   - Alex builds your website in real-time
   - Sophie creates LinkedIn marketing campaign
   - Marcus manages the entire process

### Voice Interaction

When it's your turn to speak:

1. The microphone button appears
2. **Hold the button** while speaking
3. Release when done
4. Your audio is processed in real-time

### Monitoring Progress

- **Conversation Panel**: See all interactions
- **Terminal Output**: Watch live development
- **Website Preview**: Automatic popup when ready
- **Status Indicators**: Know who's speaking

## 🔧 Configuration Options

### Customizing the Team

Edit `examples/web_demo.py` to modify team behavior:

```python
# Skip interview phase for testing
if True:  # Change to False for full interview
    orchestrator.interview_notes = [
        "Target audience: flower lovers in Paris.",
        "Pages needed: Home, Catalogue, About, Contact.",
        # ... preset answers
    ]
    orchestrator.phase = "ideation_prep"
```

### Adjusting Timing

For faster/slower transitions:
```python
orchestrator.turn_delay_seconds = 0.5  # Default is 0.5
```

## 🚨 Troubleshooting

### Common Issues & Solutions

**1. "Port already in use" error**
```bash
python clear_ports.py
# Then restart the application
```

**2. No audio playing**
- Check browser console (F12)
- Ensure microphone permissions granted
- Verify FFmpeg is installed: `ffmpeg -version`

**3. LinkedIn posting fails**
- Check your LinkedIn tokens are valid
- Ensure you have company page admin access
- Verify the organization ID matches

**4. Website doesn't appear**
- Check terminal output for errors
- Ensure Node.js is installed: `node --version`
- Try manually opening: `http://localhost:3000`

**5. OpenAI API errors**
- Verify your API key has Realtime API access
- Check your OpenAI account has credits
- Ensure you're using the correct model

### Debug Mode

For detailed logging:

1. Edit `examples/web_demo.py`
2. Add at the top:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Performance Tips

1. **Use a stable internet connection** - Real-time audio requires consistent bandwidth
2. **Close unnecessary browser tabs** - Reduces client-side processing
3. **Use Chrome or Firefox** - Best WebSocket support
4. **Keep responses concise** - Shorter answers = faster processing

## 🎯 Next Steps

Now that you're up and running:

1. **Experiment with different business ideas**
2. **Try the voice interaction features**
3. **Watch the full development pipeline**
4. **Check out the generated LinkedIn posts**
5. **Explore customization options**

## 💡 Pro Tips

- **Quick Reset**: Press "Clear Workspace" between projects
- **Skip Steps**: Modify `orchestrator.phase` to jump to specific phases
- **Save Output**: Terminal output is logged for debugging
- **Multiple Sessions**: Each browser tab is independent

## 🆘 Getting Help

- **Documentation**: Check `/docs` folder
- **Issues**: GitHub Issues page
- **Community**: Join our Discord
- **Email**: support@legml.ai

---

Congratulations! You're now ready to automate business projects with Moentreprise! 🎉

Remember: Each session demonstrates the full power of AI collaboration - from idea to deployed website with marketing in minutes! 