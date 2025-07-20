# 📁 Moentreprise Project Structure

This document provides a comprehensive overview of the Moentreprise codebase organization.

## 🗂️ Directory Overview

```
moentreprise/
├── src/                        # Core library code
│   ├── simple_orchestrator.py  # Base orchestration engine
│   ├── phased_orchestrator.py  # Business workflow logic
│   ├── openai_config.py        # OpenAI API configuration
│   ├── web_tools.py            # Website generation utilities
│   └── personas/               # AI persona modules
│       └── linkedin_marketer.py # Sophie's LinkedIn integration
│
├── examples/                   # Example implementations
│   └── web_demo.py            # Main Moentreprise application
│
├── resources/                  # Static assets
│   └── Mo.png                 # Mo logo image
│
├── docs/                      # Documentation
│   ├── QUICKSTART.md         # Getting started guide
│   ├── ARCHITECTURE.md       # Technical architecture
│   └── PROJECT_STRUCTURE.md  # This file
│
├── scripts/                   # Utility scripts
│   └── [various scripts]     # Helper utilities
│
├── static/                    # Web static files
│   └── [generated]           # Auto-generated content
│
├── venv/                     # Python virtual environment
│   └── [python packages]     # Installed dependencies
│
├── .git/                     # Git repository data
├── .gitignore               # Git ignore rules
├── LICENSE                  # MIT license
├── README.md               # Main documentation
├── README_LINKEDIN.md      # LinkedIn setup guide
├── requirements.txt        # Python dependencies
├── env.example            # Environment template
└── clear_ports.py         # Port cleanup utility
```

## 📄 Core Files Explained

### `/src/simple_orchestrator.py`

The foundation of the orchestration system:

```python
class SimpleOrchestrator:
    """Base orchestrator for managing AI personas"""
    
    def __init__(self, personas, openai_config):
        # Initialize WebSocket connections
        # Set up audio chunk management
        # Configure persona list
    
    async def _get_persona_response(self, persona, prompt):
        # Connect to OpenAI Realtime API
        # Stream audio chunks
        # Process function calls
    
    async def _move_to_next_persona(self):
        # Handle speaker transitions
        # Manage conversation flow
```

**Key Features:**
- WebSocket management for OpenAI API
- Audio chunk tracking and timing
- Function call processing
- Event-driven architecture

### `/src/phased_orchestrator.py`

Implements business workflow on top of SimpleOrchestrator:

```python
class PhasedOrchestrator(SimpleOrchestrator):
    """Business automation workflow manager"""
    
    phases = [
        "greeting",      # Initial welcome
        "interview",     # Requirements gathering
        "ideation_prep", # Transition phase
        "ideation",      # Development & research
        "showcase",      # Website presentation
        "marketing",     # LinkedIn campaign
        "closing"        # Project wrap-up
    ]
```

**Key Features:**
- Phase-based workflow management
- Persona routing by phase
- Interview Q&A handling
- Project lifecycle control

### `/src/web_tools.py`

Website generation and development utilities:

```python
def vibe_code(idea, terminal_callback=None):
    """Execute OpenManus pipeline for website generation"""
    # Run development commands
    # Stream terminal output
    # Handle build process
```

**Key Features:**
- OpenManus integration
- Real-time terminal streaming
- Development server management
- Error handling and recovery

### `/src/personas/linkedin_marketer.py`

Sophie's LinkedIn marketing capabilities:

```python
class LinkedInMarketer:
    """LinkedIn API integration for marketing"""
    
    def create_linkedin_post(self, content):
        # Generate DALL-E image
        # Upload media to LinkedIn
        # Create and publish post
```

**Key Features:**
- OAuth2 authentication
- Image generation with DALL-E
- Media upload handling
- Company page posting

### `/examples/web_demo.py`

Main application entry point:

```python
# Flask + SocketIO server setup
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Route definitions
@app.route('/')
@app.route('/mo-logo')
@socketio.on('start_orchestrator')
@socketio.on('human_audio')
```

**Key Features:**
- Web server configuration
- Real-time event handling
- Audio streaming management
- UI serving and routing

## 🔧 Configuration Files

### `/env.example`

Template for environment variables:

```env
OPENAI_API_KEY=your-api-key-here
OPENAI_REALTIME_MODEL=gpt-4o-realtime-preview
LINKEDIN_ACCESS_TOKEN=your-token
LINKEDIN_AUTHOR_ID=your-author-id
LINKEDIN_ORG_ID=your-org-id
```

### `/requirements.txt`

Python package dependencies:

```txt
openai[realtime]>=1.0.0
flask>=2.0.0
flask-socketio>=5.0.0
python-socketio>=5.0.0
requests>=2.25.0
python-dotenv>=0.19.0
pydub>=0.25.0
```

## 🛠️ Utility Scripts

### `/clear_ports.py`

Cleans up blocked ports:

```python
def kill_process_on_port(port):
    """Find and terminate process using specified port"""
    # Platform-specific port cleanup
    # Handles Windows/Linux/macOS
```

**Usage:**
```bash
python clear_ports.py
```

## 📚 Documentation Structure

### `/docs/QUICKSTART.md`
- Installation steps
- First-time setup
- Basic usage guide
- Troubleshooting tips

### `/docs/ARCHITECTURE.md`
- System design overview
- Component interactions
- Data flow diagrams
- Design decisions

### `/docs/PROJECT_STRUCTURE.md`
- This file
- Directory organization
- File purposes
- Code organization

## 🎨 Frontend Assets

### `/resources/Mo.png`
- Mo brand logo
- Used in web interface
- Purple character design

### Generated Static Files
- `/static/` - Auto-generated by development pipeline
- Website builds stored here
- Served by development server

## 🔄 Development Workflow

### 1. Local Development
```bash
cd examples
python web_demo.py
```

### 2. Adding Features
1. Modify core files in `/src/`
2. Update personas if needed
3. Test with web interface
4. Document changes

### 3. Testing Personas
- Edit persona configs in `web_demo.py`
- Adjust instructions and parameters
- Test conversation flows

## 🏗️ Code Organization Principles

### Separation of Concerns
- **Core Logic**: `/src/` - Reusable components
- **Applications**: `/examples/` - Specific implementations
- **Assets**: `/resources/` - Static files
- **Documentation**: `/docs/` - User guides

### Modularity
- Each persona is independent
- Orchestrators are extensible
- Tools are pluggable
- UI is decoupled

### Scalability
- Async/await throughout
- Event-driven architecture
- Stateless request handling
- Resource cleanup

## 🚀 Extension Points

### Adding New Personas
1. Create persona config in `web_demo.py`
2. Optionally add specialized module in `/src/personas/`
3. Update phase logic if needed
4. Test integration

### Custom Tools
1. Define function schema
2. Implement handler
3. Add to persona tools
4. Handle in orchestrator

### UI Customization
1. Modify HTML/CSS in `web_demo.py`
2. Update color schemes
3. Add new UI elements
4. Enhance interactions

## 📦 Deployment Preparation

### Required Files
- All `/src/` modules
- `/examples/web_demo.py`
- `/resources/` assets
- `requirements.txt`
- `.env` configuration

### Optional Files
- `/docs/` for reference
- `clear_ports.py` for debugging
- `README.md` for documentation

### Excluded Files
- `/venv/` - Recreate on deployment
- `/static/` - Generated at runtime
- `.git/` - Version control data
- `*.pyc` - Compiled Python files

---

This structure enables Moentreprise to maintain clean separation between core functionality, business logic, and presentation while remaining flexible for future enhancements. 