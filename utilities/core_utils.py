"""
Author: Nishant Sharma (nishant@insituate.ai)

File: utilities/core_utils.py
Description: Implements functions with shareed logic across all other util files
"""

import os
from termcolor import colored
import time
import json
import os
import uuid
from dotenv import load_dotenv
from datetime import datetime

def load_config(env="development"):
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', f'{env}.json')
    with open(config_path, 'r') as config_file:
        return json.load(config_file)

def generate_new_user_id():
    # Generate a UUID, remove dashes, and prepend 'user_'
    uuid_str = str(uuid.uuid4()).replace('-', '')
    return f"user_{uuid_str[:32]}"

def generate_final_prompt(user_name : str, memory : str, user_utterance : str, conversation : str):

    if memory != "":
        memory = f"""The following is a memory about {user_name}. It contains experiences and opinions.
        {memory}
        """

    if conversation != "":
        conversation = f"""The following is a conversation of you and {user_name}, for context:
        {conversation}
        """

    prompt = f"""You are {user_name}'s buddy.

    {memory}
    
    {conversation}
    {user_name} : {user_utterance}

    You have to reply to keep the conversation flowing.
    """
    return(prompt)

def transcribe_audio(file_path : str):

    audio_file= open(f"{global_path}/audio.mp3", "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )
    print(transcription.text)