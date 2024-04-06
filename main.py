import os
import pickle
from typing import List

import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config
from app import db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    message_id: int
    message: str

class Chat(BaseModel):
    chat_id: str
    messages: List[Message]
    

@app.get("/")
async def root():
    return {}

@app.post("/query")
async def query(chat: Chat) -> Message:
    table_name = "embbedings"
    message = chat.messages[-1]

    # pass message in embbeding model
    message_vector = [1, 2, 3]

    db.search(table_name, "raggaidb", message_vector, limit=3)
    return Message(message_id=None, message="Hello, World!")

if __name__ == "__main__":
    if os.listdir("database") == []:
        table_name = "embbedings"
        data_info = pickle.load(open("data_info.pkl", "rb"))
        db.insert(table_name, uri="raggaidb")

    uvicorn.run(app, host="localhost", port=8000, workers=1)