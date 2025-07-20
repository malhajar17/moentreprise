from typing import Dict, Any

class Tool:
    name: str
    description: str
    async def execute(self, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register_tool(self, tool: Tool):
        self.tools[tool.name] = tool

    def has(self, name: str) -> bool:
        return name in self.tools

    async def run(self, name: str, **kwargs):
        if name not in self.tools:
            return {"error": f"tool {name} not found"}
        return await self.tools[name].execute(**kwargs)

# global registry
registry = ToolRegistry() 