"""
Author: Nishant Sharma (nishant@insituate.ai)

File: utilities/llm_utils.py
Description: Implements llm calls
"""

from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import subprocess
import uvicorn
from utilities.utils import *

app = FastAPI()

class InputData(BaseModel):
    utterance: str
    user_name: str
    user_id: str

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
    try:
        return user_login(email=login.email, password=login.password, db=db)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})

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

@app.post("/generate_audio")
async def generate_audio(data: InputData, db: Session = Depends(get_db)):

    try:
        user_input = data.utterance
        user_name = data.user_name
        user_id = data.user_id
        print(user_input)
        conversation_history = read_conversation(user_id=user_id, db=db)
        print(colored(f"conversation_history : {conversation_history}", 'yellow'))
        if user_input:
            # Assuming generate_reply_1 is a function from your utilities module
            reply = await generate_reply_1(user_utterance=user_input, user_id=user_id, user_name=user_name, conversation=conversation_history, db=db)
            add_conversation(user_id=user_id, role=user_name, message=user_input, db=db)
            add_conversation(user_id=user_id, role="Nova", message=reply, db=db)
            # Assuming you have a client instance for your TTS model
            response = openai_client.audio.speech.create(
                model="tts-1-hd",
                voice="fable",
                input=reply,
            )
            # Provide the file path directly to stream_to_file
            output_file_path = "output.mp3"
            response.stream_to_file(output_file_path)
            # Stream the file back to the client
            return FileResponse(
                path=output_file_path,
                filename="output.mp3",
                media_type="audio/mpeg"
            ), 200
        else:
            return JSONResponse(status_code=400, content={"message": "Invalid input"})
        
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})

@app.post("/generate_reply")
async def generate_text(data: InputData, db: Session = Depends(get_db)):

    # try:
    user_input = data.utterance
    user_name = data.user_name
    user_id = data.user_id
    print(user_input)
    conversation_history = read_conversation(user_id=user_id, db=db)
    print(colored(f"conversation_history : {conversation_history}", 'yellow'))
    if user_input:
        # Assuming generate_reply_1 is a function from your utilities module
        reply = await generate_reply_1(user_utterance=user_input, user_id=user_id, user_name=user_name, conversation=conversation_history, db=db)
        add_conversation(user_id=user_id, role=user_name, message=user_input, db=db)
        add_conversation(user_id=user_id, role="Nova", message=reply, db=db)
        response = JSONResponse(status_code=200, content={"message": reply})
        
        # Call generate_summary_and_insights after returning the response
        await generate_summary_and_insights(user_id=user_id, db=db, conversation=conversation_history)
        print(reply)
        return response
    else:
        return JSONResponse(status_code=400, content={"message": "Invalid input"})
    
    # except Exception as e:
    #     return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Internal Server Error"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6000, threaded=True)
