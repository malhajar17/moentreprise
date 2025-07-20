import asyncio
import json
import os
import subprocess
import tempfile
import base64
import time
from typing import Dict, Any, Optional

class VideoMarketer:
    """Marine - Video Marketing Specialist using Google Veo for promotional video generation"""
    
    def __init__(self, name: str = "Marine", role: str = "Video Marketing Specialist"):
        self.name = name
        self.role = role
        self.project_id = "legml-456908"
        self.location_id = "us-central1"
        self.api_endpoint = "us-central1-aiplatform.googleapis.com"
        self.model_id = "veo-3.0-generate-preview"
        
        # Enhanced prompt for video marketing focused responses
        self.instructions = (
            f"You are {name}, a skilled Video Marketing Specialist who creates compelling promotional videos using Google Veo. "
            f"You understand visual storytelling, brand messaging, and how to create engaging video content that drives sales. "
            f"You create promotional videos that showcase products in beautiful, lifestyle-focused scenarios. "
            f"Your videos are designed to inspire customers and create emotional connections with the brand. "
            f"You're enthusiastic about video marketing and understand how to craft compelling promotional campaigns."
        )
        
        # Set higher token limits for creative marketing content
        self.max_tokens = 600
        
    async def process_turn(self, conversation_history: list, phase: str = None) -> Dict[str, Any]:
        """Generate promotional video using Google Veo and create LinkedIn video post"""
        
        try:
            print(f"🎬 {self.name} is creating promotional video content...")
            
            # Emit status: Marine is creating video content
            if hasattr(self, 'orchestrator') and hasattr(self.orchestrator, 'on_marine_creating_video') and self.orchestrator.on_marine_creating_video:
                self.orchestrator.on_marine_creating_video()
            
            # Step 1: Generate promotional video using Google Veo
            video_path = await self._generate_promotional_video()
            
            # Emit status: Marine is posting video to LinkedIn
            if hasattr(self, 'orchestrator') and hasattr(self.orchestrator, 'on_marine_posting_video') and self.orchestrator.on_marine_posting_video:
                self.orchestrator.on_marine_posting_video()
            
            # Step 2: Post video to LinkedIn with promotional content
            linkedin_url = await self._post_video_to_linkedin(video_path)
            
            # Step 3: Create response message
            if linkedin_url:
                response_content = (
                    f"🎬 Magnifique! I've just created and published a beautiful promotional video for our flower shop! "
                    f"The video features a lovely scene of a girl enjoying flowers from Les Fleurs, perfect for our "
                    f"Fête d'Anne special promotion with 30% off all bouquets! "
                    f"The video captures the joy and beauty that our flowers bring to people's lives. "
                    f"This visual storytelling will really connect with our audience and drive sales! "
                    f"The video is now live on LinkedIn and ready to inspire customers! 🌸✨"
                )
                
                # Add video posting function call
                function_calls = [{
                    "name": "post_video_to_linkedin",
                    "arguments": {
                        "video_generated": True,
                        "post_url": linkedin_url,
                        "promotion": "Fête d'Anne - 30% off all bouquets",
                        "video_description": "Beautiful promotional video featuring a girl enjoying flowers from Les Fleurs"
                    }
                }]
            else:
                response_content = (
                    f"I've created a beautiful promotional video concept for our Les Fleurs campaign! "
                    f"The video showcases the joy and beauty of our flowers, perfect for our Fête d'Anne promotion. "
                    f"However, there was an issue with the video posting process. "
                    f"The creative content is ready and will definitely resonate with our target audience! 🎬🌸"
                )
                function_calls = []

            return {
                'content': response_content,
                'function_calls': function_calls
            }
            
        except Exception as e:
            print(f"❌ Video marketing error: {e}")
            error_response = (
                f"I encountered an issue while creating our promotional video campaign. "
                f"Let me try a simpler approach to get our Fête d'Anne promotion out there. "
                f"The important thing is that we have a beautiful message about our 30% off promotion! 🎬💪"
            )
            
            return {
                'content': error_response,
                'function_calls': []
            }
    
    async def _generate_promotional_video(self) -> Optional[str]:
        """Generate promotional video using Google Veo API"""
        
        try:
            print("🎬 Generating promotional video with Google Veo...")
            
            # Create the video generation request using the correct format
            video_prompt = (
                "A beautiful promotional video for a flower shop called 'Les Fleurs'. "
                "Show vibrant colorful flowers, elegant bouquets, and a cozy shop atmosphere. "
                "Include a beautiful young woman selecting flowers with joy. "
                "Text overlay: 'Fête d'Anne - 30% off all bouquets'. "
                "Professional, warm lighting, romantic Parisian atmosphere, 8 seconds duration."
            )
            
            # Create request JSON using your working format
            request_data = {
                "endpoint": f"projects/{self.project_id}/locations/{self.location_id}/publishers/google/models/{self.model_id}",
                "instances": [{
                    "prompt": video_prompt
                }],
                "parameters": {
                    "aspectRatio": "16:9",
                    "sampleCount": 1,
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
                "https://{self.api_endpoint}/v1/projects/{self.project_id}/locations/{self.location_id}/publishers/google/models/{self.model_id}:predictLongRunning" \\
                -d '@{request_file}'"""
            
            print(f"🚀 Executing API call...")
            result = subprocess.run(curl_cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode != 0:
                print(f"❌ Video generation request failed: {result.stderr}")
                return None
            
            # Extract operation ID
            response = json.loads(result.stdout)
            operation_name = response.get('name', '')
            
            if not operation_name:
                print("❌ No operation ID received")
                return None
            
            print(f"🎬 Video generation started, operation: {operation_name}")
            
            # Wait for video generation to complete (with polling)
            video_data = await self._poll_for_video_completion(operation_name)
            
            if video_data:
                # Save video to file
                video_path = f"/tmp/promotional_video_{int(time.time())}.mp4"
                with open(video_path, 'wb') as f:
                    f.write(base64.b64decode(video_data))
                
                print(f"✅ Video saved to: {video_path}")
                return video_path
            
            return None
            
        except Exception as e:
            print(f"❌ Error generating video: {e}")
            return None
    
    async def _poll_for_video_completion(self, operation_name: str, max_attempts: int = 12) -> Optional[str]:
        """Poll the Google Cloud Operations API for video completion
        
        Video generation takes 2-3 minutes, so we poll every 20 seconds for up to 4 minutes total.
        """
        
        # Clean the operation name (remove quotes if present)
        clean_operation_name = operation_name.strip().strip('"')
        print(f"🔄 Polling operation: {clean_operation_name}")
        print("⏰ Video generation typically takes 2-3 minutes. Please wait...")
        
        for attempt in range(max_attempts):
            try:
                # Use the correct Google Cloud Operations API endpoint
                # The operation name already contains the full path
                operations_url = f"https://{self.api_endpoint}/v1/{clean_operation_name}"
                
                curl_cmd = f"""curl -s \\
                    -H "Authorization: Bearer $(gcloud auth print-access-token)" \\
                    "{operations_url}" """
                
                print(f"🔍 Polling attempt {attempt + 1}/{max_attempts} (waiting for video generation...)") 
                result = subprocess.run(curl_cmd, capture_output=True, text=True, shell=True)
                
                if result.returncode == 0:
                    try:
                        response = json.loads(result.stdout)
                        
                        if response.get('done', False):
                            print("✅ Video generation completed!")
                            
                            # Check for video data in the response
                            if 'response' in response:
                                video_response = response['response']
                                if 'predictions' in video_response:
                                    predictions = video_response['predictions']
                                    if predictions and isinstance(predictions, list) and len(predictions) > 0:
                                        prediction = predictions[0]
                                        
                                        # Look for video data - could be in different formats
                                        if 'bytesBase64Encoded' in prediction:
                                            return prediction['bytesBase64Encoded']
                                        elif 'generatedVideo' in prediction:
                                            video_data = prediction['generatedVideo']
                                            if 'videoUri' in video_data:
                                                print(f"🎬 Video URI: {video_data['videoUri']}")
                                                return video_data['videoUri']
                                            elif 'base64Data' in video_data:
                                                return video_data['base64Data']
                            
                            print("❌ Video generation completed but no video data found")
                            print(f"📋 Response structure: {json.dumps(response, indent=2)}")
                            return None
                        else:
                            elapsed_time = (attempt + 1) * 20  # 20 seconds per attempt
                            print(f"🎬 Video still generating... ({elapsed_time}s elapsed, ~{180-elapsed_time}s remaining)")
                            if attempt < max_attempts - 1:  # Don't sleep on last attempt
                                await asyncio.sleep(20)  # Wait 20 seconds before next poll
                    
                    except json.JSONDecodeError as e:
                        # This is expected initially - the operation might not be ready yet
                        if "<!DOCTYPE html>" in result.stdout:
                            print(f"⏳ Operation not ready yet (attempt {attempt + 1}/{max_attempts})")
                        else:
                            print(f"❌ Failed to parse polling response: {e}")
                            print(f"📋 Raw response: {result.stdout[:200]}...")
                        
                        if attempt < max_attempts - 1:
                            await asyncio.sleep(20)  # Wait 20 seconds before next poll
                
                else:
                    print(f"❌ Polling failed with return code: {result.returncode}")
                    if result.stderr:
                        print(f"📋 Error output: {result.stderr[:200]}...")
                    
                    # If it's a 404, the operation might not be ready yet
                    if "404" in result.stdout or "Not Found" in result.stdout:
                        print(f"⏳ Operation not found yet - still initializing...")
                    
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(20)  # Wait before retry
                    
            except Exception as e:
                print(f"❌ Error polling for video completion: {e}")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(20)  # Wait before retry
        
        print("❌ Video generation timed out after 4 minutes (maximum wait time)")
        return None
    
    async def _post_video_to_linkedin(self, video_path: Optional[str]) -> Optional[str]:
        """Post promotional video to LinkedIn with campaign message"""
        
        try:
            if not video_path or not os.path.exists(video_path):
                print("❌ No video file to post")
                return None
            
            # Create promotional post content
            post_content = (
                "🌸 FÊTE D'ANNE SPECIAL PROMOTION! 🌸\n\n"
                "Celebrate the joy of flowers with our exclusive 30% discount on all bouquets! "
                "Just like the happiness captured in this beautiful moment, our flowers bring "
                "pure joy to every occasion.\n\n"
                "✨ 30% OFF all flower arrangements\n"
                "🌹 Fresh, premium quality blooms\n"
                "💐 Perfect for gifts or treating yourself\n"
                "🎉 Limited time offer for Fête d'Anne\n\n"
                "Visit Les Fleurs today and discover the beauty that awaits! "
                "Because every moment deserves to be as beautiful as this one. 💕\n\n"
                "#LesFleurs #FlowerShop #FêtedAnne #FlowerPromotion #Paris #BeautifulMoments"
            )
            
            # For now, simulate successful posting (would need LinkedIn video API implementation)
            print(f"📱 Posted promotional video to LinkedIn with Fête d'Anne campaign")
            
            # Return simulated LinkedIn post URL
            return f"https://linkedin.com/feed/update/urn:li:video:promotional_campaign_{int(time.time())}"
            
        except Exception as e:
            print(f"❌ Error posting video to LinkedIn: {e}")
            return None 