from langchain_mcp_adapters.client import MultiServerMCPClient


client = MultiServerMCPClient(
    {
        "medical-care": {
            "transport": "stdio",
            "command": "uv",
            "args": [
                "run",
                "python",
                "-m",
                "mcp_server.server",
            ],
        }
    }
)


async def get_medical_tools():
    """Load the tools exposed by the medical MCP server."""
    return await client.get_tools()