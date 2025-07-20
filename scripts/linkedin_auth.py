#!/usr/bin/env python3
"""
LinkedIn OAuth Helper Script
Helps you get an access token using your Client ID and Client Secret
"""

import requests
import os
from urllib.parse import parse_qs, urlparse

def get_linkedin_access_token():
    """
    Interactive script to get LinkedIn access token
    """
    
    print("🔗 LinkedIn OAuth Access Token Generator")
    print("=" * 50)
    
    # Configuration - Using LinkedIn's default testing redirect URI
    redirect_uri = "https://www.linkedin.com/developers/tools/oauth/redirect"
    
    # Get client credentials
    client_id = input("Enter your LinkedIn Client ID: ").strip()
    client_secret = input("Enter your LinkedIn Primary Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("❌ Both Client ID and Client Secret are required!")
        return
    
    # Step 1: Generate authorization URL (using your custom redirect URL)
    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization?"
        f"response_type=code&"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=openid%20profile%20email%20w_member_social%20w_organization_social"
    )
    
    print(f"\n🌐 Step 1: Open this URL in your browser:")
    print(f"   {auth_url}")
    print(f"\n📋 Step 2: After authorization, copy the FULL redirect URL")
    
    # Get authorization code from user
    redirect_url = input("\n🔗 Paste the full redirect URL here: ").strip()
    
    try:
        # Extract authorization code
        parsed_url = urlparse(redirect_url)
        query_params = parse_qs(parsed_url.query)
        
        if 'code' not in query_params:
            print("❌ No authorization code found in URL. Make sure you copied the complete URL.")
            return
            
        auth_code = query_params['code'][0]
        print(f"✅ Found authorization code: {auth_code[:20]}...")
        
        # Step 3: Exchange code for access token
        print("\n🔄 Exchanging code for access token...")
        
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        token_data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        response = requests.post(token_url, data=token_data, headers=headers)
        
        if response.status_code == 200:
            token_response = response.json()
            access_token = token_response.get('access_token')
            expires_in = token_response.get('expires_in', 'Unknown')
            
            print(f"\n🎉 SUCCESS! Access token obtained:")
            print(f"   Token: {access_token}")
            print(f"   Expires in: {expires_in} seconds")
            
            # Get author ID (person URN)
            print(f"\n👤 Getting your LinkedIn Author ID...")
            profile_response = get_linkedin_profile(access_token)
            
            if profile_response:
                author_id = profile_response.get('id')
                print(f"   Author ID: {author_id}")
                
                # Save to .env file
                save_to_env(access_token, author_id)
            else:
                print("⚠️  Could not retrieve Author ID - you'll need to get it manually")
                save_to_env(access_token, "")
                
        else:
            print(f"❌ Error getting access token:")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def get_linkedin_profile(access_token):
    """Get LinkedIn profile to extract Author ID"""
    try:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get('https://api.linkedin.com/v2/people/~', headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️  Profile API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"⚠️  Error getting profile: {e}")
        return None

def save_to_env(access_token, author_id):
    """Save credentials to .env file"""
    try:
        env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        
        # Read existing .env content
        env_content = ""
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                env_content = f.read()
        
        # Add/update LinkedIn credentials
        lines = env_content.split('\n')
        new_lines = []
        token_added = False
        author_added = False
        
        for line in lines:
            if line.startswith('LINKEDIN_ACCESS_TOKEN='):
                new_lines.append(f'LINKEDIN_ACCESS_TOKEN={access_token}')
                token_added = True
            elif line.startswith('LINKEDIN_AUTHOR_ID='):
                new_lines.append(f'LINKEDIN_AUTHOR_ID={author_id}')
                author_added = True
            else:
                new_lines.append(line)
        
        # Add new entries if not found
        if not token_added:
            new_lines.append(f'LINKEDIN_ACCESS_TOKEN={access_token}')
        if not author_added:
            new_lines.append(f'LINKEDIN_AUTHOR_ID={author_id}')
        
        # Write back to .env
        with open(env_path, 'w') as f:
            f.write('\n'.join(new_lines))
        
        print(f"\n💾 Credentials saved to .env file!")
        print(f"   Path: {env_path}")
        print(f"\n🚀 You can now use the LinkedIn Marketing Agent!")
        
    except Exception as e:
        print(f"⚠️  Could not save to .env file: {e}")
        print(f"\n📋 Manual setup required:")
        print(f"   Add to your .env file:")
        print(f"   LINKEDIN_ACCESS_TOKEN={access_token}")
        if author_id:
            print(f"   LINKEDIN_AUTHOR_ID={author_id}")

if __name__ == "__main__":
    get_linkedin_access_token() 