#!/usr/bin/env python3
"""Simple test script to test Google Veo API calls using curl."""

import subprocess
import json
import os

def test_veo_api():
    """Test Google Veo API with curl commands."""
    
    print("🎬 Testing Google Veo API with curl...")
    
    # For testing purposes, let's use a test project ID
    # In production, this should come from environment variables
    project_id = "test-project-12345"  # Replace with actual project ID
    
    # Test 1: Try to get an access token (this will likely fail without proper auth)
    print("\n🔑 Test 1: Attempting to get access token...")
    
    # Method 1: Try using service account key if available
    service_account_key = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if service_account_key and os.path.exists(service_account_key):
        print(f"📋 Found service account key: {service_account_key}")
        
        token_cmd = f"""curl -s -X POST https://oauth2.googleapis.com/token \\
            -H "Content-Type: application/x-www-form-urlencoded" \\
            -d "grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=$(python3 -c "
import jwt
import json
import time
from pathlib import Path

# Load service account key
with open('{service_account_key}') as f:
    key_data = json.load(f)

# Create JWT
now = int(time.time())
payload = {{
    'iss': key_data['client_email'],
    'scope': 'https://www.googleapis.com/auth/cloud-platform',
    'aud': 'https://oauth2.googleapis.com/token',
    'iat': now,
    'exp': now + 3600
}}

token = jwt.encode(payload, key_data['private_key'], algorithm='RS256')
print(token)
")" """
        
        print("🔧 Attempting service account authentication...")
        print(f"Command: {token_cmd[:100]}...")
        
    else:
        print("❌ No service account key found")
        print("💡 Let's try a direct API call to see the error response...")
        
        # Test 2: Try direct API call without auth to see what happens
        video_prompt = "A beautiful flower shop promotional video"
        
        request_data = {
            "contents": [{
                "parts": [{
                    "text": video_prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.9,
                "topK": 40,
                "maxOutputTokens": 2048
            }
        }
        
        api_url = f"https://aiplatform.googleapis.com/v1/projects/{project_id}/locations/us-central1/publishers/google/models/veo-001:generateContent"
        
        test_cmd = f"""curl -s -X POST \\
            -H "Content-Type: application/json" \\
            -d '{json.dumps(request_data)}' \\
            "{api_url}" """
        
        print(f"\n🧪 Test API call without authentication:")
        print(f"URL: {api_url}")
        print(f"Payload: {json.dumps(request_data, indent=2)}")
        
        try:
            result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True, timeout=30)
            print(f"\n📤 Response Status: {result.returncode}")
            print(f"📥 Response Body: {result.stdout}")
            if result.stderr:
                print(f"⚠️  STDERR: {result.stderr}")
                
            # Try to parse JSON response
            if result.stdout:
                try:
                    response_json = json.loads(result.stdout)
                    print(f"\n📋 Parsed Response:")
                    print(json.dumps(response_json, indent=2))
                except json.JSONDecodeError:
                    print("❌ Response is not valid JSON")
                    
        except subprocess.TimeoutExpired:
            print("⏰ Request timed out")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test 3: Show what the correct curl command should look like
    print(f"\n💡 For reference, the correct authenticated curl command would be:")
    print(f"""
curl -X POST \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "contents": [{{
      "parts": [{{
        "text": "A beautiful promotional video for a flower shop called Le Fleur. Show vibrant colorful flowers, elegant bouquets, and a cozy shop atmosphere. Include text overlay: Fête d\\'Anne - 30% off all bouquets. Professional, warm lighting, 8 seconds duration."
      }}]
    }}],
    "generationConfig": {{
      "temperature": 0.7,
      "topP": 0.9,
      "topK": 40,
      "maxOutputTokens": 2048
    }}
  }}' \\
  "https://aiplatform.googleapis.com/v1/projects/YOUR_PROJECT_ID/locations/us-central1/publishers/google/models/veo-001:generateContent"
""")

if __name__ == "__main__":
    test_veo_api() 