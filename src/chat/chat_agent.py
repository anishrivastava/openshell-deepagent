from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7
)

# =========================
# 🔥 SAFE CHAT RESPONSE
# =========================
def generate_chat_response(
    user_query,
    tool_output,
    history=None,
    skill="logistics"
):

    try:

        prompt = f"""
You are a helpful AI logistics assistant.

User Query:
{user_query}

Skill:
{skill}

Tool Output:
{str(tool_output)[:3000]}

Respond conversationally like ChatGPT.
Keep response short and professional.
"""

        response = llm.invoke(prompt)

        return response.content

    except Exception as e:

        return f"AI response generation failed: {str(e)}"