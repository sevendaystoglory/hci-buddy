from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()

client = OpenAI(api_key = os.getenv('OPENAI_KEY'))

response = client.audio.speech.create(
    model="tts-1-hd",
    voice="nova",
    input="Good morning, Nishant. Have anything up your mind?",
)

response.stream_to_file("output3.mp3")
