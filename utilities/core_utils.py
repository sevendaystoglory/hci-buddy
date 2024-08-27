"""
Author: Nishant Sharma (nishant@insituate.ai)

File: utilities/core_utils.py
Description: Implements functions with shared logic across all other util files
"""

import os
from termcolor import colored
import time
import json
import os
import uuid
from dotenv import load_dotenv
from datetime import datetime
import re

load_dotenv()

def load_config(env="development"):
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', f'{env}.json')
    with open(config_path, 'r') as config_file:
        return json.load(config_file)
        
config = load_config()

buddy_name = config['buddy_name']
global_path = config['global_path']
memory_model_name = config['memory_model_name']
reply_model_name = config['reply_model_name']

def load_text_file(file_path: str) -> str:
    full_path = os.path.join(global_path, file_path)
    with open(full_path, 'r') as file:
        return file.read().strip()

def remove_emojis(text):
    """Remove all emojis from the given text or dictionary."""
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    
    if isinstance(text, dict):
        return {k: remove_emojis(v) for k, v in text.items()}
    elif isinstance(text, str):
        return emoji_pattern.sub(r'', text)
    else:
        return text
def remove_prefixes(text, prefixes: list):
    """
    Remove specified prefixes from the beginning of the text or dictionary values.
    
    Args:
    text (str or dict): The input text or dictionary to process.
    prefixes (list): A list of prefixes to remove.
    
    Returns:
    str or dict: The text or dictionary with specified prefixes removed from the beginning of string values.
    """
    if isinstance(text, dict):
        return {k: remove_prefixes(v, prefixes) for k, v in text.items()}
    elif isinstance(text, str):
        for prefix in prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):]
        return text.strip()
    else:
        return text

def generate_new_user_id():
    # Generate a UUID, remove dashes, and prepend 'user_'
    uuid_str = str(uuid.uuid4()).replace('-', '')
    return f"user_{uuid_str[:32]}"

def generate_final_prompt(user_name: str, memory: str, user_utterance: str, conversation: str, buddy_name: str):
    prompt_template = load_text_file('utilities/prompts/final_prompt_template.txt')

    if memory:
        memory = f"""The following is a memory about {user_name}. It contains experiences and opinions.
        {memory}
        """

    if conversation:
        conversation = f"""The following is a conversation of you and {user_name}, for context:
        {conversation}
        """

    prompt = prompt_template.format(
        user_name=user_name,
        memory=memory,
        buddy_name=buddy_name,
        conversation=conversation,
        user_utterance=user_utterance
    )
    return prompt

def transcribe_audio(file_path : str):

    audio_file= open(f"{global_path}/audio.mp3", "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )
    print(transcription.text)