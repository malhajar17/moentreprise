# 📱 LinkedIn Integration Setup for Moentreprise

This guide explains how to set up LinkedIn API access for Sophie's marketing automation features in Moentreprise.

## 🎯 Overview

Sophie, the Marketing Director persona, can automatically:
- Generate professional marketing content
- Create AI-powered images with DALL-E
- Post directly to your LinkedIn company page
- Share your newly built website with the world

## 🔑 Prerequisites

1. LinkedIn account with company page admin access
2. LinkedIn Developer account
3. Company page where you want to post

## 📋 Step-by-Step Setup

### 1. Create LinkedIn App

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Click "Create app"
3. Fill in the required information:
   - **App name**: Moentreprise Marketing Bot
   - **LinkedIn Page**: Select your company page
   - **Privacy policy URL**: Your website URL
   - **App logo**: Upload Mo logo or your company logo

### 2. Configure OAuth Settings

1. In your app settings, go to "Auth" tab
2. Add OAuth 2.0 redirect URLs:
   ```
   http://localhost:3001/callback
   https://your-domain.com/callback
   ```
3. Request the following permissions:
   - `r_liteprofile`
   - `w_member_social`
   - `r_organization_social`
   - `w_organization_social`

### 3. Get Your Credentials

From the "Auth" tab, copy:
- **Client ID**
- **Client Secret**

### 4. Generate Access Token

#### Option 1: Using LinkedIn's OAuth Flow

1. Construct the authorization URL:
   ```
   https://www.linkedin.com/oauth/v2/authorization?
   response_type=code&
   client_id=YOUR_CLIENT_ID&
   redirect_uri=http://localhost:3001/callback&
   scope=r_liteprofile%20w_member_social%20r_organization_social%20w_organization_social
   ```

2. Visit the URL and authorize the app
3. Extract the `code` from the redirect URL
4. Exchange code for access token:
   ```bash
   curl -X POST https://www.linkedin.com/oauth/v2/accessToken \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -d 'grant_type=authorization_code' \
     -d 'code=YOUR_AUTH_CODE' \
     -d 'client_id=YOUR_CLIENT_ID' \
     -d 'client_secret=YOUR_CLIENT_SECRET' \
     -d 'redirect_uri=http://localhost:3001/callback'
   ```

#### Option 2: Using LinkedIn Token Inspector

For testing, you can use LinkedIn's Token Inspector to generate a token with the required permissions.

### 5. Get Organization and Author IDs

#### Organization ID:
1. Go to your LinkedIn company page
2. Click "Admin tools" → "Page info"
3. Your organization ID is in the URL or page info
4. Format: `urn:li:organization:12345678`

#### Author ID:
1. Use this API call with your access token:
   ```bash
   curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     https://api.linkedin.com/v2/me
   ```
2. Extract the `id` field from the response

### 6. Configure Moentreprise

Add to your `.env` file:
```env
LINKEDIN_ACCESS_TOKEN=your-access-token
LINKEDIN_AUTHOR_ID=urn:li:person:YOUR_ID
LINKEDIN_ORG_ID=12345678  # Just the number, not the full URN
```

## 🧪 Testing Your Setup

1. Start Moentreprise:
   ```bash
   cd examples
   python web_demo.py
   ```

2. Launch an AI business team session
3. Let the team build a website
4. Watch Sophie create and post to LinkedIn automatically

## 🔒 Security Best Practices

1. **Never commit tokens**: Keep `.env` in `.gitignore`
2. **Rotate tokens regularly**: LinkedIn tokens expire
3. **Limit permissions**: Only request needed scopes
4. **Use environment variables**: Never hardcode credentials

## 🚨 Troubleshooting

### "Unauthorized" Error
- Check if your access token is valid
- Ensure you have the correct permissions
- Verify organization admin access

### "Organization not found"
- Confirm the organization ID is correct
- Check if you're an admin of the company page
- Try using just the numeric ID without the URN prefix

### Image Upload Fails
- Ensure DALL-E API is working
- Check image size (LinkedIn has limits)
- Verify media upload permissions

### Post Not Appearing
- Check LinkedIn's posting limits
- Ensure content meets LinkedIn guidelines
- Verify the company page is active

## 📝 API Rate Limits

LinkedIn enforces rate limits:
- **Daily**: Varies by app and permissions
- **Per-minute**: Usually 100-300 requests
- **Posting**: Be mindful of spam policies

## 🎨 Customizing Sophie's Posts

Edit Sophie's behavior in `src/personas/linkedin_marketer.py`:

```python
# Customize post template
post_template = """
🚀 {headline}

{description}

✨ {key_features}

🔗 {website_url}

#Moentreprise #AIAutomation #WebDevelopment
"""
```

## 📚 Additional Resources

- [LinkedIn API Documentation](https://docs.microsoft.com/en-us/linkedin/)
- [OAuth 2.0 Guide](https://docs.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow)
- [Company Page API](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/organization-share-api)

---

With LinkedIn integration configured, Sophie can now automatically market your AI-built websites to the world! 🎯📱✨ 