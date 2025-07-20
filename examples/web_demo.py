#!/usr/bin/env python3
"""
Simple Web Test for Orchestrator - Optimized for real-time performance
Test multiple personas in conversation chain using OpenAI Realtime API
"""

import asyncio
import json
import base64
from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO, emit
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from simple_orchestrator import SimpleOrchestrator, PersonaConfig
from openai_config import OPENAI_REALTIME_CONFIG
import threading
import queue
import time
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global orchestrator instance
orchestrator = None
website_showcased = False  # Flag to prevent Alex from showcasing multiple times

# REMOVED: audio_playback_complete event that was causing double-waiting

def convert_to_pcm16(audio_data: bytes) -> bytes:
    """Convert browser audio (WebM/WAV) to PCM16 format for OpenAI Realtime API"""
    try:
        import io
        import wave
        import subprocess
        import tempfile
        import os
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_input:
            temp_input.write(audio_data)
            temp_input_path = temp_input.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_output:
            temp_output_path = temp_output.name
        
        try:
            # Use ffmpeg to convert to PCM16 WAV (24kHz mono for OpenAI)
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-i', temp_input_path,
                '-acodec', 'pcm_s16le',
                '-ac', '1',  # mono
                '-ar', '24000',  # 24kHz sample rate for OpenAI
                temp_output_path
            ]
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ FFmpeg error: {result.stderr}")
                raise Exception(f"FFmpeg conversion failed: {result.stderr}")
            
            # Read the converted PCM16 WAV file and extract just the audio data
            with wave.open(temp_output_path, 'rb') as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
                print(f"🎵 Converted audio: {wav_file.getnframes()} frames, {wav_file.getframerate()}Hz, {wav_file.getnchannels()} channels")
                return frames
                
        finally:
            # Clean up temporary files
            try:
                os.unlink(temp_input_path)
                os.unlink(temp_output_path)
            except:
                pass
                
    except Exception as e:
        print(f"❌ Audio conversion failed: {e}")
        raise e

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>🚀 Moentreprise - AI Business Automation Platform</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.0/socket.io.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #4338ca;
            --primary-light: #5b21b6;
            --primary-dark: #312e81;
            --accent: #6b46c1;
            --success: #047857;
            --error: #b91c1c;
            --neutral: #4b5563;
            --light-gray: #f8fafc;
            --white: #ffffff;
            --text-dark: #1e1b4b;
            --text-light: #4338ca;
            --gradient-primary: linear-gradient(135deg, #312e81 0%, #4338ca 100%);
            --gradient-secondary: linear-gradient(135deg, #4338ca 0%, #6b46c1 100%);
            --shadow-soft: 0 4px 6px -1px rgba(67, 56, 202, 0.15), 0 2px 4px -1px rgba(67, 56, 202, 0.08);
            --shadow-medium: 0 10px 15px -3px rgba(67, 56, 202, 0.15), 0 4px 6px -2px rgba(67, 56, 202, 0.08);
            --shadow-large: 0 25px 50px -12px rgba(67, 56, 202, 0.25);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body { 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
            min-height: 100vh;
            color: var(--text-dark);
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header { 
            text-align: center; 
            background: var(--white);
            padding: 40px 30px; 
            border-radius: 20px; 
            margin-bottom: 30px;
            box-shadow: var(--shadow-large);
            position: relative;
            overflow: hidden;
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 5px;
            background: var(--gradient-primary);
        }
        
        .logo {
            width: 80px;
            height: 80px;
            margin: 0 auto 20px;
            background: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 36px;
            color: white;
            box-shadow: var(--shadow-medium);
            padding: 10px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }
        
        .header .subtitle {
            font-size: 1.2rem;
            color: var(--text-light);
            font-weight: 400;
        }
        
        .team-section {
            background: var(--white);
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: var(--shadow-medium);
        }
        
        .team-section h2 {
            font-size: 1.8rem;
            font-weight: 600;
            color: var(--text-dark);
            margin-bottom: 20px;
            text-align: center;
        }
        
        .personas-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .persona-card {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            padding: 20px;
            border-radius: 15px;
            border: 2px solid transparent;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .persona-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            transition: all 0.3s ease;
        }
        
        .persona-card:hover {
            transform: translateY(-5px);
            box-shadow: var(--shadow-large);
        }
        
        .persona-card.marcus::before { background: var(--gradient-primary); }
        .persona-card.sarah::before { background: var(--gradient-secondary); }
        .persona-card.alex::before { background: var(--gradient-primary); }
        .persona-card.maya::before { background: var(--gradient-secondary); }
        .persona-card.sophie::before { background: var(--gradient-primary); }
        
        .persona-header {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .persona-avatar {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            color: white;
            margin-right: 15px;
            box-shadow: var(--shadow-soft);
        }
        
        .marcus .persona-avatar { background: var(--primary); }
        .sarah .persona-avatar { background: var(--accent); }
        .alex .persona-avatar { background: var(--primary-light); }
        .maya .persona-avatar { background: var(--accent); }
        .sophie .persona-avatar { background: var(--primary); }
        
        .persona-name {
            font-size: 1.3rem;
            font-weight: 600;
            color: var(--text-dark);
        }
        
        .persona-role {
            font-size: 0.9rem;
            color: var(--text-light);
            font-weight: 500;
        }
        
        .persona-description {
            color: var(--text-light);
            font-size: 0.95rem;
            line-height: 1.5;
        }
        
        .controls { 
            background: var(--white);
            padding: 30px; 
            border-radius: 20px; 
            margin-bottom: 30px;
            box-shadow: var(--shadow-medium);
        }
        
        .conversation { 
            background: var(--white);
            padding: 30px; 
            border-radius: 20px; 
            max-height: 600px; 
            overflow-y: auto;
            box-shadow: var(--shadow-medium);
        }
        
        .turn { 
            margin: 15px 0; 
            padding: 20px; 
            border-radius: 15px; 
            border-left: 5px solid #ccc;
            animation: slideIn 0.4s ease-out;
            box-shadow: var(--shadow-soft);
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        .marcus { border-left-color: var(--primary); background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%); }
        .sarah { border-left-color: var(--accent); background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%); }
        .alex { border-left-color: var(--primary-light); background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%); }
        .maya { border-left-color: var(--accent); background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%); }
        .sophie { border-left-color: var(--primary); background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%); }
        .human { border-left-color: var(--neutral); background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); }
        .system { border-left-color: var(--neutral); background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); font-style: italic; }
        
        button { 
            padding: 15px 30px; 
            font-size: 16px; 
            font-weight: 600;
            margin: 10px; 
            cursor: pointer; 
            border: none; 
            border-radius: 12px;
            color: white;
            transition: all 0.3s ease;
            box-shadow: var(--shadow-soft);
            font-family: inherit;
        }
        
        button:hover { 
            transform: translateY(-2px); 
            box-shadow: var(--shadow-medium); 
        }
        
        button:disabled { 
            opacity: 0.6; 
            cursor: not-allowed; 
            transform: none; 
            box-shadow: var(--shadow-soft);
        }
        
        .start { background: linear-gradient(135deg, var(--success) 0%, #047857 100%); }
        .stop { background: linear-gradient(135deg, var(--error) 0%, #b91c1c 100%); }
        .clear { background: var(--gradient-secondary); }
        .mic { background: var(--gradient-primary); }
        
        #status { 
            font-weight: 600; 
            padding: 20px; 
            margin: 20px 0; 
            border-radius: 12px;
            text-align: center;
            transition: all 0.3s ease;
            box-shadow: var(--shadow-soft);
        }
        
        .active { 
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
            color: var(--success); 
            border: 2px solid var(--success);
        }
        
        .inactive { 
            background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
            color: var(--error); 
            border: 2px solid var(--error);
        }
        
        .speaking { 
            background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
            color: var(--primary-dark); 
            border: 2px solid var(--primary);
        }
        
        .working { 
            background: linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 100%);
            color: var(--accent); 
            border: 2px solid var(--accent);
        }
        
        .audio-indicator {
            display: inline-block;
            width: 20px;
            height: 20px;
            margin-left: 10px;
            animation: pulse 1.5s infinite;
        }
        
        .loading-dots {
            display: inline-block;
        }
        
        .loading-dots::after {
            content: '';
            display: inline-block;
            animation: loading-dots 1.4s infinite;
        }
        
        @keyframes loading-dots {
            0%, 20% { content: ''; }
            40% { content: '.'; }
            60% { content: '..'; }
            80%, 100% { content: '...'; }
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(1.1); }
        }
        
        /* Terminal Display Styles */
        .terminal-container {
            background: var(--white);
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: var(--shadow-medium);
            display: none; /* Hidden by default */
        }
        
        .terminal-header {
            background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
            color: #fff;
            padding: 15px 20px;
            border-radius: 12px 12px 0 0;
            font-weight: 600;
            border-bottom: 1px solid #374151;
            display: flex;
            align-items: center;
        }
        
        .terminal-header::before {
            content: '💻';
            margin-right: 10px;
            font-size: 20px;
        }
        
        .terminal-content {
            background: #0d1117;
            color: #58a6ff;
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 14px;
            padding: 20px;
            border-radius: 0 0 12px 12px;
            max-height: 400px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            border: 2px solid #21262d;
            border-top: none;
            line-height: 1.5;
        }
        
        /* Website Preview Styles */
        .website-preview {
            border: 3px solid var(--primary);
            box-shadow: 0 10px 25px rgba(67, 56, 202, 0.25);
            border-radius: 15px;
            animation: websiteGlow 2s ease-in-out infinite;
        }
        
        @keyframes websiteGlow {
            0%, 100% { 
                box-shadow: 0 10px 25px rgba(67, 56, 202, 0.25);
                transform: scale(1);
            }
            50% { 
                box-shadow: 0 15px 35px rgba(67, 56, 202, 0.35);
                transform: scale(1.02);
            }
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .container { padding: 15px; }
            .header { padding: 30px 20px; }
            .header h1 { font-size: 2rem; }
            .personas-grid { grid-template-columns: 1fr; }
            .persona-card { margin-bottom: 15px; }
            button { padding: 12px 20px; font-size: 14px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <img src="/mo-logo" alt="Mo Logo" style="width: 60px; height: 60px; object-fit: contain;">
            </div>
            <h1>Moentreprise</h1>
            <p class="subtitle">AI-Powered Business Automation Platform</p>
        </div>

        <div class="team-section">
            <h2>🌟 Meet Your AI Business Team</h2>
            <div class="personas-grid">
                <div class="persona-card marcus">
                    <div class="persona-header">
                        <div class="persona-avatar">👨‍💼</div>
                        <div>
                            <div class="persona-name">Marcus</div>
                            <div class="persona-role">Project Manager</div>
                        </div>
                    </div>
                    <div class="persona-description">
                        Leads the entire project from start to finish. Coordinates team members, manages timelines, and ensures client requirements are met. Your trusted point of contact throughout the journey.
                    </div>
                </div>

                <div class="persona-card sarah">
                    <div class="persona-header">
                        <div class="persona-avatar">👩‍💻</div>
                        <div>
                            <div class="persona-name">Sarah</div>
                            <div class="persona-role">Business Analyst</div>
                        </div>
                    </div>
                    <div class="persona-description">
                        Conducts detailed requirement gathering through friendly interviews. Understands your business needs, target audience, and project goals to create the perfect brief for the team.
                    </div>
                </div>

                <div class="persona-card alex">
                    <div class="persona-header">
                        <div class="persona-avatar">👨‍💻</div>
                        <div>
                            <div class="persona-name">Alex</div>
                            <div class="persona-role">Full-Stack Developer</div>
                        </div>
                    </div>
                    <div class="persona-description">
                        Transforms ideas into reality by building beautiful, functional websites. Specializes in modern web technologies and creates responsive, user-friendly digital experiences.
                    </div>
                </div>

                <div class="persona-card maya">
                    <div class="persona-header">
                        <div class="persona-avatar">👩‍🔬</div>
                        <div>
                            <div class="persona-name">Maya</div>
                            <div class="persona-role">Research Specialist</div>
                        </div>
                    </div>
                    <div class="persona-description">
                        Conducts market research and competitive analysis. Gathers inspiration from successful websites in your industry to inform design and functionality decisions.
                    </div>
                </div>

                <div class="persona-card sophie">
                    <div class="persona-header">
                        <div class="persona-avatar">👩‍🎨</div>
                        <div>
                            <div class="persona-name">Sophie</div>
                            <div class="persona-role">Marketing Director</div>
                        </div>
                    </div>
                    <div class="persona-description">
                        Creates compelling marketing campaigns and social media content. Specializes in LinkedIn marketing with AI-generated visuals to promote your business launch effectively.
                    </div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 20px; padding: 20px; background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%); border-radius: 15px; border-left: 4px solid var(--primary);">
                <strong style="color: var(--primary-dark);">🎯 How it works:</strong> Each AI team member collaborates naturally, choosing who speaks next based on project needs. Experience seamless business automation with intelligent workflow management!
            </div>
        </div>

        <div class="controls">
            <div id="status" class="inactive">Ready to launch your business automation experience</div>
            
            <div style="text-align: center; margin-bottom: 20px;">
                <button onclick="startConversation()" class="start" id="startBtn">
                    🚀 Launch AI Business Team
                </button>
                
                <button onclick="stopConversation()" class="stop" id="stopBtn" disabled>
                    🛑 Stop Session
                </button>
                
                <button onclick="clearConversation()" class="clear">
                    🧹 Clear Workspace
                </button>
                
                <button id="micBtn" onmousedown="startRecording()" onmouseup="stopRecording()" 
                        onmouseleave="stopRecording()" style="display: none;" class="mic">
                    🎤 Hold to Speak
                </button>
            </div>
            
            <div style="background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%); padding: 15px; border-radius: 12px; border: 1px solid var(--primary); margin-top: 15px;">
                <div style="font-weight: 600; color: var(--primary-dark); margin-bottom: 8px;">💡 Getting Started:</div>
                <div style="color: var(--text-light); font-size: 0.95rem; line-height: 1.5;">
                    Click "Launch AI Business Team" to start your automated business consultation. Your AI team will guide you through requirements gathering, website development, and marketing launch - all in real-time!
                </div>
            </div>
        </div>

        <!-- Terminal Display -->
        <div class="terminal-container" id="terminalContainer">
            <div class="terminal-header">
                Implementation Pipeline - Live Development Output
            </div>
            <div class="terminal-content" id="terminalOutput">
                <!-- Terminal output will appear here -->
            </div>
        </div>

        <div class="conversation" id="conversation">
            <div style="text-align: center; padding: 40px 20px; color: var(--text-light);">
                <div style="font-size: 3rem; margin-bottom: 20px;">🤖</div>
                <h3 style="color: var(--text-dark); margin-bottom: 10px;">Ready for AI Business Automation</h3>
                <p>Launch your AI business team to experience intelligent project management, automated development, and strategic marketing - all working together seamlessly!</p>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        let isActive = false;
        let mediaRecorder = null;
        let isRecording = false;
        let audioChunks = [];
        let currentSpeaker = null;
        let audioContextStartTime = null;
        
        // Terminal output accumulator
        let terminalOutput = '';
        let terminalVisible = false;
        
        // Microphone management
        let microphoneStream = null;
        let isMicrophoneMuted = false;
        
        // Optimized audio streaming system - no waiting for confirmation
        class AudioStreamPlayer {
            constructor() {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                this.isPlaying = false;
                this.startTime = 0;
                this.scheduledDuration = 0;
                this.chunkCount = 0;
                this.speakerName = null;
                this.sources = []; // Track all scheduled sources
            }
            
            async addChunk(audioBase64, speakerName) {
                try {
                    // Decode base64 to array buffer
                    const binaryString = atob(audioBase64);
                    const bytes = new Uint8Array(binaryString.length);
                    for (let i = 0; i < binaryString.length; i++) {
                        bytes[i] = binaryString.charCodeAt(i);
                    }
                    
                    // Decode audio data
                    const audioBuffer = await this.audioContext.decodeAudioData(bytes.buffer);
                    
                    this.chunkCount++;
                    console.log(`🎵 Chunk ${this.chunkCount} for ${speakerName}: ${audioBuffer.duration.toFixed(3)}s`);
                    
                    // Schedule playback
                    this.scheduleChunk(audioBuffer, speakerName);
                    
                } catch (e) {
                    console.error('Error adding audio chunk:', e);
                }
            }
            
            scheduleChunk(audioBuffer, speakerName) {
                const source = this.audioContext.createBufferSource();
                source.buffer = audioBuffer;
                source.connect(this.audioContext.destination);
                
                const currentTime = this.audioContext.currentTime;
                let startTime;
                
                if (!this.isPlaying) {
                    // First chunk - start immediately
                    startTime = currentTime + 0.01; // Minimal delay
                    this.startTime = startTime;
                    this.isPlaying = true;
                    this.speakerName = speakerName;
                    audioContextStartTime = Date.now();
                } else {
                    // Schedule seamlessly after previous chunks
                    startTime = this.startTime + this.scheduledDuration;
                }
                
                source.start(startTime);
                this.sources.push(source);
                this.scheduledDuration += audioBuffer.duration;
                
                // Log precise timing
                const msUntilPlay = ((startTime - currentTime) * 1000).toFixed(0);
                console.log(`⏱️ Chunk ${this.chunkCount} scheduled: +${msUntilPlay}ms`);
            }
            
            getEstimatedCompletionTime() {
                if (!this.isPlaying) return 0;
                const remainingTime = (this.startTime + this.scheduledDuration) - this.audioContext.currentTime;
                return Math.max(0, remainingTime * 1000); // Convert to milliseconds
            }
            
            reset() {
                // Stop all scheduled sources
                this.sources.forEach(source => {
                    try { source.stop(); } catch (e) {}
                });
                this.sources = [];
                this.isPlaying = false;
                this.startTime = 0;
                this.scheduledDuration = 0;
                this.chunkCount = 0;
                this.speakerName = null;
                console.log('🔄 Audio player reset');
            }
        }
        
        const audioPlayer = new AudioStreamPlayer();

        // Microphone Control Functions
        function muteMicrophone() {
            if (microphoneStream) {
                microphoneStream.getTracks().forEach(track => {
                    track.enabled = false; // Mute the track
                });
                isMicrophoneMuted = true;
                console.log('🔇 Microphone muted');
            }
        }
        
        function unmuteMicrophone() {
            if (microphoneStream) {
                microphoneStream.getTracks().forEach(track => {
                    track.enabled = true; // Unmute the track
                });
                isMicrophoneMuted = false;
                console.log('🎤 Microphone unmuted');
            }
        }
        
        function stopMicrophone() {
            if (microphoneStream) {
                microphoneStream.getTracks().forEach(track => track.stop());
                microphoneStream = null;
                isMicrophoneMuted = false;
                console.log('🛑 Microphone stopped');
            }
        }

        // Socket event handlers
        socket.on('status', function(data) {
            const status = document.getElementById('status');
            status.textContent = data.message;
            status.className = data.type;
        });

        socket.on('persona_started', function(data) {
            const status = document.getElementById('status');
            status.innerHTML = `🎤 ${data.name} is speaking... <span class="audio-indicator">🔊</span>`;
            status.className = 'speaking';
            
            // CRITICAL: Mute microphone to prevent feedback during persona speech
            muteMicrophone();
            
            // Reset audio player for new speaker
            currentSpeaker = data.name;
            audioPlayer.reset();
            audioPlayer.speakerName = data.name;
            
            console.log(`🎤 ${data.name} started speaking - microphone muted`);
        });
        
        socket.on('audio_chunk', function(data) {
            // Stream audio chunks immediately as they arrive
            if (data.speaker === currentSpeaker && data.audio) {
                audioPlayer.addChunk(data.audio, data.speaker);
            }
        });

        socket.on('persona_finished', function(data) {
            // Just update the conversation display - no waiting!
            addToConversation(data.name.toLowerCase(), `${data.name}: ${data.text}`);
            
            // Log timing info (using 400ms per chunk for faster transitions)
            const estimatedRemaining = audioPlayer.getEstimatedCompletionTime();
            console.log(`✅ ${data.name} finished. Audio will complete in ~${estimatedRemaining.toFixed(0)}ms`);
            
            // Update status to show transition
            const status = document.getElementById('status');
            status.textContent = `Transitioning to next speaker...`;
            status.className = 'active';
        });

        socket.on('conversation_complete', function(data) {
            const status = document.getElementById('status');
            status.textContent = '🎬 Conversation completed!';
            status.className = 'inactive';
            
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            isActive = false;
            
            addToConversation('system', '🎬 Business automation session completed! Your AI team delivered exceptional results.');
            
            // Reset audio player and cleanup microphone
            audioPlayer.reset();
            cleanupMicrophone();
        });
        // ---------- live terminal stream ----------
        socket.on('terminal_chunk', function(data){
            // Show terminal container on first output
            if (!terminalVisible) {
                document.getElementById('terminalContainer').style.display = 'block';
                terminalVisible = true;
            }
            
            // Accumulate terminal output
            terminalOutput += data.text;
            
            // Update terminal display
            const terminalElement = document.getElementById('terminalOutput');
            terminalElement.textContent = terminalOutput;
            
            // Auto-scroll to bottom
            terminalElement.scrollTop = terminalElement.scrollHeight;
            
            // Optional: Also add a system message for the first terminal output
            if (terminalOutput.length < 100) { // Only for the beginning
                addToConversation('system', '💻 Implementation pipeline started - check terminal output above!');
            }
        });

        // ---------- dev server popup preview ----------
        socket.on('dev_server_ready', function(data){
            addToConversation('system', '<strong>💻 Dev server launched: '+data.url+'</strong>');
            
            // Show website in a popup window (with built-in server checking)
            // Alex showcase will be triggered automatically when popup confirms it's working
            showWebsitePopup(data.url);
            
            console.log('🎯 Popup will trigger Alex showcase when website is confirmed working');
        });
        
        socket.on('linkedin_post_created', function(data){
            console.log('📱 LinkedIn post created:', data);
            
            // Add LinkedIn post info to conversation
            const postInfo = `🔗 LinkedIn post created: "${data.content.substring(0, 100)}..." ${data.image_generated ? '🖼️ With AI-generated image' : ''} ${data.post_url ? `📍 ${data.post_url}` : ''}`;
            addToConversation('system', postInfo);
            
            // Show a nice notification
            if (data.post_url) {
                addToConversation('system', `✅ Successfully posted to LinkedIn! 🎉`);
            }
        });
        
        // Status indicators for AI personas working
        socket.on('maya_searching', function(data){
            const status = document.getElementById('status');
            status.innerHTML = `🔍 Maya is analyzing similar websites... <span class="loading-dots"></span>`;
            status.className = 'working';
            console.log('🔍 Maya started website research');
        });
        
        socket.on('sophie_creating_content', function(data){
            const status = document.getElementById('status');
            status.innerHTML = `✨ Sophie is crafting LinkedIn marketing content... <span class="loading-dots"></span>`;
            status.className = 'working';
            console.log('✨ Sophie started content creation');
        });
        
        socket.on('sophie_generating_image', function(data){
            const status = document.getElementById('status');
            status.innerHTML = `🎨 Sophie is generating a beautiful marketing image... <span class="loading-dots"></span>`;
            status.className = 'working';
            console.log('🎨 Sophie started image generation');
        });
        
        socket.on('sophie_posting_linkedin', function(data){
            const status = document.getElementById('status');
            status.innerHTML = `📱 Sophie is publishing to LinkedIn... <span class="loading-dots"></span>`;
            status.className = 'working';
            console.log('📱 Sophie posting to LinkedIn');
        });
        socket.on('human_turn_started', function(data) {
            // Wait for persona audio to finish before activating microphone
            const estimatedRemaining = audioPlayer.getEstimatedCompletionTime();
            const delay = Math.max(500, estimatedRemaining + 200); // At least 500ms, or audio + 200ms buffer
            
            console.log(`🎤 Human turn starting - waiting ${delay}ms for audio to complete`);
            
            setTimeout(() => {
            const status = document.getElementById('status');
            status.innerHTML = '🎤 Your turn! Hold the microphone button to speak';
            status.className = 'speaking';
            
            addToConversation('system', '🎤 Your turn! Hold the microphone button to jump in.');
                
                // Now safe to activate microphone
                unmuteMicrophone();
            showMicrophoneButton();
                
                console.log(`🎤 Microphone activated for human input`);
            }, delay);
        });

        socket.on('human_turn_ended', function(data) {
            // Mute microphone when human turn ends
            muteMicrophone();
            hideMicrophoneButton();
            console.log(`🎤 Human turn ended - microphone muted`);
        });
        


        // UI Functions
        function startConversation() {
            if (isActive) return;
            
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
            isActive = true;
            
            // Clear conversation and terminal first
            document.getElementById('conversation').innerHTML = '';
            clearTerminal();
            
            fetch('/start_orchestrator', {method: 'POST'})
                .then(r => r.json())
                .then(d => {
                    if (d.error) {
                        alert('Error: ' + d.error);
                        resetButtons();
                    }
                })
                .catch(e => {
                    console.error('Error:', e);
                    alert('Failed to start conversation');
                    resetButtons();
                });
        }

        function stopConversation() {
            if (!isActive) return;
            
            // Stop any playing audio and cleanup microphone
            audioPlayer.reset();
            cleanupMicrophone();
            
            fetch('/stop_orchestrator', {method: 'POST'})
                .then(r => r.json())
                .then(d => console.log('Stopped:', d));
            
            resetButtons();
        }

        function clearConversation() {
            document.getElementById('conversation').innerHTML = 
                '<div style="text-align: center; padding: 40px 20px; color: var(--text-light);"><div style="font-size: 3rem; margin-bottom: 20px;">🤖</div><h3 style="color: var(--text-dark); margin-bottom: 10px;">Ready for AI Business Automation</h3><p>Launch your AI business team to experience intelligent project management, automated development, and strategic marketing - all working together seamlessly!</p></div>';
            audioPlayer.reset();
            
            // Clear terminal and microphone
            clearTerminal();
            cleanupMicrophone();
        }
        
        function clearTerminal() {
            terminalOutput = '';
            terminalVisible = false;
            document.getElementById('terminalContainer').style.display = 'none';
            document.getElementById('terminalOutput').textContent = '';
        }
        
        function cleanupMicrophone() {
            stopMicrophone();
            hideMicrophoneButton();
        }
        
        async function showWebsitePopup(url) {
            addToConversation('system', '⏳ Waiting for dev server to be ready...');
            
            // Wait for server to be ready before opening popup
            const serverReady = await waitForServer(url);
            
            if (serverReady) {
                addToConversation('system', '✅ Server ready! Opening website...');
                
                // Create popup window with the website
                const popup = window.open(
                    url, 
                    'websitePreview', 
                    'width=900,height=700,scrollbars=yes,resizable=yes,status=yes,toolbar=no,menubar=no,location=yes'
                );
                
                if (popup) {
                    // Focus the popup
                    popup.focus();
                    
                    addToConversation('system', '🌐 Website opened in new window! Perfect! 🎉');
                    
                    // 🎯 WEBSITE WORKING PERFECTLY - Signal immediate Alex showcase
                    console.log('🎯 Website popup working perfectly - triggering Alex showcase immediately');
                    
                    // Stop any potential Marcus threads and trigger Alex immediately
                    socket.emit('website_working_perfectly', {url: url});
                    
                    // Auto-close popup after 45 seconds
                    setTimeout(() => {
                        if (!popup.closed) {
                            popup.close();
                            console.log('Website popup auto-closed after 45 seconds');
                        }
                    }, 45000);
                } else {
                    // Popup blocked - fallback to inline iframe with delay
                    addToConversation('system', '⚠️ Popup blocked - showing inline preview:');
                    setTimeout(() => {
                        const ifr = document.createElement('iframe');
                        ifr.src = url;
                        ifr.style = 'width:100%;height:450px;margin-top:10px;';
                        ifr.className = 'website-preview';
                        document.getElementById('conversation').appendChild(ifr);
                        
                        // Even for iframe fallback, trigger Alex showcase if content loads
                        ifr.onload = () => {
                            console.log('🎯 Website iframe loaded successfully - triggering Alex showcase');
                            socket.emit('website_working_perfectly', {url: url});
                        };
                        
                        setTimeout(()=>ifr.remove(), 25000); // Remove after 25 seconds
                    }, 1000); // 1 second delay for iframe
                }
            } else {
                addToConversation('system', '❌ Server connection failed - please check the terminal output');
            }
        }
        
        async function waitForServer(url, maxAttempts = 10) {
            console.log(`🔄 Checking server availability: ${url}`);
            
            for (let attempt = 1; attempt <= maxAttempts; attempt++) {
                try {
                    console.log(`📡 Attempt ${attempt}/${maxAttempts} - checking ${url}`);
                    
                    // Update status for user feedback
                    if (attempt > 1) {
                        addToConversation('system', `🔄 Checking server... (attempt ${attempt}/${maxAttempts})`);
                    }
                    
                    // Use fetch with timeout to check if server responds
                    const controller = new AbortController();
                    const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 second timeout
                    
                    const response = await fetch(url, { 
                        method: 'HEAD', // Just check if server responds
                        signal: controller.signal,
                        cache: 'no-cache'
                    });
                    
                    clearTimeout(timeoutId);
                    
                    if (response.ok || response.status < 500) {
                        console.log(`✅ Server ready on attempt ${attempt}`);
                        return true;
                    }
                } catch (error) {
                    console.log(`⚠️ Attempt ${attempt} failed:`, error.message);
                    
                    // Don't show error for first few attempts (normal startup time)
                    if (attempt > 3) {
                        addToConversation('system', `⚠️ Server not responding yet... (${error.name})`);
                    }
                }
                
                // Wait 2 seconds before next attempt
                if (attempt < maxAttempts) {
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }
            }
            
            console.log(`❌ Server not ready after ${maxAttempts} attempts`);
            return false;
        }

        function resetButtons() {
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            isActive = false;
            
            const status = document.getElementById('status');
            status.textContent = 'Ready to launch your business automation experience';
            status.className = 'inactive';
        }

        function addToConversation(speaker, text) {
            const conversation = document.getElementById('conversation');
            
            const turn = document.createElement('div');
            turn.className = `turn ${speaker}`;
            turn.innerHTML = `<strong>${new Date().toLocaleTimeString()}</strong><br>${text}`;
            
            conversation.appendChild(turn);
            conversation.scrollTop = conversation.scrollHeight;
        }

        function showMicrophoneButton() {
            document.getElementById('micBtn').style.display = 'inline-block';
        }

        function hideMicrophoneButton() {
            document.getElementById('micBtn').style.display = 'none';
        }

        // Recording functions
        async function startRecording() {
            if (isRecording) return;
            
            try {
                // Get microphone stream if not already available
                if (!microphoneStream) {
                    microphoneStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    console.log('🎤 Microphone stream acquired');
                }
                
                // Ensure microphone is unmuted for recording
                if (isMicrophoneMuted) {
                    unmuteMicrophone();
                }
                
                mediaRecorder = new MediaRecorder(microphoneStream);
                audioChunks = [];
                
                mediaRecorder.ondataavailable = function(event) {
                    audioChunks.push(event.data);
                };
                
                mediaRecorder.onstop = function() {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    sendAudioToServer(audioBlob);
                };
                
                mediaRecorder.start();
                isRecording = true;
                
                const micBtn = document.getElementById('micBtn');
                micBtn.textContent = '🔴 Recording...';
                micBtn.style.background = '#e74c3c';
                
                console.log('🎤 Started recording');
            } catch (error) {
                console.error('Error accessing microphone:', error);
                alert('Could not access microphone. Please check permissions.');
            }
        }

        function stopRecording() {
            if (!isRecording || !mediaRecorder) return;
            
            mediaRecorder.stop();
            isRecording = false;
            
            const micBtn = document.getElementById('micBtn');
            micBtn.textContent = '🎤 Hold to Speak';
            micBtn.style.background = '#3498db';
            
            console.log('🎤 Stopped recording');
        }

        function sendAudioToServer(audioBlob) {
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.wav');
            
            fetch('/human_audio', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                console.log('Audio sent successfully:', data);
                addToConversation('human', `You: "${data.transcription || '[Speaking...]'}"`);
            })
            .catch(error => {
                console.error('Error sending audio:', error);
                alert('Error sending audio to server');
            });
        }
        
        // Log performance metrics
        setInterval(() => {
            if (isActive && currentSpeaker) {
                const remaining = audioPlayer.getEstimatedCompletionTime();
                if (remaining > 0) {
                    console.log(`⏱️ ${currentSpeaker}: ${remaining.toFixed(0)}ms audio remaining`);
                }
            }
        }, 1000);
    </script>
</body>
</html>
'''

@app.route('/start_orchestrator', methods=['POST'])
def start_orchestrator():
    """Start the AI conversation orchestrator - OPTIMIZED VERSION"""
    global orchestrator
    
    try:
        print("🎭 Starting OPTIMIZED AI orchestrator...")
        
        if orchestrator and orchestrator.is_conversation_active():
            return jsonify({'error': 'Conversation already active'})
        
        
        # Define the personas - AI Conspiracy with Natural Personalities!
        personas = [
            # 0 – Marcus (Project Manager)
            PersonaConfig(
                name="Marcus",
                voice="alloy",
                instructions="You are Marcus, the Project Manager. Process has two phases:\nPHASE A – Interview (Sarah + Human).\n   • First, greet the client warmly in ≤2 sentences.\n   • THEN call `select_next_speaker` with `speaker_index=\"1\"` (Sarah) so she can interview.\nPHASE B – Ideation round.\n   • When Sarah later returns the mic to you with complete requirements, acknowledge her effort in one friendly sentence, then delegate FIRST TASK to Maya: 'Please find at least five similar websites and take screenshots for inspiration.' After saying this, call `select_next_speaker` with `speaker_index=\"4\"` (Maya).\nKeep responses friendly and professional. Always include the required `select_next_speaker`.",
                temperature=0.7,
                max_response_tokens=4090
            ),
            # 1 – Sarah (Interviewer)
            PersonaConfig(
                name="Sarah",
                voice="sage",
                instructions="You are Sarah, the Interviewer. Your job is to collect basic requirements in plain language **for non-technical clients**. Ask one short, clear question (<=10 words) at a time. Keep tone friendly and conversational, not robotic. Questions can be up to 12 words. Focus on:\n 1. Target audience\n 2. Required pages\n 3. Colour palette\n 4. Inspiration sites\n 5. Timeline & budget\n 6. Success metric.\nRULE: Your reply must contain **one** clear question (<=10 words). Do NOT send an empty message. After the question, immediately call the function.\nBefore the question, write a brief acknowledgement of the user's last answer in ONE short sentence (e.g., 'Got it - noted.'). Maintain an internal checklist; never repeat a question you've already asked. Ask the next unseen question from the list. If the answer is vague, politely ask for a concrete example. After each question call `select_next_speaker` with `speaker_index=\"7\"`. When all info gathered, thank them and hand control back to Marcus with `speaker_index=\"0\".",
                temperature=0.6,
                max_response_tokens=4090
            ),
            # 2 – Alex (Developer/Implementer)
            PersonaConfig(
                name="Alex",
                voice="coral",
                instructions="You are Alex, the Developer. After receiving Marcus's design direction and Maya's research, you have enough information to create the website. Say something like 'I have enough information to create the website, proceeding with implementation' then immediately call the `vibe_code` function to trigger the automated build pipeline. Do NOT call select_next_speaker - let the pipeline handle the next steps.",
                temperature=0.8,
                max_response_tokens=4090
            ),
            # 3 – Jordan (Developer)
            PersonaConfig(
                name="Jordan",
                voice="coral",
                instructions="You are Jordan, the Developer. Suggest one technical architecture or framework choice suited to this project (≤2 sentences).  Then call `select_next_speaker` with `speaker_index=\"4\"` (Maya).",
                temperature=0.8,
                max_response_tokens=4090
            ),
            # 4 – Maya (Researcher)
            PersonaConfig(
                name="Maya",
                voice="sage",
                instructions="You are Maya, the Researcher. Simply say 'Screenshots updated' and nothing more. Be very brief - just those two words.",
                temperature=0.8,
                max_response_tokens=50
            ),
            # 5 – Casey (Marketer)
            PersonaConfig(
                name="Casey",
                voice="verse",
                instructions="You are Casey, the Marketer. Offer one initial marketing angle or launch channel (≤2 sentences). Then call `select_next_speaker` with `speaker_index=\"6\"` (Sam).",
                temperature=0.8,
                max_response_tokens=4090
            ),
            # 6 – Sam (Validator)
            PersonaConfig(
                name="Sam",
                voice="ash",
                instructions="You are Sam, the Validator. In 1 sentence summarise the collective ideas and confirm they meet the requirements, then call `select_next_speaker` with `speaker_index=\"0\"` (Marcus).",
                temperature=0.7,
                max_response_tokens=4090
            ),
            # 7 – Sophie (LinkedIn Marketing Director)
            PersonaConfig(
                name="Sophie",
                voice="sage",
                instructions="""You are Sophie, the Marketing Director specializing in LinkedIn marketing.

When called upon, you should:
1. FIRST, speak enthusiastically: "Fantastic! I'll create an amazing LinkedIn marketing campaign for our beautiful LeFleur website! Let me craft an engaging post with a stunning floral image to announce our launch to the professional community."
2. Then immediately call the post_to_linkedin function with content about the website launch
3. Finally, call select_next_speaker with speaker_index='0' to return control to Marcus

You MUST:
- Speak your full response out loud (the text above)
- Call post_to_linkedin function
- Call select_next_speaker with speaker_index='0'

Do NOT wait for the LinkedIn post to complete - just announce what you're doing and pass control back to Marcus.""",
                temperature=0.7,
                max_response_tokens=800
            )
        ]
        # NOTE: Human will be automatically appended as index 8 by SimpleOrchestrator.
        
        # Create optimized orchestrator
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
        from phased_orchestrator import PhasedOrchestrator
        orchestrator = PhasedOrchestrator(personas, OPENAI_REALTIME_CONFIG)
        # Allow enough turns for greeting, 6-question interview, ideation round and closing
        orchestrator.max_turns = 30

        # -----------------------------------------------
        # DEBUG – optionally skip the interview phase
        # -----------------------------------------------
        if True:
            orchestrator.interview_notes = [
                "Target audience: flower lovers in Paris.",
                "Pages needed: Home, Catalogue, About, Contact.",
                "Preferred palette: red-rose with white accents.",
                "amazon",
                "Timeline: 2 weeks, budget €3k.",
                "nice website."
            ]
            orchestrator.phase = "ideation_prep"  # jump past interview
            orchestrator.questions_left = 0
        
        # CRITICAL: Add audio chunk streaming handler
        orchestrator.on_audio_chunk = lambda speaker, chunk_b64: socketio.emit('audio_chunk', {
            'speaker': speaker,
            'audio': chunk_b64
        })
        
        # Simple event handlers - no extra waiting
        orchestrator.on_persona_started = lambda name: socketio.emit('persona_started', {'name': name})
        orchestrator.on_human_turn_started = lambda: socketio.emit('human_turn_started', {})
        orchestrator.on_human_turn_ended = lambda: socketio.emit('human_turn_ended', {})
        orchestrator.on_terminal_chunk = lambda text: socketio.emit('terminal_chunk', {'text': text})
        orchestrator.on_dev_server_ready = lambda url: socketio.emit('dev_server_ready', {'url': url})
        
        # Status indicators for persona activities
        orchestrator.on_maya_searching = lambda: socketio.emit('maya_searching', {})
        orchestrator.on_sophie_creating_content = lambda: socketio.emit('sophie_creating_content', {})
        orchestrator.on_sophie_generating_image = lambda: socketio.emit('sophie_generating_image', {})
        orchestrator.on_sophie_posting_linkedin = lambda: socketio.emit('sophie_posting_linkedin', {})
        
        def on_persona_finished(name, text, audio_data):
            """Handle persona finished - NO WAITING, just emit the event"""
            print(f"🎬 {name} finished speaking: {text[:50]}...")
            
            # Just emit the completion event - orchestrator handles all timing
            socketio.emit('persona_finished', {
                'name': name, 
                'text': text
            })
        
        orchestrator.on_persona_finished = on_persona_finished
        orchestrator.on_conversation_complete = lambda: socketio.emit('conversation_complete', {})
        
        # REMOVED: audio_playback_complete handler that was causing double-waiting
        
        def run_orchestrator():
            """Run orchestrator in background thread - OPTIMIZED"""
            global website_showcased
            
            # Reset flags for new conversation
            website_showcased = False
            print("🔄 Reset website_showcased flag for new conversation")
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # NO PATCHING - use orchestrator's optimized timing as-is
                
                loop.run_until_complete(orchestrator.start_conversation_async(
                    "Hello! I'd like to create an online flower shop called LeFleur based in Paris. Can you help me?"
                ))
            except Exception as e:
                print(f"❌ Orchestrator error: {e}")
                socketio.emit('status', {'type': 'inactive', 'message': f'Error: {e}'})
            finally:
                loop.close()
        
        # Start orchestrator in background thread
        import threading
        threading.Thread(target=run_orchestrator, daemon=True).start()
        
        socketio.emit('status', {'type': 'active', 'message': 'Real-time AI conversation started!'})
        
        return jsonify({'success': True, 'message': 'Optimized orchestrator started'})
        
    except Exception as e:
        print(f"❌ Error starting orchestrator: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/human_audio', methods=['POST'])
def handle_human_audio():
    """Handle human audio input"""
    global orchestrator
    
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        # Read audio data
        audio_data = audio_file.read()
        print(f"🎤 Received human audio: {len(audio_data)} bytes")
        
        if orchestrator:
            # Convert browser audio to PCM16 format for OpenAI Realtime API
            try:
                pcm16_audio = convert_to_pcm16(audio_data)
                print(f"🎤 Converted to PCM16: {len(pcm16_audio)} bytes")
                
                # Send converted audio to orchestrator 
                orchestrator.add_human_audio(pcm16_audio)
                
            except Exception as e:
                print(f"❌ Audio conversion error: {e}")
                # Fallback to text input
                orchestrator.add_human_response("I'd like to join the conversation!")
            
            return jsonify({
                'success': True, 
                'transcription': '[Audio passed directly to AI]',
                'message': 'Human audio passed directly to next persona'
            })
        else:
            return jsonify({'error': 'Orchestrator not active'}), 400
        
    except Exception as e:
        print(f"❌ Error handling human audio: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/stop_orchestrator', methods=['POST'])
def stop_orchestrator():
    """Stop the AI conversation orchestrator"""
    global orchestrator
    
    try:
        if orchestrator:
            orchestrator.stop_conversation()
        
        socketio.emit('status', {'type': 'inactive', 'message': 'Conversation stopped'})
        
        return jsonify({'success': True, 'message': 'Orchestrator stopped'})
        
    except Exception as e:
        print(f"❌ Error stopping orchestrator: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/mo-logo')
def serve_mo_logo():
    """Serve Mo logo image"""
    from flask import send_file
    import os
    
    logo_path = '/home/azureuser/modcast/resources/Mo.png'
    if os.path.exists(logo_path):
        return send_file(logo_path, mimetype='image/png')
    else:
        # Fallback to a simple SVG if image not found
        return '''<svg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg">
            <circle cx="30" cy="30" r="30" fill="#1e293b"/>
            <text x="30" y="38" font-family="Inter, sans-serif" font-size="20" font-weight="bold" 
                  fill="white" text-anchor="middle">Mo</text>
        </svg>''', 200, {'Content-Type': 'image/svg+xml'}

@app.route('/status')
def get_status():
    """Get orchestrator status"""
    global orchestrator
    
    if orchestrator:
        return jsonify(orchestrator.get_conversation_summary())
    else:
        return jsonify({'status': 'not_initialized'})

@socketio.on('alex_showcase')
def handle_alex_showcase(data):
    """Handle Alex showcasing his completed work"""
    global orchestrator, website_showcased
    
    try:
        # Check if Alex has already showcased the website
        if website_showcased:
            print("🚫 Alex has already showcased the website - ignoring duplicate request")
            return
            
        url = data.get('url', '')
        print(f"🎨 Alex showcasing website: {url}")
        
        if orchestrator:
            # Clean up any potential background threads or processes first
            print("🧹 Cleaning up background processes before Alex showcase...")
            
            # Trigger Alex to actually speak about his work using orchestrator
            def alex_showcase_speech():
                import asyncio
                import time
                
                # Wait a moment for website popup to fully stabilize
                time.sleep(1)
                
                # Force stop any other background operations that might interfere
                if hasattr(orchestrator, '_background_threads'):
                    for thread in orchestrator._background_threads:
                        if thread.is_alive():
                            print(f"🛑 Stopping background thread: {thread.name}")
                
                if orchestrator.is_conversation_active():
                    print("🎤 Alex is now ready to showcase the website!")
                    
                    # Set Alex's persona for the showcase
                    alex_persona = None
                    for persona in orchestrator.personas:
                        if persona.name == "Alex":
                            alex_persona = persona
                            break
                    
                    if alex_persona:
                        # Update Alex's instructions for the showcase - ensure he hands to Marcus
                        marcus_index = next((i for i, p in enumerate(orchestrator.personas) if p.name == "Marcus"), 0)
                        showcase_instructions = f"You are Alex, the developer. The website is now live at {url}! Express your pride and excitement about completing the project. Mention 1-2 key features you implemented. Keep it to 2-3 enthusiastic sentences, then call select_next_speaker with speaker_index='{marcus_index}' to hand control to Marcus for his response."
                        alex_persona.instructions = showcase_instructions
                        
                        # Clear any pending speaker selections to avoid conflicts
                        orchestrator.selected_next_speaker = None
                        
                        # Force Alex to speak
                        alex_index = next((i for i, p in enumerate(orchestrator.personas) if p.name == "Alex"), 0)
                        orchestrator.current_persona_index = alex_index
                        orchestrator.current_turn += 1
                        orchestrator.current_speaker = "Alex"
                        orchestrator.is_speaking = True
                        
                        print(f"🎯 Forcing Alex (index {alex_index}) to speak about the completed website")
                        
                        # Create clean async context to run the persona turn
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            loop.run_until_complete(orchestrator._start_persona_turn(f"The website is now live at {url} and ready to showcase!"))
                        except Exception as e:
                            print(f"❌ Error in Alex showcase speech: {e}")
                            # Fallback - emit a simple text response
                            socketio.emit('persona_finished', {
                                'name': 'Alex',
                                'text': f"Perfect! The website is now live at {url}. I've successfully implemented all the features we discussed!"
                            })
                        finally:
                            loop.close()
                else:
                    print("⚠️ Orchestrator is not active for Alex showcase")
            
            # Run Alex's showcase speech in background thread
            import threading
            alex_thread = threading.Thread(target=alex_showcase_speech, daemon=True, name="AlexShowcase")
            alex_thread.start()
            
            print("🚀 Alex showcase thread started successfully")
            
        return {'success': True}
        
    except Exception as e:
        print(f"❌ Error in alex_showcase: {e}")
        return {'error': str(e)}, 500

@socketio.on('website_working_perfectly')
def handle_website_working_perfectly(data):
    """Handle immediate Alex showcase when website is confirmed working"""
    global orchestrator, website_showcased
    
    try:
        # Check if Alex has already showcased the website
        if website_showcased:
            print("🚫 Website already showcased - ignoring duplicate trigger")
            return
            
        url = data.get('url', '')
        print(f"🎯 Website working perfectly confirmed! URL: {url}")
        print("🧹 Aggressively stopping ALL background processes...")
        
        # Kill background threads related to build/dev processes
        import threading
        import subprocess
        import os
        import signal
        
        active_threads = threading.active_count()
        print(f"🧵 Active threads before cleanup: {active_threads}")
        
        # 1. Kill all npm/node processes that might be running
        try:
            print("🔪 Killing npm/node build processes...")
            
            # Try using psutil if available, otherwise use system commands
            try:
                import psutil
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        pinfo = proc.info
                        if pinfo['name'] in ['npm', 'node', 'nodejs'] or \
                           (pinfo['cmdline'] and any('npm' in str(cmd) or 'vite' in str(cmd) or 'dev' in str(cmd) for cmd in pinfo['cmdline'])):
                            print(f"🔪 Killing process: {pinfo['pid']} - {pinfo['name']} - {pinfo['cmdline']}")
                            proc.terminate()
                            try:
                                proc.wait(timeout=2)
                            except psutil.TimeoutExpired:
                                proc.kill()  # Force kill if terminate doesn't work
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
            except ImportError:
                # Fallback to system commands if psutil not available
                print("🔪 psutil not available, using system commands...")
                try:
                    # Kill npm processes
                    subprocess.run(['pkill', '-f', 'npm'], stderr=subprocess.DEVNULL, timeout=5)
                    subprocess.run(['pkill', '-f', 'node.*dev'], stderr=subprocess.DEVNULL, timeout=5)
                    subprocess.run(['pkill', '-f', 'vite'], stderr=subprocess.DEVNULL, timeout=5)
                    print("🔪 System kill commands executed")
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    print("⚠️ System kill commands failed or not available")
                    
        except Exception as e:
            print(f"⚠️ Error killing npm processes: {e}")
        
        # 2. Kill background threads by name pattern  
        try:
            print("🔪 Killing background threads...")
            all_threads = threading.enumerate()
            killed_threads = []
            
            for thread in all_threads:
                thread_name = getattr(thread, 'name', 'Unknown')
                
                # Kill threads related to build processes, but keep essential ones
                should_kill = any(pattern in thread_name.lower() for pattern in [
                    'vibe', 'build', 'npm', 'dev', 'executor', 'subprocess', 'terminal', 'popen'
                ]) and thread != threading.current_thread() and \
                not thread_name.startswith('MainThread') and \
                not thread_name.startswith('Thread-') and \
                'SocketIO' not in thread_name and \
                'Flask' not in thread_name
                
                if should_kill:
                    print(f"🔪 Attempting to stop thread: {thread_name} (daemon={getattr(thread, 'daemon', False)})")
                    killed_threads.append(thread_name)
                    try:
                        # For daemon threads, we can't really stop them safely, but we can try
                        if hasattr(thread, '_stop'):
                            thread._stop()
                        elif hasattr(thread, '_Thread__stop'):
                            thread._Thread__stop()  # Internal Python method
                        elif hasattr(thread, 'terminate'):
                            thread.terminate()
                        
                        # Additional aggressive approach for specific thread types
                        if hasattr(thread, '_target') and thread._target:
                            # Try to interrupt the target function if possible
                            try:
                                thread._target = lambda: None  # Replace target with no-op
                            except:
                                pass
                                
                    except Exception as te:
                        print(f"⚠️ Could not stop thread {thread_name}: {te}")
            
            if killed_threads:
                print(f"🔪 Attempted to kill {len(killed_threads)} threads: {', '.join(killed_threads)}")
            else:
                print("ℹ️ No build-related threads found to kill")
                
        except Exception as e:
            print(f"⚠️ Error killing threads: {e}")
        
        # 3. Clear orchestrator state
        if orchestrator:
            # Clear any pending states
            orchestrator.selected_next_speaker = None
            orchestrator.is_speaking = False
            
            # Set clean state for Alex showcase
            orchestrator.phase = "showcase"
            
            # Stop any orchestrator-specific background processes
            if hasattr(orchestrator, 'is_audio_generating'):
                orchestrator.is_audio_generating = False
            
            print("✅ Orchestrator state cleaned for Alex showcase")
        
        # 4. Kill any processes listening on common dev server ports (aggressive cleanup)
        try:
            print("🔪 Killing processes on dev server ports...")
            import re
            
            # Extract port from URL if possible
            port = 3000  # default
            try:
                port_match = re.search(r':(\d+)', url)
                if port_match:
                    port = int(port_match.group(1))
            except:
                pass
            
            # Kill processes on the dev server port
            for dev_port in [port, 3000, 5173, 8080, 4000]:  # Common dev ports
                try:
                    # Use system commands to kill processes on specific ports
                    subprocess.run(['lsof', '-ti', f':{dev_port}'], 
                                 capture_output=True, text=True, timeout=3)
                    result = subprocess.run(['lsof', '-ti', f':{dev_port}'], 
                                          capture_output=True, text=True, timeout=3)
                    if result.returncode == 0 and result.stdout.strip():
                        pids = result.stdout.strip().split('\n')
                        for pid in pids:
                            if pid.strip():
                                print(f"🔪 Killing process {pid} on port {dev_port}")
                                subprocess.run(['kill', '-9', pid.strip()], 
                                             stderr=subprocess.DEVNULL, timeout=2)
                except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
                    pass  # Command not available or failed
                    
        except Exception as e:
            print(f"⚠️ Error killing port processes: {e}")
        
        # 5. Give processes a moment to die
        import time
        time.sleep(1.0)  # Increased wait time for cleanup
        
        final_threads = threading.active_count()
        print(f"🧵 Active threads after cleanup: {final_threads} (reduced by {active_threads - final_threads})")
        
        # 6. Final verification - list remaining suspicious threads
        remaining_threads = threading.enumerate()
        suspicious = []
        for thread in remaining_threads:
            thread_name = getattr(thread, 'name', 'Unknown')
            if any(pattern in thread_name.lower() for pattern in ['vibe', 'build', 'npm', 'dev', 'executor']):
                suspicious.append(thread_name)
        
        if suspicious:
            print(f"⚠️ Suspicious threads still running: {', '.join(suspicious)}")
        else:
            print("✅ All build-related threads appear to be cleaned up")
        
        # 7. Wait 10 seconds, then trigger Alex showcase
        if orchestrator and orchestrator.is_conversation_active():
            print("⏳ Waiting 10 seconds for website to fully stabilize...")
            time.sleep(10)
            print("🎤 Triggering Alex showcase after 10s wait - website confirmed working!")
            
            # Now set the flag to prevent future duplicates (AFTER Alex actually speaks)
            def delayed_flag_set():
                global website_showcased
                time.sleep(5)  # Wait for Alex to actually start speaking
                website_showcased = True
                print("🔒 Website showcase flag set - no more duplicates allowed")
            
            threading.Thread(target=delayed_flag_set, daemon=True).start()
            handle_alex_showcase(data)
        else:
            print("⚠️ Orchestrator not active - cannot trigger Alex showcase")
            
        return {'success': True}
        
    except Exception as e:
        print(f"❌ Error in website_working_perfectly: {e}")
        return {'error': str(e)}, 500

if __name__ == '__main__':
    print("🚀 MOENTREPRISE - AI BUSINESS AUTOMATION PLATFORM")
    print("🤖 Intelligent team collaboration with real-time execution")
    print("📱 Access: http://localhost:3001")
    print("🎯 Experience: Complete business automation from idea to launch")
    print("💼 Features: Requirements gathering → Development → Marketing automation")
    
    socketio.run(app, host='0.0.0.0', port=3001, debug=True)