# 🏗️ Moentreprise Architecture

This document provides a comprehensive overview of Moentreprise's technical architecture, component interactions, and design decisions.

## 📐 System Overview

Moentreprise is built on a multi-layered architecture that orchestrates AI personas, manages real-time communication, and automates business workflows.

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Browser Client                       │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   UI/UX     │  │ Audio Player │  │ WebSocket Client │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Flask + SocketIO Server                   │
│  ┌──────────────┐  ┌─────────────┐  ┌─────────────────┐   │
│  │ HTTP Routes  │  │ WS Handlers │  │ Audio Processor │   │
│  └──────────────┘  └─────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Phased Orchestrator                        │
│  ┌──────────────┐  ┌─────────────┐  ┌─────────────────┐   │
│  │ Phase Logic  │  │ Turn Manager │  │ Persona Router  │   │
│  └──────────────┘  └─────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Simple Orchestrator                        │
│  ┌──────────────┐  ┌─────────────┐  ┌─────────────────┐   │
│  │ WS Manager   │  │ Audio Chunks │  │ Function Calls  │   │
│  └──────────────┘  └─────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  OpenAI Realtime API                         │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Core Components

### 1. Web Interface (`examples/web_demo.py`)

The frontend provides a professional business interface with:

- **Real-time Audio Streaming**: WebAudio API for chunk-based playback
- **WebSocket Communication**: SocketIO for bidirectional messaging
- **Voice Input**: MediaRecorder API for human interaction
- **Visual Feedback**: Dynamic UI updates showing conversation state

#### Key Frontend Classes:

```javascript
class AudioStreamPlayer {
    // Manages audio chunk scheduling and playback
    // Ensures seamless audio transitions
    // Handles timing calculations
}
```

### 2. Flask Server Layer

Handles HTTP requests and WebSocket connections:

- **Routes**:
  - `/` - Serves the main interface
  - `/mo-logo` - Serves Mo branding asset
  - `/start_orchestrator` - Initializes AI team
  - `/stop_orchestrator` - Ends session
  - `/human_audio` - Processes voice input

- **SocketIO Events**:
  - Manages real-time communication
  - Streams audio chunks to client
  - Broadcasts status updates

### 3. Phased Orchestrator (`src/phased_orchestrator.py`)

Implements business workflow logic:

```python
class PhasedOrchestrator(SimpleOrchestrator):
    phases = [
        "greeting",      # Marcus welcomes client
        "interview",     # Sarah gathers requirements
        "ideation_prep", # Prepare for development
        "ideation",      # Maya research + Alex development
        "showcase",      # Alex presents website
        "marketing",     # Sophie creates campaign
        "closing"        # Marcus wraps up
    ]
```

#### Phase Transitions:

```
greeting → interview → ideation_prep → ideation → showcase → marketing → closing
    │          ↕            │             │           │           │          │
    │      (6 Q&A)          │             │           │           │          │
    └──────────────────────┴─────────────┴───────────┴───────────┴──────────┘
                                    Managed by Marcus
```

### 4. Simple Orchestrator (`src/simple_orchestrator.py`)

Core orchestration engine handling:

- **WebSocket Management**: Direct connection to OpenAI
- **Audio Chunk Tracking**: Precise timing for transitions
- **Function Call Processing**: Dynamic speaker selection
- **State Management**: Conversation history and context

#### Key Methods:

```python
async def _get_persona_response(persona, prompt):
    # Connects to OpenAI Realtime API
    # Streams audio chunks
    # Processes function calls
    
async def _move_to_next_persona():
    # Implements speaker selection logic
    # Manages phase transitions
    # Handles human turns
```

### 5. AI Personas

Each persona is configured with:

```python
PersonaConfig(
    name="Marcus",
    voice="alloy",              # OpenAI voice model
    instructions="...",         # Behavior definition
    temperature=0.7,            # Response creativity
    max_response_tokens=4090    # Output limit
)
```

### 6. External Integrations

#### OpenManus Pipeline (`src/web_tools.py`)
- Automated website generation
- Real-time development execution
- Live server deployment

#### LinkedIn Integration (`src/personas/linkedin_marketer.py`)
- OAuth2 authentication
- DALL-E image generation
- API post creation

## 🔄 Data Flow

### 1. Audio Streaming Pipeline

```
OpenAI API → WebSocket → Orchestrator → SocketIO → Browser → WebAudio API
     ↓            ↓           ↓            ↓          ↓           ↓
  PCM16      Binary      Chunks      Base64      Blob      AudioBuffer
```

