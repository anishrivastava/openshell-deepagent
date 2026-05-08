# from langchain_openai import ChatOpenAI

# llm = ChatOpenAI(
#     model="gpt-4o-mini",
#     temperature=0.7
# )

# # =========================
# # 🔥 SAFE CHAT RESPONSE
# # =========================
# def generate_chat_response(
#     user_query,
#     tool_output,
#     history=None,
#     skill="logistics"
# ):

#     try:

#         prompt = f"""
# You are a helpful AI logistics assistant.

# User Query:
# {user_query}

# Skill:
# {skill}

# Tool Output:
# {str(tool_output)[:3000]}

# Respond conversationally like ChatGPT.
# Keep response short and professional.
# """

#         response = llm.invoke(prompt)

#         return response.content

#     except Exception as e:

#         return f"AI response generation failed: {str(e)}"

"""
chat/chat_agent.py  —  LLM chat response generator
Keeps gpt-4o-mini via LangChain.
Fixes: history is now actually used in the prompt.
Adds:  file_context support (for uploaded truck reports).
"""

from __future__ import annotations
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

logger = logging.getLogger(__name__)

# ─── LLM client ────────────────────────────────────────────────────────────────
# API key is read automatically from OPENAI_API_KEY env var
# (set via GCP Secret Manager → Cloud Run env var)
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    streaming=True,        # enables token-by-token streaming to UI
)


# ==============================================================================
# GENERATE CHAT RESPONSE
# ==============================================================================
def generate_chat_response(
    user_query: str,
    tool_output,
    history: list | None = None,
    skill: str = "logistics",
    file_context: str | None = None,   # NEW: extracted text from uploaded report
) -> str:
    """
    Build a message list from history + current query and call the LLM.

    history format (same dict shape stored in Firestore):
        [ { "role": "user"|"assistant", "content": "..." }, ... ]

    Returns the assistant's response as a plain string.
    """
    try:
        # 1. System prompt
        system_content = f"""You are a helpful AI logistics assistant specialising in {skill}.
Be concise, professional, and conversational.
When referencing tool output, summarise the key numbers — don't dump raw data.
If a report has been uploaded, use it as your primary context."""

        if file_context:
            system_content += f"\n\nUploaded report context:\n{file_context[:3000]}"

        messages = [SystemMessage(content=system_content)]

        # 2. Inject conversation history (THIS WAS MISSING BEFORE)
        if history:
            for entry in history[-10:]:   # last 10 turns to stay within token limit
                role = entry.get("role", "user")
                content = entry.get("content", "")
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))

        # 3. Current user message + tool output
        user_content = f"{user_query}"
        if tool_output:
            user_content += f"\n\nTool output:\n{str(tool_output)[:3000]}"

        messages.append(HumanMessage(content=user_content))

        # 4. Call LLM
        response = llm.invoke(messages)
        return response.content

    except Exception as e:
        logger.error(f"[chat_agent] generate_chat_response failed: {e}")
        return f"AI response generation failed: {str(e)}"


# ==============================================================================
# STREAMING VERSION  (used by SSE endpoint in api.py)
# ==============================================================================
async def stream_chat_response(
    user_query: str,
    tool_output,
    history: list | None = None,
    skill: str = "logistics",
    file_context: str | None = None,
):
    """
    Async generator that yields response tokens one by one.
    Used by the SSE streaming endpoint.

    Usage in api.py:
        async for token in stream_chat_response(...):
            yield f"data: {token}\n\n"
    """
    try:
        system_content = f"""You are a helpful AI logistics assistant specialising in {skill}.
Be concise, professional, and conversational.
When referencing tool output, summarise the key numbers — don't dump raw data."""

        if file_context:
            system_content += f"\n\nUploaded report context:\n{file_context[:3000]}"

        messages = [SystemMessage(content=system_content)]

        if history:
            for entry in history[-10:]:
                role = entry.get("role", "user")
                content = entry.get("content", "")
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))

        user_content = user_query
        if tool_output:
            user_content += f"\n\nTool output:\n{str(tool_output)[:3000]}"

        messages.append(HumanMessage(content=user_content))

        # Stream tokens
        async for chunk in llm.astream(messages):
            if chunk.content:
                yield chunk.content

    except Exception as e:
        logger.error(f"[chat_agent] stream_chat_response failed: {e}")
        yield f"Error: {str(e)}"