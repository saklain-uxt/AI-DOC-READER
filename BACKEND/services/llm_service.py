
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODEL_NAME = "openai/gpt-oss-120b"


def get_llm():
    """
    Initialize and return the Groq chat model.
    """

    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not configured")

    return ChatGroq(
        model=MODEL_NAME,
        temperature=0.2,
        api_key=GROQ_API_KEY,
        max_retries=2,
    )


async def generate_llm_response(messages):
    """
    Generate a response asynchronously using Groq.
    """

    llm = get_llm()

    response = await llm.ainvoke(messages)

    return response.content
