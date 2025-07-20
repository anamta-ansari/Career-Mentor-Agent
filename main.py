from agents import Agent, Runner, OpenAIChatCompletionsModel, RunConfig
from openai.types.responses import ResponseTextDeltaEvent
from openai import AsyncOpenAI
from dotenv import load_dotenv
import chainlit as cl
import os

load_dotenv()

# ----------------------------
# Load GEMINI API Key
# ----------------------------
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("Set GEMINI_API_KEY in .env")

# ----------------------------
# Gemini Client Setup (not used in fallback anymore)
# ----------------------------
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=client,
)

config = RunConfig(model=model, model_provider=client, tracing_disabled=True)

# ----------------------------
# Career Mentor Agent setup
# ----------------------------
agent = Agent(
    name="CareerMentorAgent",
    instructions="""
    You are a Career Mentor. Guide users through three types of requests:

    1. Suggest suitable career paths based on their interests.
    2. Provide skill roadmaps for a specific career.
    3. Suggest real-world job titles/roles related to a chosen field.

    Be concise, helpful, and personalized in your replies.
    """
)

# ----------------------------
# Chainlit Chat Start
# ----------------------------
@cl.on_chat_start
async def handle_start():
    cl.user_session.set("history", [])
    await cl.Message(
        content="👩‍💼 Hello! I'm your Career Mentor. Ask me about careers, skills to learn, or job roles."
    ).send()

# ----------------------------
# Chainlit Chat Message Handler
# ----------------------------
@cl.on_message
async def handle_message(message: cl.Message):
    history = cl.user_session.get("history")
    history.append({"role": "user", "content": message.content})

    msg = cl.Message(content="")
    await msg.send()

    # ✅ Hardcoded roadmaps
    roadmaps = {
        "data scientist": "1. Python\n2. Statistics\n3. Machine Learning\n4. SQL\n5. Real-world projects",
        "web developer": "1. HTML/CSS\n2. JavaScript\n3. React or Vue\n4. Backend (Node.js/Django)\n5. Deploy projects",
        "ai engineer": "1. Python\n2. Deep Learning\n3. NLP\n4. TensorFlow\n5. Model Deployment",
        "graphic designer": "1. Adobe Tools\n2. Color Theory\n3. Typography\n4. UI/UX\n5. Portfolio",
        "seo": "1. Keyword Research\n2. On-Page SEO\n3. Link Building\n4. Analytics Tools (GA, GSC)\n5. Content Optimization"
    }

    # 🔍 Match user's query
    user_query = message.content.lower()
    response_override = None

    for career, roadmap in roadmaps.items():
        if career in user_query:
            response_override = f"🛠️ Skill roadmap for **{career.title()}**:\n{roadmap}"
            break

    if response_override:
        msg.content = response_override
        await msg.update()
        history.append({"role": "assistant", "content": response_override})
        cl.user_session.set("history", history)
        return

    # ✅ Custom support message (instead of Gemini)
    support_msg = (
        "❓ I don’t have a predefined roadmap for that career yet.\n\n"
        "But I can still help! Please tell me more about the field or interest you have.\n\n"
        "You can also try asking about:\n"
        "- Web Developer\n- Data Scientist\n- AI Engineer\n- SEO Expert\n- Graphic Designer"
    )

    msg.content = support_msg
    await msg.update()
    history.append({"role": "assistant", "content": support_msg})
    cl.user_session.set("history", history)
    return
