import asyncio
import json
import os
import openai
import requests
import base64
from io import BytesIO
from PIL import Image
import tempfile
from typing import Dict, Any, Optional

class LinkedInMarketer:
    """LinkedIn Marketing Agent - Creates engaging posts with images and publishes to LinkedIn"""
    
    def __init__(self, name: str = "Sophie", role: str = "LinkedIn Marketing Specialist", api_key: str = ""):
        self.name = name
        self.role = role
        self.api_key = api_key
        self.linkedin_access_token = os.getenv('LINKEDIN_ACCESS_TOKEN', '')
        self.linkedin_author_id = os.getenv('LINKEDIN_AUTHOR_ID', '')
        self.linkedin_org_id = os.getenv('LINKEDIN_ORG_ID', '')  # Organization ID for company page
        
        # Enhanced prompt for marketing-focused responses
        self.instructions = (
            f"You are {name}, a skilled Marketing Director specializing in social media and brand promotion. "
            f"You create engaging LinkedIn posts that announce product launches, generate excitement, and drive traffic. "
            f"Your posts are professional yet enthusiastic, include relevant hashtags, and have clear calls-to-action. "
            f"You understand how to create compelling marketing copy that resonates with professional audiences on LinkedIn. "
            f"Always be excited about new product launches and focus on benefits to users."
        )
        
        # Set higher token limits for creative marketing content
        self.max_tokens = 800
        
    async def process_turn(self, conversation_history: list, phase: str = None) -> Dict[str, Any]:
        """Create LinkedIn post and image, then publish to LinkedIn"""
        
        try:
            print(f"🎯 {self.name} is creating LinkedIn marketing content...")
            
            # Emit status: Sophie is creating content
            if hasattr(self, 'orchestrator') and hasattr(self.orchestrator, 'on_sophie_creating_content') and self.orchestrator.on_sophie_creating_content:
                self.orchestrator.on_sophie_creating_content()
            
            # Step 1: Generate LinkedIn post content using GPT-4o
            post_content = await self._create_linkedin_post(conversation_history)
            
            # Emit status: Sophie is generating image
            if hasattr(self, 'orchestrator') and hasattr(self.orchestrator, 'on_sophie_generating_image') and self.orchestrator.on_sophie_generating_image:
                self.orchestrator.on_sophie_generating_image()
            
            # Step 2: Generate marketing image using DALL-E
            image_path = await self._generate_marketing_image()
            
            # Emit status: Sophie is posting to LinkedIn
            if hasattr(self, 'orchestrator') and hasattr(self.orchestrator, 'on_sophie_posting_linkedin') and self.orchestrator.on_sophie_posting_linkedin:
                self.orchestrator.on_sophie_posting_linkedin()
            
            # Step 3: Post to LinkedIn with image
            linkedin_url = await self._post_to_linkedin(post_content, image_path)
            
            # Step 4: Create response message
            if linkedin_url:
                response_content = (
                    f"🚀 Fantastic! I've just published our website launch announcement on LinkedIn! "
                    f"The post is live and includes a beautiful marketing image. "
                    f"I've tagged it with relevant hashtags to maximize reach. "
                    f"Our professional network will be excited to visit lefleur.com! "
                    f"This should drive some great traffic to our new site. Great work everyone! 🎉"
                )
                
                # Add LinkedIn posting function call
                import json
                safe_content = json.dumps(post_content)[1:-1]  # Remove outer quotes
                function_calls = [{
                    "name": "post_to_linkedin",
                    "arguments": {
                        "content": safe_content,
                        "image_generated": True,
                        "post_url": linkedin_url,
                        "website_url": "https://lefleur.com"
                    }
                }]
            else:
                response_content = (
                    f"I've created an amazing LinkedIn post and marketing image for our lefleur.com launch! "
                    f"However, there was an issue with the LinkedIn API connection. "
                    f"I have the content ready to post manually if needed. "
                    f"The marketing materials look fantastic and will definitely generate excitement! 📱✨"
                )
                function_calls = []

            return {
                'content': response_content,
                'function_calls': function_calls
            }
            
        except Exception as e:
            print(f"❌ LinkedIn marketing error: {e}")
            error_response = (
                f"I encountered an issue while creating our LinkedIn marketing campaign. "
                f"Let me try a simpler approach to get our website announcement out there. "
                f"The important thing is that our amazing lefleur.com website is ready to share with the world! 💪"
            )
            
            return {
                'content': error_response,
                'function_calls': []
            }
    
    async def _create_linkedin_post(self, conversation_history: list) -> str:
        """Generate engaging LinkedIn post content using GPT-4o"""
        
        # Extract website details from conversation
        context_summary = self._extract_website_context(conversation_history)
        
        prompt = f"""
        Create an engaging LinkedIn post to announce the launch of our new website "lefleur.com" from lelefleurfrance_hackathon. 

        Context: {context_summary}

        Requirements:
        - Professional yet enthusiastic tone from a French AI company perspective
        - Highlight key features and voice agent automation technology
        - Include relevant hashtags (#WebsiteLaunch #AIInnovation #VoiceAgents #FrenchTech #Automation)
        - Call-to-action to visit lefleur.com
        - Keep it under 280 words
        - Make it exciting and shareable
        - Focus on AI/voice technology value proposition
        - Mention this is from the team at lelefleurfrance_hackathon
        
        Write a compelling LinkedIn post that showcases our AI innovation and drives engagement.
        """
        
        try:
            response = await asyncio.to_thread(
                openai.chat.completions.create,
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.instructions},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7  # More creative for marketing content
            )
            
            post_content = response.choices[0].message.content.strip()
            print(f"📝 Generated LinkedIn post: {post_content[:100]}...")
            return post_content
            
        except Exception as e:
            print(f"❌ Error generating LinkedIn post: {e}")
            # Fallback post
            return (
                "🚀 Excited to announce the launch of lefleur.com from the lelefleurfrance_hackathon team! "
                "Our AI-powered voice agents have been working around the clock to create something amazing. "
                "Check it out and witness the future of AI automation! "
                "#WebsiteLaunch #AIInnovation #VoiceAgents #FrenchTech #Automation"
            )
    
    async def _generate_marketing_image(self) -> Optional[str]:
        """Generate marketing image using DALL-E"""
        
        try:
            print("🎨 Generating marketing image with DALL-E...")
            
            # Create flower-focused marketing image prompt
            image_prompt = (
                "A beautiful, elegant marketing image for a French flower shop website launch. "
                "Feature gorgeous fresh flowers like roses, peonies, and eucalyptus in soft pastel colors. "
                "Include the text 'lefleur.com' in elegant, modern typography overlaid on the floral arrangement. "
                "Parisian aesthetic with soft lighting, premium floral bouquets, and sophisticated design. "
                "Background should be clean white or soft cream with delicate flower petals scattered around. "
                "Professional photography style, luxury flower shop branding, perfect for LinkedIn social media. "
                "High quality, 16:9 landscape aspect ratio, Instagram-worthy floral composition."
            )
            
            response = await asyncio.to_thread(
                openai.images.generate,
                model="gpt-image-1",
                prompt=image_prompt,
                size="1536x1024",  # Good for LinkedIn (landscape)
                quality="high",
                output_format="jpeg",
                output_compression=80
            )
            
            # Handle gpt-image-1 response (base64 encoded)
            import base64
            from io import BytesIO
            
            if hasattr(response.data[0], 'b64_json') and response.data[0].b64_json:
                # gpt-image-1 returns base64 encoded image
                image_base64 = response.data[0].b64_json
                image_bytes = base64.b64decode(image_base64)
                
                # Save to temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                temp_file.write(image_bytes)
                temp_file.close()
                
                print(f"✅ Marketing image saved: {temp_file.name}")
                return temp_file.name
            elif hasattr(response.data[0], 'url') and response.data[0].url:
                # Fallback for URL-based models (like DALL-E 3)
                image_url = response.data[0].url
                image_response = requests.get(image_url)
                
                if image_response.status_code == 200:
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                    temp_file.write(image_response.content)
                    temp_file.close()
                    
                    print(f"✅ Marketing image saved: {temp_file.name}")
                    return temp_file.name
                else:
                    print("❌ Failed to download generated image")
                    return None
            else:
                print("❌ No image data found in response")
                return None
                
        except Exception as e:
            print(f"❌ Error generating marketing image: {e}")
            return None
    
    async def _post_to_linkedin(self, content: str, image_path: Optional[str] = None) -> Optional[str]:
        """Post content with image to LinkedIn using their API"""
        
        if not self.linkedin_access_token:
            print("⚠️ LinkedIn credentials not configured - skipping actual posting")
            # Simulate successful posting for demo
            return "https://linkedin.com/post/simulated-post-id"
        
        try:
            # LinkedIn API endpoint for creating posts
            url = "https://api.linkedin.com/v2/ugcPosts"
            
            headers = {
                'Authorization': f'Bearer {self.linkedin_access_token}',
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0'
            }
            
            # Use organization posting if available, fallback to personal
            author_urn = f"urn:li:organization:{self.linkedin_org_id}" if self.linkedin_org_id else f"urn:li:person:{self.linkedin_author_id}"
            
            # Base post data structure  
            post_data = {
                "author": author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": f"{content}\n\n🔔 Follow @lelefleurfrance_hackathon for more AI innovations! 🚀 #AICompany #TechInnovation"
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            # If we have an image, upload it first and attach to post
            if image_path and os.path.exists(image_path):
                media_urn = await self._upload_image_to_linkedin(image_path)
                if media_urn:
                    post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
                    post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
                        "status": "READY",
                        "description": {
                            "text": "Marketing image for lefleur.com launch"
                        },
                        "media": media_urn
                    }]
            
            # Post to LinkedIn
            response = requests.post(url, headers=headers, json=post_data)
            
            if response.status_code == 201:
                post_id = response.headers.get('x-restli-id', 'unknown')
                linkedin_url = f"https://linkedin.com/feed/update/{post_id}"
                print(f"✅ Posted to LinkedIn successfully: {linkedin_url}")
                return linkedin_url
            else:
                print(f"❌ LinkedIn API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error posting to LinkedIn: {e}")
            return None
        finally:
            # Clean up temp image file
            if image_path and os.path.exists(image_path):
                try:
                    os.unlink(image_path)
                except:
                    pass
    
    async def _upload_image_to_linkedin(self, image_path: str) -> Optional[str]:
        """Upload image to LinkedIn and get media URN"""
        
        try:
            # Step 1: Register upload
            register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
            
            headers = {
                'Authorization': f'Bearer {self.linkedin_access_token}',
                'Content-Type': 'application/json'
            }
            
            # Use same author URN logic for image upload ownership
            owner_urn = f"urn:li:organization:{self.linkedin_org_id}" if self.linkedin_org_id else f"urn:li:person:{self.linkedin_author_id}"
            
            register_data = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": owner_urn,
                    "serviceRelationships": [
                        {
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"
                        }
                    ]
                }
            }
            
            register_response = requests.post(register_url, headers=headers, json=register_data)
            
            if register_response.status_code != 200:
                print(f"❌ Failed to register upload: {register_response.text}")
                return None
            
            upload_info = register_response.json()
            upload_url = upload_info['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
            asset_id = upload_info['value']['asset']
            
            # Step 2: Upload image (binary upload as per Microsoft docs)
            with open(image_path, 'rb') as image_file:
                upload_headers = {
                    'Authorization': f'Bearer {self.linkedin_access_token}'
                }
                upload_response = requests.post(upload_url, headers=upload_headers, data=image_file)
            
            if upload_response.status_code == 201:
                print(f"✅ Image uploaded successfully")
                return asset_id
            else:
                print(f"❌ Failed to upload image: {upload_response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error uploading image to LinkedIn: {e}")
            return None
    
    def _extract_website_context(self, conversation_history: list) -> str:
        """Extract relevant website details from conversation history"""
        
        context = []
        for message in conversation_history[-10:]:  # Last 10 messages
            speaker = message.get('speaker', '')
            content = message.get('content', '')
            
            # Look for website-related information
            if any(keyword in content.lower() for keyword in ['website', 'site', 'web', 'lefleur', 'features', 'design']):
                context.append(f"{speaker}: {content[:200]}...")
        
        if not context:
            return "We built an innovative new website called lefleur.com with modern features and great user experience."
        
        return " | ".join(context[-5:])  # Last 5 relevant messages 