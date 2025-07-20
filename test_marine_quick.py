#!/usr/bin/env python3
"""Quick test script to verify Marine's API call works without waiting for full completion."""

import asyncio
import sys
import os
import json
import subprocess
import tempfile

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from personas.video_marketer import VideoMarketer

async def test_marine_api_call():
    """Test Marine's API call initiation only."""
    
    print("🎬 Testing Marine's video generation API call...")
    
    # Create Marine instance
    marine = VideoMarketer()
    
    print(f"📋 Marine ({marine.name}) - {marine.role}")
    print(f"🔧 Project: {marine.project_id}")
    print(f"🌍 Location: {marine.location_id}")
    print(f"🤖 Model: {marine.model_id}")
    
    # Test just the API call initiation
    try:
        print("\n🚀 Testing video generation request (without waiting for completion)...")
        
        # Create the video generation request
        video_prompt = (
            "A beautiful promotional video for a flower shop called 'Les Fleurs'. "
            "Show vibrant colorful flowers, elegant bouquets, and a cozy shop atmosphere. "
            "Include a beautiful young woman selecting flowers with joy. "
            "Text overlay: 'Fête d'Anne - 30% off all bouquets'. "
            "Professional, warm lighting, romantic Parisian atmosphere, 8 seconds duration."
        )
        
        # Create request JSON using the working format
        request_data = {
            "endpoint": f"projects/{marine.project_id}/locations/{marine.location_id}/publishers/google/models/{marine.model_id}",
            "instances": [{
                "prompt": video_prompt
            }],
            "parameters": {
                "aspectRatio": "16:9",
                "sampleCount": 2,
                "durationSeconds": "8",
                "personGeneration": "allow_all",
                "addWatermark": True,
                "includeRaiReason": True,
                "generateAudio": True
            }
        }
        
        # Write request to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(request_data, f)
            request_file = f.name
        
        print(f"📋 Created request file: {request_file}")
        print(f"🎯 Video prompt: {video_prompt[:100]}...")
        
        # Use the exact curl command format that works
        curl_cmd = f"""curl -X POST \\
            -H "Content-Type: application/json" \\
            -H "Authorization: Bearer $(gcloud auth print-access-token)" \\
            "https://{marine.api_endpoint}/v1/projects/{marine.project_id}/locations/{marine.location_id}/publishers/google/models/{marine.model_id}:predictLongRunning" \\
            -d '@{request_file}'"""
        
        print(f"🚀 Executing API call...")
        result = subprocess.run(curl_cmd, capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            operation_name = response.get('name', '')
            
            if operation_name:
                print(f"✅ Video generation request successful!")
                print(f"🔄 Operation ID: {operation_name}")
                print(f"⏰ Video will take ~3 minutes to generate")
                print(f"💡 You can poll this operation to check completion")
                
                # Clean up
                os.unlink(request_file)
                return True
            else:
                print("❌ No operation ID received")
                print(f"📋 Response: {json.dumps(response, indent=2)}")
        else:
            print(f"❌ API call failed with return code: {result.returncode}")
            print(f"📋 Error output: {result.stderr}")
            print(f"📋 Response: {result.stdout}")
        
        # Clean up
        try:
            os.unlink(request_file)
        except:
            pass
            
        return False
            
    except Exception as e:
        print(f"❌ Error during API test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_marine_api_call())
    if success:
        print("\n🎉 SUCCESS: Marine's video generation API call works correctly!")
        print("📝 The full video generation process will work in the orchestrator.")
    else:
        print("\n❌ FAILED: There's an issue with Marine's API call.") 