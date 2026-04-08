from google import genai
import asyncio

async def main():
    client = genai.Client(api_key='test')
    try:
        stream = await client.aio.models.generate_content_stream(model='gemini-2.5-flash', contents='x')
        print("AWAIT SUCCESS", type(stream))
    except Exception as e:
        print("AWAIT ERROR:", e)

if __name__ == "__main__":
    asyncio.run(main())
