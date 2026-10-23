# Nexora — AI Study Assistant

Nexora is an AI-powered study assistant built with **LangGraph** and the **Model Context Protocol (MCP)**. It connects to two separate MCP servers — one remote, one local — to give a single conversational agent access to both a shared study-resource question bank and a private personal notes/tasks system.

**Demo video:** [Watch Nexora in action](https://drive.google.com/file/d/1NAQ_g2Syy-_bCz_trWXMIASu1ZrHS6er/view?usp=drivesdk) — shows both the local notes/tasks server and the remote study-resources server working end-to-end.

---

## What it does

Ask Nexora things like:
- "What topics are available for Data Structures?"
- "Quiz me on medium-difficulty questions for Operating Systems."
- "What's my progress on Algorithms?"
- "Who's leading the leaderboard for DBMS?"
- "Save a note under Python / Decorators about how `@staticmethod` works."
- "What tasks do I still have pending?"

The agent decides which MCP server to route each request to and calls the right tool automatically.

## Architecture

```
┌─────────────┐        ┌──────────────────────────┐
│  Streamlit  │◄──────►│   LangGraph Agent (Gemini) │
│   Frontend  │        └──────────────────────────┘
└─────────────┘                   │
                    ┌──────────────┴──────────────┐
                    ▼                              ▼
        ┌────────────────────┐        ┌─────────────────────────┐
        │ Study Resources MCP │        │  Study Personal MCP      │
        │ (remote, HTTP)      │        │  (local, stdio)          │
        │ Prefect Horizon     │        │  SQLite-backed           │
        │ 9 tools: questions, │        │  6 tools: notes, tasks    │
        │ progress, leaderboard│       │                          │
        └────────────────────┘        └─────────────────────────┘
```

This is an intentional hybrid design, not an oversight:

- **Study Resources MCP** is deployed remotely over HTTP because it's shared, non-sensitive data (question banks, leaderboards) that should be reachable from anywhere.
- **Study Personal MCP** runs locally over stdio and stores notes/tasks in a local SQLite file **by design** — this keeps personal study data on your own machine rather than in a shared cloud database. This mirrors how tools like Claude Desktop handle local MCP servers for personal data.

## Tech stack

- **Agent orchestration:** LangGraph (`create_agent`), `langchain-mcp-adapters`
- **LLM:** Google Gemini (via `langchain-google-genai`)
- **Frontend:** Streamlit
- **MCP servers:** FastMCP (both remote and local)
- **Local storage:** SQLite
- **Auth:** Bearer token auth for the remote MCP server

## Setup

### 1. Clone and install
```bash
git clone https://github.com/raghuvendra34/nexora.git
cd nexora
uv sync   # or: pip install -r requirements.txt
```

### 2. Environment variables
Create a `.env` file:
```
GOOGLE_API_KEY=your_gemini_api_key
STUDY_RESOURCES_API_KEY=your_study_resources_api_key
LOCAL_MCP_PATH=/absolute/path/to/local-mcp
```

### 3. Run the local MCP server
The personal notes/tasks server needs to be reachable locally for the notes/tasks tools to work:
```bash
cd local-mcp
uv run fastmcp inspect main.py   # sanity check
```

### 4. Run the app
```bash
streamlit run app.py
```

## Deployment & limitations

**Important:** the hosted Streamlit Cloud link only has access to the **remote** Study Resources MCP server. The Study Personal MCP server communicates over stdio and depends on a local SQLite file — there's nothing for the deployed app to connect to unless you're running it locally.

The [demo video](https://drive.google.com/file/d/1NAQ_g2Syy-_bCz_trWXMIASu1ZrHS6er/view?usp=drivesdk) above shows both servers working together on a local run, so you can see the full feature set even without cloning the repo.

| Feature | Local run | Deployed link |
|---|---|---|
| Topics, questions, quizzing | ✅ | ✅ |
| Progress tracking, leaderboard | ✅ | ✅ |
| Personal notes | ✅ | ❌ |
| Personal tasks | ✅ | ❌ |

To use the full feature set, clone the repo and run it locally following the setup steps above.

## Known limitations & next steps

- **Personal data isn't reachable remotely.** Planned fix: migrate the personal MCP server from stdio + local SQLite to HTTP transport + a hosted Postgres instance (e.g. Supabase), with per-user scoping, so the deployed link works end-to-end.
- **Agent is rebuilt per request.** Currently the LangGraph agent and MCP client are reinitialized on every chat message. Next step: cache the client/agent across a session using `st.cache_resource` to reduce latency.
- **No conversation memory beyond the current Streamlit session.** Chat history resets on reload; a future version could persist conversations per user.

## Project structure

```
nexora/
├── app.py              # Streamlit frontend + agent invocation
├── client.py            # MCP client configuration (both servers)
├── local-mcp/
│   └── main.py           # Personal notes/tasks MCP server (stdio, SQLite)
└── README.md
```

---

Built by Raghuvendra Kumar — [portfolio](https://raghuvendra34.github.io) · [LinkedIn](https://linkedin.com/in/raghuvendra-kumar-76919128a)
