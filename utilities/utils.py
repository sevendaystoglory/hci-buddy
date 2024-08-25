"""
Author: Nishant Sharma (nishant@insituate.ai)

File: utilities/utils.py
Description: Implements various global methods for Nova
"""
from utilities.db_utils import *
from utilities.llm_utils import openai_response, bedrock_response, groq_response, openai_client

load_dotenv()

config = load_config()

buddy_name = config['buddy_name']
global_path = config['global_path']
memory_model_name = config['memory_model_name']
reply_model_name = config['reply_model_name']

def generate_reply_1(user_utterance : str, user_name : str, conversation : str, user_id : str, db):

    buddy_preamble = f"""
    Your name is {buddy_name}. You are excited about the world. You like sarcasm and helping people. You are shy at first but with time become talkative to your friend. You like to gain knowledge and read books. You can talk in slang and can be blunt at times. Always consider the person your friend and you may be informal to him. Keep the talk short.
    """
    memory = get_memory(db = db, user_id = user_id)
    print(colored(memory, 'yellow'))

    content = generate_final_prompt(user_name = user_name, memory = memory, user_utterance = user_utterance, conversation = conversation)
    prompt_list = [{"role" : "system" , "content" : buddy_preamble}, {"role" : "user" , "content" : content}]
    
    synthesize_memory(user_utterance = user_utterance, user_name = user_name, conversation = conversation, db = db, user_id = user_id)

    reply = model_response(model_name = reply_model_name, prompt_list = prompt_list)

    return(reply)

def synthesize_memory(user_utterance : str, user_name : str, user_id : str, conversation, db):

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

    response = model_response(prompt_list = prompt_list, model_name = memory_model_name, structured = 'True-memory')
    
    if response['memory_found'] == True:
        store_memory(db = db, user_id = user_id, memory = response['memory'])
        return(True)
    else:
        return(False)

def model_response(model_name :  str, prompt_list : list, structured = False):
    
    global config

    if model_name == 'openai':
        reply = openai_response(prompt_list, structured = structured)
    elif model_name == 'bedrock':
        reply = bedrock_response(prompt_list, structured = structured)
    elif model_name == 'groq':
        reply = groq_response(prompt_list, structured = structured)
    else:
        reply = openai_response(prompt_list, structured = structured)

    return reply
    