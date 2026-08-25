import os
from dotenv import load_dotenv
from fastmcp.client.auth import BearerAuth
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()


def get_client():
    local_mcp_path = os.environ["LOCAL_MCP_PATH"]

    return MultiServerMCPClient({
        "study-personal": {
            "transport": "stdio",
            "command": "uv",
            "args": [
                "run",
                "--directory",
                local_mcp_path,
                "python",
                "main.py",
            ],
        },

        "study-resources": {
            "transport": "streamable_http",
            "url": "https://study-resources-mcp.fastmcp.app/mcp",
            "auth": BearerAuth(os.environ["STUDY_RESOURCES_API_KEY"]),
        },
    })