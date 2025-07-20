import aiohttp, base64, os
from typing import Dict, Any
from . import Tool, registry

class WebScreenshotTool(Tool):
    name = "take_screenshot"
    description = "Fetch a full-page PNG screenshot for a given URL. Returns base64 PNG."

    async def execute(self, url: str) -> Dict[str, Any]:
        api_key = os.getenv("SCREENSHOT_API_KEY")
        if not api_key:
            return {"error": "SCREENSHOT_API_KEY not set"}
        endpoint = f"https://api.screenshotapi.net/screenshot"
        params = {
            "token": api_key,
            "url": url,
            "output": "image",
            "file_type": "png",
            "full_page": "true"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint, params=params) as resp:
                if resp.status != 200:
                    return {"error": f"status {resp.status}"}
                img_bytes = await resp.read()
                return {
                    "url": url,
                    "image_base64": base64.b64encode(img_bytes).decode("utf-8")
                }

# Register
registry.register_tool(WebScreenshotTool()) 