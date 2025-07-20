#!/usr/bin/env python3
"""Test script to generate a video using Google Veo API via curl commands."""

import subprocess
import json
import time
import os
import sys

def run_curl_command(cmd):
    """Run a curl command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        print(f"Command: {cmd}")
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        return result
    except subprocess.TimeoutExpired:
        print(f"Command timed out: {cmd}")
        return None
    except Exception as e:
        print(f"Error running command: {e}")
        return None

def generate_video():
    """Generate a promotional video using Google Veo API."""
    
    # Check for required environment variables
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
    if not project_id:
        print("❌ GOOGLE_CLOUD_PROJECT_ID environment variable not set")
        return None
    
    print(f"🎬 Using Google Cloud Project: {project_id}")
    
    # Step 1: Get access token
    print("\n🔑 Getting Google Cloud access token...")
    token_cmd = "gcloud auth print-access-token"
    token_result = run_curl_command(token_cmd)
    
    if not token_result or token_result.returncode != 0:
        print("❌ Failed to get access token")
        return None
    
    access_token = token_result.stdout.strip()
    print(f"✅ Got access token: {access_token[:20]}...")
    
    # Step 2: Prepare video generation request
    video_prompt = "A beautiful promotional video for a flower shop called 'Le Fleur'. Show vibrant colorful flowers, elegant bouquets, and a cozy shop atmosphere. Include text overlay: 'Fête d'Anne - 30% off all bouquets'. Professional, warm lighting, 8 seconds duration."
    
    request_data = {
        "prompt": video_prompt,
        "config": {
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.9,
                "topK": 40,
                "maxOutputTokens": 2048
            }
        }
    }
    
    # Step 3: Generate video
    print(f"\n🎥 Generating video with prompt: {video_prompt[:100]}...")
    
    generate_url = f"https://aiplatform.googleapis.com/v1/projects/{project_id}/locations/us-central1/publishers/google/models/veo-001:generateContent"
    
    generate_cmd = f'''curl -X POST \\
  -H "Authorization: Bearer {access_token}" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(request_data)}' \\
  "{generate_url}"'''
    
    generate_result = run_curl_command(generate_cmd)
    
    if not generate_result or generate_result.returncode != 0:
        print("❌ Failed to generate video")
        return None
    
    try:
        response_data = json.loads(generate_result.stdout)
        print(f"✅ Video generation response: {json.dumps(response_data, indent=2)}")
        
        # Check if we got a video URL or need to poll for completion
        if 'candidates' in response_data and response_data['candidates']:
            candidate = response_data['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                for part in candidate['content']['parts']:
                    if 'fileData' in part:
                        video_uri = part['fileData'].get('fileUri')
                        if video_uri:
                            print(f"🎉 Video generated successfully: {video_uri}")
                            return video_uri
        
        # If no immediate result, check for operation ID for polling
        if 'name' in response_data:
            operation_id = response_data['name']
            print(f"🔄 Video generation started, operation ID: {operation_id}")
            return poll_for_video_completion(access_token, operation_id)
        
        print("❓ Unexpected response format")
        return None
        
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse response JSON: {e}")
        print(f"Raw response: {generate_result.stdout}")
        return None

def poll_for_video_completion(access_token, operation_id):
    """Poll for video generation completion."""
    
    print(f"\n⏳ Polling for video completion...")
    max_attempts = 30  # 5 minutes with 10-second intervals
    
    for attempt in range(max_attempts):
        print(f"🔄 Polling attempt {attempt + 1}/{max_attempts}...")
        
        poll_cmd = f'''curl -X GET \\
  -H "Authorization: Bearer {access_token}" \\
  "{operation_id}"'''
        
        poll_result = run_curl_command(poll_cmd)
        
        if not poll_result or poll_result.returncode != 0:
            print(f"❌ Polling failed on attempt {attempt + 1}")
            continue
        
        try:
            response_data = json.loads(poll_result.stdout)
            
            if response_data.get('done', False):
                print("✅ Video generation completed!")
                
                if 'response' in response_data:
                    video_response = response_data['response']
                    if 'candidates' in video_response:
                        for candidate in video_response['candidates']:
                            if 'content' in candidate and 'parts' in candidate['content']:
                                for part in candidate['content']['parts']:
                                    if 'fileData' in part:
                                        video_uri = part['fileData'].get('fileUri')
                                        if video_uri:
                                            print(f"🎉 Video URI: {video_uri}")
                                            return video_uri
                
                print("❓ Video completed but no URI found")
                return None
            
            else:
                print(f"⏳ Still generating... (attempt {attempt + 1})")
                time.sleep(10)  # Wait 10 seconds before next poll
        
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse polling response: {e}")
            continue
    
    print("❌ Video generation timed out")
    return None

def main():
    """Main function to test video generation."""
    print("🎬 Testing Google Veo video generation...")
    
    video_uri = generate_video()
    
    if video_uri:
        print(f"\n🎉 SUCCESS: Video generated at {video_uri}")
        
        # Try to download the video
        print("\n📥 Attempting to download video...")
        download_cmd = f"curl -o test_video.mp4 '{video_uri}'"
        download_result = run_curl_command(download_cmd)
        
        if download_result and download_result.returncode == 0:
            print("✅ Video downloaded as test_video.mp4")
        else:
            print("❌ Failed to download video")
    else:
        print("\n❌ FAILED: Could not generate video")

if __name__ == "__main__":
    main() 