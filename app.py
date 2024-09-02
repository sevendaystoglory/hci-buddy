"""
Author: Nishant Sharma (nishant@insituate.ai)

File: utilities/llm_utils.py
Description: Implements llm calls
"""

from fastapi import FastAPI, Request, HTTPException, Depends, status, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from pydantic import BaseModel
import subprocess
import uvicorn
from utilities.utils import *
from google.cloud import texttospeech
import asyncio
import time
import io

app = FastAPI()

class InputData(BaseModel):
    utterance: str
    user_name: str
    user_id: str
    transcript: str = None

class UserCreate(BaseModel):
    name: str
    password: str
    email: str

class UserUpdate(BaseModel):
    name: str = None
    password: str = None

class Login(BaseModel):
    email: str
    password: str

@app.post("/sign_up")
async def new_user_sign_up(user: UserCreate, db: Session = Depends(get_db)):
    user_id = generate_new_user_id()
    try:
        return create_user(user_id=user_id, name=user.name, email=user.email, password=user.password, db=db)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})

@app.post("/login")
async def login(login : Login, db: Session = Depends(get_db)):
    # try:
        return user_login(email=login.email, password=login.password, db=db)
    # except Exception as e:
        # return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})

# Read user by user_id
@app.get("/users/{user_id}")
async def read_user(user_id: str, db: Session = Depends(get_db)):
    db_user = get_user_by_id(user_id=user_id, db=db)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Update user details
@app.put("/users/{user_id}")
async def update_user_route(user_id: str, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = update_user(user_id=user_id, name=user.name, password=user.password, db=db)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated", "user": db_user}

# Delete a user
@app.delete("/users/{user_id}")
async def delete_user_route(user_id: str, db: Session = Depends(get_db)):
    db_user = delete_user(user_id=user_id, db=db)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted", "user": db_user}

# Give reply
@app.post("/generate_reply")
async def generate_text(data: InputData, db: Session = Depends(get_db)):
    start = time.time()
    # try:
    user_input = data.utterance
    user_name = data.user_name
    user_id = data.user_id

    print(user_id)
    print(user_input)

    conversation_history = read_conversation(user_id=user_id, db=db)
    print(colored(f"conversation_history : {conversation_history}", 'yellow'))

    if user_input:

        reply = await generate_reply_1(user_utterance=user_input, user_id=user_id, user_name=user_name, conversation=conversation_history, db=db)
        add_conversation(user_id=user_id, role=user_name, message=user_input, db=db)
        add_conversation(user_id=user_id, role=buddy_name, message=reply, db=db)
        if asyncio.iscoroutine(reply):
            reply = asyncio.run(reply)
        print(reply)
        response = JSONResponse(status_code=200, content={"message": reply})
        
        end = time.time()
        print(f"Time Elapsed: {end-start}")
        return response
    else:
        return JSONResponse(status_code=400, content={"message": "Invalid input"})
    
    # except Exception as e:
    #     return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})

# Generate audio
@app.post("/generate_audio")
async def generate_audio(data: InputData, db: Session = Depends(get_db)):
    start = time.time()
    user_input = data.utterance
    user_name = data.user_name
    user_id = data.user_id

    print(user_id)
    print(user_input)

    conversation_history = read_conversation(user_id=user_id, db=db)
    print(colored(f"conversation_history : {conversation_history}", 'yellow'))

    if user_input:
        reply = await generate_reply_1(user_utterance=user_input, user_id=user_id, user_name=user_name, conversation=conversation_history, db=db)
        add_conversation(user_id=user_id, role=user_name, message=user_input, db=db)
        add_conversation(user_id=user_id, role=buddy_name, message=reply, db=db)
        if asyncio.iscoroutine(reply):
            reply = asyncio.run(reply)
        print(reply)

        # Google Text-to-Speech implementation
        client = texttospeech.TextToSpeechClient.from_service_account_file('config/google_secret_key_tts.json')
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE, name="en-US-Neural2-C"
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        input_text = texttospeech.SynthesisInput(text=reply)

        response = client.synthesize_speech(
            input=input_text, voice=voice, audio_config=audio_config
        )

        audio_content = io.BytesIO(response.audio_content)
        audio_content.seek(0)

        # Create a JSON response with the text reply
        json_response = json.dumps({"text": reply}).encode('utf-8')

        # Combine audio and JSON data
        combined_content = io.BytesIO()
        combined_content.write(json_response)
        combined_content.write(b'\n')  # Add a newline separator
        combined_content.write(audio_content.getvalue())
        combined_content.seek(0)

        end = time.time()
        print(f"Time Elapsed: {end-start}")

        # Return a streaming response with the combined content
        return StreamingResponse(combined_content, media_type='application/octet-stream')
    else:
        return JSONResponse(status_code=400, content={"message": "Invalid input"})
 

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6000, threaded=True)
