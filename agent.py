from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from client import get_client

load_dotenv()

SYSTEM_PROMPT = """
You are Nexora, an AI study assistant.

Use the Personal Study MCP for notes and tasks.

Use the Study Resources MCP for:
- topics
- questions
- progress
- recommendations
- leaderboard

Always use MCP tools when the required information is available.
Do not invent information.
Give clear, concise, student-friendly answers.
"""


async def create_nexora_agent():
    """Build the Nexora LangGraph agent, wired to both MCP servers.

    This is the single source of truth for agent construction — app.py
    imports and calls this rather than duplicating the setup.
    """
    client = get_client()
    tools = await client.get_tools()

    model = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        temperature=0
    )

    return create_agent(
        model=model,
        tools=tools,
        system_prompt=SYSTEM_PROMPT
    )