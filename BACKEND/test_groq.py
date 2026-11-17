
import asyncio

from services.llm_service import generate_llm_response


async def main():
    messages = [
        (
            "system",
            "You are a helpful AI assistant."
        ),
        (
            "human",
            "Explain what Retrieval Augmented Generation "
            "is in simple terms."
        )
    ]

    response = await generate_llm_response(messages)

    print("\nGroq Response:\n")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
