#!/usr/bin/env python3
"""
Port Cleaner Script
Kills all processes running on commonly used ports before starting the AI orchestrator
"""

import subprocess
import os
import sys

def kill_port(port):
    """Kill processes running on the specified port"""
    try:
        # Find process using the port
        result = subprocess.run(
            ['lsof', '-ti', f':{port}'], 
            capture_output=True, 
            text=True, 
            check=False
        )
        
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    print(f"🔥 Killing process {pid} on port {port}")
                    subprocess.run(['kill', '-9', pid], check=False)
            return True
        else:
            print(f"✅ Port {port} is already free")
            return False
            
    except Exception as e:
        print(f"❌ Error clearing port {port}: {e}")
        return False

def kill_nodejs_processes():
    """Kill all node.js processes"""
    try:
        print("🔥 Killing all Node.js processes...")
        subprocess.run(['pkill', '-f', 'node'], check=False)
        subprocess.run(['pkill', '-f', 'npm'], check=False)
        subprocess.run(['pkill', '-f', 'vite'], check=False)
        return True
    except Exception as e:
        print(f"❌ Error killing Node.js processes: {e}")
        return False

def kill_browser_processes():
    """Kill browser processes that might be hanging"""
    try:
        print("🔥 Killing browser processes...")
        subprocess.run(['pkill', '-f', 'chromium'], check=False)
        subprocess.run(['pkill', '-f', 'chrome'], check=False)
        subprocess.run(['pkill', '-f', 'playwright'], check=False)
        return True
    except Exception as e:
        print(f"❌ Error killing browser processes: {e}")
        return False

def main():
    print("🧹 Clearing all ports and processes before starting...")
    print("=" * 50)
    
    # Common ports used by the system
    ports_to_clear = [
        3001,  # Flask web demo
        3000,  # React/Vite dev server
        3002,  # Alt dev server
        3003,  # Alt web server
        3004,  # Alt web server
        3005,  # WebSocket server
        3006,  # Vite default port
        3007,  # Alt React port
    ]
    
    # Clear ports
    for port in ports_to_clear:
        kill_port(port)
    
    print()
    
    # Kill specific process types
    kill_nodejs_processes()
    kill_browser_processes()
    
    print()
    print("✅ Port and process cleanup complete!")
    print("🚀 Ready to start the AI orchestrator system")
    print()
    print("💡 Next steps:")
    print("   cd examples")
    print("   python web_demo.py")

if __name__ == "__main__":
    main() 