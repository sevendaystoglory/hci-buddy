from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from utilities.utils import get_db, read_conversation, add_conversation, generate_reply_1
from sqlalchemy.orm import Session
import concurrent.futures
import time
from termcolor import colored

app = FastAPI()

class InputData(BaseModel):
    utterance: str
    user_name: str
    user_id: str

@app.post("/generate_reply")
async def generate_text(data: InputData, db: Session = Depends(get_db)):
    start = time.time()
    
    user_input = data.utterance
    user_name = data.user_name
    user_id = data.user_id
    time.sleep(0.999)
    end = time.time()
    print(end-start)
    return JSONResponse(status_code=200, content={"message": "Your name is Atif. Uperman. Batman. Spiderman."})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6000)