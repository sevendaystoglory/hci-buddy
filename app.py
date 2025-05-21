"""
Author: Nishant Sharma (nishant@insituate.ai)

File: utilities/llm_utils.py
Description: Implements llm calls
"""

from fastapi import FastAPI, Request, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from pydantic import BaseModel
import subprocess
import uvicorn
from utilities.utils import *
import asyncio
import time
from datetime import datetime, timedelta

app = FastAPI()

class InputData(BaseModel):
    utterance: str
    user_name: str
    user_id: str
    character: str

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

class ContinuousInputData(BaseModel):
    transcription: str
    question: str
    user_id: str
    user_name: str
    character: str
    
class ChatbotFeatures(BaseModel):
    name: str
    gender: str
    interaction_style: str
    emotional_support: str
    learning_approach: str
    problem_solving: str
    tone: str
    expertise: str
    
    
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

    transcription = str(read_transcription(user_id=data.user_id, db=db))[:20000]
    conversation_history = read_conversation(user_id=user_id, db=db)
    print(colored(f"conversation_history : {conversation_history}", 'yellow'))

    if user_input:

        reply = await generate_reply_1(user_utterance=user_input, user_id=user_id, user_name=user_name, conversation=conversation_history, db=db, transcription=transcription)
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
    print(colored(f"data : {data}", 'red'))
    user_input = data.utterance
    user_name = data.user_name
    user_id = data.user_id
    character = data.character

    conversation_history = read_conversation(user_id=user_id, db=db)
    transcription = str(read_transcription(user_id=data.user_id, db=db))[:20000]
    print(colored(f"conversation_history : {conversation_history}", 'yellow'))

    if user_input:
        reply = await generate_reply_1(user_utterance=user_input, user_id=user_id, user_name=user_name, conversation=conversation_history, db=db, transcription=transcription)
        add_conversation(user_id=user_id, role=user_name, message=user_input, db=db)
        add_conversation(user_id=user_id, role=buddy_name, message=reply, db=db)

        if asyncio.iscoroutine(reply):
            reply = asyncio.run(reply)  
        print(reply)
        # Google Text-to-Speech implementation
        speech, audio_type = generate_text_to_speech(reply, character)
        
        combined_content = prepare_combined_content(reply, speech, audio_type)

        end = time.time()
        print(f"Time Elapsed: {end-start}")

        # Return a streaming response with the combined content
        # return JSONResponse(status_code=500, content={"message": "Invalid input"})
        return StreamingResponse(combined_content, media_type='application/octet-stream')
    else:
        return JSONResponse(status_code=400, content={"message": "Invalid input"})

@app.post("/generate_response_continuous")
async def generate_response_continuous(data: ContinuousInputData, db: Session = Depends(get_db)):
    start = time.time()
    character = data.character

    print(f"User ID: {data.user_id}")
    print(f"Transcription: {data.transcription}")
    print(f"Question: {data.question}")

    # Use current time if start_time is not provided
    start_time = datetime.utcnow()
    # Set end_time to 5 minutes after start_time
    end_time = start_time + timedelta(minutes=5)
    add_transcription(user_id=data.user_id, transcription=data.transcription, start_time=start_time, end_time=end_time, db=db)
    transcription = str(read_transcription(user_id=data.user_id, db=db))[:20000]
    conversation_history = read_conversation(user_id=data.user_id, db=db)

    if data.question:
        reply = await generate_reply_1(user_utterance=data.question, user_id=data.user_id, user_name=data.user_name, conversation=conversation_history, db=db, transcription=transcription)
        add_conversation(user_id=data.user_id, role=data.user_name, message=data.question, db=db)
        add_conversation(user_id=data.user_id, role=buddy_name, message=reply, db=db)
                
        if asyncio.iscoroutine(reply):
            reply = asyncio.run(reply)
        print(reply)

        # Google Text-to-Speech implementation
        speech, audio_type = generate_text_to_speech(reply, character)
        
        combined_content = prepare_combined_content(reply, speech, audio_type)

        end = time.time()
        print(f"Time Elapsed: {end-start}")

        # Return a streaming response with the combined content
        return StreamingResponse(combined_content, media_type='application/octet-stream')
    else:
        return JSONResponse(status_code=400, content={"message": "Invalid input: Question is required"})

@app.post("/generate_response_continuous_v2")
async def generate_response_continuous_v2(
    data: ContinuousInputData = Depends(),
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    start = time.time()
    user_id = data.user_id
    user_name = data.user_name
    character = data.character
    question = data.question

    print(f"User ID: {user_id}")
    print(f"Question: {question}")

    # Read the uploaded audio file
    audio_content = await audio_file.read()

    # Convert audio to text
    transcription = convert_audio_to_text(audio_content)
    print(f"Transcription: {transcription}")

    # Use current time if start_time is not provided
    start_time = datetime.utcnow()
    # Set end_time to 5 minutes after start_time
    end_time = start_time + timedelta(minutes=5)
    add_transcription(user_id=user_id, transcription=transcription, start_time=start_time, end_time=end_time, db=db)
    full_transcription = str(read_transcription(user_id=user_id, db=db))[:20000]
    conversation_history = read_conversation(user_id=user_id, db=db)

    if data.question:
        reply = await generate_reply_1(user_utterance=question, user_id=user_id, user_name=user_name, conversation=conversation_history, db=db, transcription=full_transcription)
        add_conversation(user_id=user_id, role=user_name, message=question, db=db)
        add_conversation(user_id=user_id, role=buddy_name, message=reply, db=db)
                
        if asyncio.iscoroutine(reply):
            reply = await reply
        print(reply)

        # Google Text-to-Speech implementation
        speech, audio_type = generate_text_to_speech(reply, character)
        
        combined_content = prepare_combined_content(reply, speech, audio_type)

        end = time.time()
        print(f"Time Elapsed: {end-start}")

        # Return a streaming response with the combined content
        return StreamingResponse(combined_content, media_type='application/octet-stream')
    else:
        return JSONResponse(status_code=400, content={"message": "Invalid input: Question is required"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6000, threaded=True)
