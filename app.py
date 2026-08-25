import asyncio
import streamlit as st

from agent import create_nexora_agent


def get_event_loop():
    """Reuse one event loop for the whole session instead of creating and
    closing a new one per message. The cached agent's MCP connections are
    bound to whichever loop they were created on, so tearing down the loop
    between messages breaks them with 'Event loop is closed'."""
    if "loop" not in st.session_state:
        st.session_state.loop = asyncio.new_event_loop()
    return st.session_state.loop


def get_agent():
    """Build the agent once per session and cache it, instead of
    reconnecting to both MCP servers on every single chat message."""
    if "agent" not in st.session_state:
        loop = get_event_loop()
        st.session_state.agent = loop.run_until_complete(create_nexora_agent())
    return st.session_state.agent


def ask_nexora(question):
    loop = get_event_loop()
    agent = get_agent()

    async def _run():
        result = await agent.ainvoke({
            "messages": [
                {"role": "user", "content": question}
            ]
        })

        response = next(
            (m.content for m in reversed(result["messages"])
             if m.type == "ai" and m.content),
            "I couldn't generate a response."
        )

        if isinstance(response, list):
            response = "".join(
                item.get("text", "")
                for item in response
                if isinstance(item, dict)
            )

        return response

    return loop.run_until_complete(_run())


st.set_page_config(
    page_title="Nexora",
    page_icon="📚",
    layout="centered"
)

st.title("Nexora")
st.caption("Your AI study assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask Nexora anything about your studies..."):

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = ask_nexora(prompt)
                st.markdown(response)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })

            except Exception as e:
                st.error(f"Something went wrong: {e}")