### 2. Function Call Flow

```
Persona Response → Function Call Detection → Execute Function → Update State
       ↓                    ↓                      ↓               ↓
   "I'll do X"    select_next_speaker()     Set next speaker   Transition
```

### 3. Development Pipeline

```
Alex Triggered → vibe_code() → OpenManus → npm install → npm run dev → Preview
       ↓              ↓            ↓           ↓             ↓           ↓
   "Building"    Execute      Generate     Install      Launch      Showcase
```

## 🎯 Design Decisions

### 1. Chunk-Based Audio Streaming

**Why**: Reduces latency from ~3s to <500ms
**How**: 430ms chunks streamed as generated
**Benefit**: Natural conversation flow

### 2. Phased Workflow

**Why**: Predictable business process
**How**: State machine with defined transitions
**Benefit**: Reliable project completion

### 3. Function-Based Speaker Selection

**Why**: Dynamic yet controlled flow
**How**: OpenAI function calling for decisions
**Benefit**: Natural conversation patterns

### 4. Separate Orchestrator Layers

**Why**: Separation of concerns
**How**: Base orchestrator + business logic layer
**Benefit**: Reusable components

## 🔐 Security Considerations

1. **API Key Management**: Environment variables
2. **Input Validation**: Sanitized user inputs
3. **Process Isolation**: Sandboxed execution
4. **Rate Limiting**: API call throttling
5. **Error Boundaries**: Graceful failure handling

## 📊 Performance Optimizations

### 1. Audio Streaming
- Chunk size: 430ms (optimal for latency/quality)
- Scheduling: Pre-calculated timing
- Buffering: Minimal to reduce delay

### 2. Concurrent Processing
- Parallel persona preparation
- Async WebSocket handling
- Non-blocking I/O operations

### 3. Resource Management
- Connection pooling
- Memory-efficient audio handling
- Automatic cleanup routines

## 🔌 Extension Points

### Adding New Personas

1. Define PersonaConfig
2. Add to persona list
3. Implement any special tools
4. Update phase logic if needed

### Custom Tools

```python
def _create_custom_function():
    return {
        "type": "function",
        "name": "custom_tool",
        "description": "...",
        "parameters": {...}
    }
```

### Workflow Modifications

1. Extend PhasedOrchestrator
2. Define new phases
3. Implement transition logic
4. Add phase-specific prompts

## 🏃 Runtime Flow

### Typical Session Lifecycle

1. **Initialization**
   - User clicks "Launch AI Business Team"
   - Server creates orchestrator instances
   - WebSocket connections established

2. **Greeting Phase**
   - Marcus introduces the team
   - Transitions to Sarah

3. **Interview Phase**
   - Sarah asks 6 questions
   - Human provides answers
   - Responses stored for team

4. **Development Phase**
   - Maya researches competitors
   - Alex builds website
   - Real-time terminal output

5. **Marketing Phase**
   - Sophie creates LinkedIn post
   - DALL-E generates image
   - Post published to company page

6. **Closing Phase**
   - Marcus thanks team
   - Session marked complete
   - Resources cleaned up

## 🧪 Testing Strategies

### Unit Tests
- Persona response validation
- Function call parsing
- Audio chunk management

### Integration Tests
- End-to-end workflow
- API communication
- External service mocking

### Performance Tests
- Audio latency measurement
- Concurrent session handling
- Memory usage profiling

## 📈 Monitoring & Debugging

### Logging Levels
- INFO: Normal operations
- DEBUG: Detailed flow
- ERROR: Failures and recovery

### Key Metrics
- Response latency
- Audio chunk timing
- API call success rates
- Session completion rates

### Debug Tools
- Browser DevTools for frontend
- Python debugger for backend
- Network inspection for APIs

## 🚀 Deployment Considerations

### Requirements
- Python 3.8+ environment
- Node.js for development pipeline
- FFmpeg for audio processing
- Sufficient API quotas

### Scaling Options
- Horizontal scaling with load balancer
- Queue-based job processing
- CDN for static assets
- Database for session persistence

### Production Checklist
- [ ] Environment variables configured
- [ ] Error handling comprehensive
- [ ] Logging infrastructure ready
- [ ] Monitoring alerts set up
- [ ] Backup strategies defined

---

This architecture enables Moentreprise to deliver a seamless, professional AI-powered business automation experience while maintaining flexibility for future enhancements. 