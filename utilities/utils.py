"""
Author: Nishant Sharma (nishant@insituate.ai)

File: utilities/utils.py
Description: Implements various global methods for Nova
"""

from utilities.db_utils import *
from utilities.llm_utils import openai_response, bedrock_response, groq_response
from utilities.core_utils import remove_emojis, remove_prefixes, extract_quoted_content
import asyncio

async def generate_reply_1(user_utterance: str, user_name: str, conversation: str, user_id: str, db):
    buddy_preamble = load_text_file('utilities/prompts/buddy_preamble.txt').format(buddy_name=buddy_name, user_name=user_name)
    
    memory = get_memory(db=db, user_id=user_id)
    print(colored(f"Retrieved Memory: {memory}", 'red'))

    # To retrieve a summary
    user_summary = get_user_summary(user_id=user_id, db=db)

    content = generate_final_prompt(user_id=user_id, user_name=user_name, memory=memory, user_utterance=user_utterance, conversation=conversation, buddy_name=buddy_name, user_summary=user_summary)
    prompt_list = [{"role": "system", "content": buddy_preamble}, {"role": "user", "content": content}]

    # Run both coroutines concurrently
    memory_result, reply = await asyncio.gather(
        synthesize_memory(user_utterance=user_utterance, user_name=user_name, user_id=user_id, conversation=conversation, db=db),
        model_response(model_name=reply_model_name, prompt_list=prompt_list)
    )

    reply = extract_quoted_content(reply)

    return reply


async def synthesize_memory(user_utterance: str, user_name: str, user_id: str, conversation, db):
    if user_utterance != "":
        user_utterance = f"""The utterance is given by the user. Remember that you have to extract the memory from the utterance only.
        {user_utterance}
        """

    preamble = load_text_file('utilities/prompts/memory_preamble.txt')
    final_prompt = load_text_file('utilities/prompts/memory_prompt.txt').format(
        user_name=user_name,
        conversation=conversation,
        user_utterance=user_utterance
    )

    prompt_list = [{"role": "system", "content": preamble}, {"role": "user", "content": final_prompt}]

    response = await model_response(prompt_list=prompt_list, model_name=memory_model_name, structured='True-memory')
    
    if response['memory_found'] == True:
        store_memory(db=db, user_id=user_id, memory=response['memory'])
        return True
    else:
        return False

async def model_response(model_name: str, prompt_list: list, structured=False):
    global config

    if model_name == 'openai':
        reply = openai_response(prompt_list, structured=structured)
    elif model_name == 'bedrock':
        reply = bedrock_response(prompt_list, structured=structured)
    elif model_name == 'groq':
        reply = groq_response(prompt_list, structured=structured)
    else:
        reply = openai_response(prompt_list, structured=structured)

    # If the reply is a coroutine, await it
    if asyncio.iscoroutine(reply):
        reply = await reply

    # Remove emojis and prefixes from the reply
    reply = remove_prefixes(remove_emojis(reply), ['Nova:', 'Nova :', 'Haha,', 'haha,', 'nova:', 'nova: '])
    
    # New function to extract content within outermost quotes
    def extract_content(text):
        if text.startswith('"') and text.endswith('"'):
            return text[1:-1]
        return text

    return reply

async def generate_summary_and_insights(user_id: str, conversation: str, db: Session):
    # Load the summary prompt
    summary_prompt = load_text_file('utilities/prompts/summary_prompt.txt')
    
    # Create the prompt list
    prompt_list = [
        {"role": "system", "content": "You are an AI assistant tasked with generating a summary of a user's conversation."},
        {"role": "user", "content": summary_prompt.format(conversation=conversation)}
    ]
    
    # Generate the summary using one of the models
    summary = await model_response(model_name=config['summary_model_name'], prompt_list=prompt_list, structured=False)
    
    # Add or update the summary in the database
    upsert_summary(user_id=user_id, summary=summary, db=db)
    
    return summary


