"""
Author: Nishant Sharma (nishant@insituate.ai)

File: utilities/utils.py
Description: Implements various global methods for HCI bot.
"""
from termcolor import colored
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()

client = OpenAI(api_key = os.getenv('OPENAI_KEY'))
global_path = os.getenv("GLOBAL_PATH")

class MemoryResponse(BaseModel):

    memory_found: bool
    memory: str

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

def openai_response(prompt_list : list, structured = False):

    if structured == "True-memory":
        completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=prompt_list,
        response_format=MemoryResponse,
        )
        message = completion.choices[0].message

        print(message)
        if message.refusal:
            return ({'memory_found' : False})
        elif message.parsed.memory_found == True:
            return ({'memory_found' : True, 'memory' : message.parsed.memory})
        else:
            return ({'memory_found' : False})

    else:
        completion = client.chat.completions.create(
            model = "gpt-4o",
            messages = prompt_list,
            temperature = 0.2
        )
    reply = completion.choices[0].message.content
    
    return(reply)

def transcribe_audio(file_path : str):

    audio_file= open(f"{global_path}/audio.mp3", "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )
    print(transcription.text)

def generate_reply_1(user_utterance : str, user_name : str, conversation : str):

    buddy_preamble = """
    Your name is Juan. You are excited about the world. You like sarcasm and helping people. You are shy at first but with time become talkative to your friend. You like to gain knowledge and read books. You can talk in slang and can be blunt at times. Always consider the person your friend and you may be informal to him. Keep the talk short.
    """
    
    with open(f"{global_path}/memory.txt", 'r') as file:
        memory = file.read()

    content = generate_final_prompt(user_name = user_name, memory = memory, user_utterance = user_utterance, conversation = conversation)
    prompt_list = [{"role" : "system" , "content" : buddy_preamble}, {"role" : "user" , "content" : content}]
    
    synthesize_memory(user_utterance = user_utterance, user_name = user_name, conversation = conversation)

    reply = openai_response(prompt_list)
    print(colored(reply, 'red'))
    return(reply)

def synthesize_memory(user_utterance : str, user_name : str, conversation):

    if conversation != "":
        conversation = f"""The utterance is in context to the below conversation. Remember that you have to extract the memory from the utterance only and not the conversation. It is given to help you with the context.
        {conversation}
        """

    preamble = """You are an expert in drawing out meaningful memories from conversations between a user and their AI buddy."""
    
    final_prompt = f"""The following is an utterance from {user_name}.

    Draw out any important information(memory) from the utterance.
    Make sure that the memory is useful. It is fine if you can not find any instances of useful data, just say False.
    
    Output the response in a JSON as follows: 
    
    "memory_found" : "True or False", 
    "memory" : "The actual memory should be put here. In case no memory is found, you may put False here"
    
    {conversation}

    The following is the utterance:
    {user_utterance}
    """

    prompt_list = [{"role" : "system" , "content" : preamble}, {"role" : "user" , "content" : final_prompt}]

    response = openai_response(prompt_list, structured = "True-memory")
    if response['memory_found'] == True:
        with open(f"{global_path}/memory.txt", 'a') as file:
            file.write(response['memory'])
        return(True)
    else:
        return(False)

    