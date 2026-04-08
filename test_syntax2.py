from google import genai
import asyncio
import os

async def main():
    client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY', 'test'))
    try:
        stream = await client.aio.models.generate_content_stream(model='gemini-2.5-flash', contents='hello')
        async for chunk in stream:
            print("TEXT:", chunk.text)
            print("USAGE:", chunk.usage_metadata)
    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    asyncio.run(main())
