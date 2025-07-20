#!/usr/bin/env python3
"""Test script to verify Marine's video generation functionality."""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from personas.video_marketer import VideoMarketer

async def test_marine_video_generation():
    """Test Marine's video generation process."""
    
    print("🎬 Testing Marine's video generation...")
    
    # Create Marine instance
    marine = VideoMarketer()
    
    # Test video generation
    print(f"📋 Marine ({marine.name}) - {marine.role}")
    print(f"🔧 Project: {marine.project_id}")
    print(f"🌍 Location: {marine.location_id}")
    print(f"🤖 Model: {marine.model_id}")
    
    # Test the video generation method directly
    try:
        print("\n🚀 Starting video generation test...")
        video_result = await marine._generate_promotional_video()
        
        if video_result:
            print(f"✅ Video generation successful!")
            print(f"📹 Result type: {type(video_result)}")
            if isinstance(video_result, str):
                if video_result.startswith('http'):
                    print(f"🔗 Video URL: {video_result}")
                else:
                    print(f"📊 Video data length: {len(video_result)} characters")
            else:
                print(f"📋 Video result: {video_result}")
        else:
            print("❌ Video generation failed - no result returned")
            
    except Exception as e:
        print(f"❌ Error during video generation: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🏁 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_marine_video_generation()) 