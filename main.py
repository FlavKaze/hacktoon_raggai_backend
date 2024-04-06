import os
import sys
import pickle
from typing import List

import ollama
from ollama import Client

import uvicorn
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.logger import logger
from pyngrok import ngrok

import config
from app import db

app = FastAPI()
table_name = "embbedings"

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Settings(BaseSettings):
    # ... The rest of our FastAPI settings

    BASE_URL: str = "http://localhost:8001"
    USE_NGROK: bool = os.environ.get("USE_NGROK", "False") == "True"


settings = Settings()


def init_webhooks(base_url):
    # Update inbound traffic via APIs to use the public-facing ngrok URL
    pass


if settings.USE_NGROK and os.environ.get("NGROK_AUTHTOKEN"):
    # pyngrok should only ever be installed or initialized in a dev environment when this flag is set
    

    # Get the dev server port (defaults to 8000 for Uvicorn, can be overridden with `--port`
    # when starting the server
    port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else "8001"

    # Open a ngrok tunnel to the dev server
    public_url = ngrok.connect(port).public_url
    logger.info(f"ngrok tunnel \"{public_url}\" -> \"http://127.0.0.1:{port}\"")

    # Update any base URLs or webhooks to use the public ngrok URL
    settings.BASE_URL = public_url
    init_webhooks(public_url)


client = Client(host='https://bff5-34-70-133-48.ngrok-free.app')


def chat_inference(message, context):
    context = '\n- '.join(context)
    prompt = f"""
    Given only the following information :

    -{context}

    answer the following question: {message}

    if the answer can't be found in the texts above, respond "I don't know"
"""

    response = client.chat(model='mistral', messages=[
        {
            'role': 'user',
            'content': prompt,
        },
    ])

    return response['message']['content']



class Message(BaseModel):
    message_id: str
    message: str

class Chat(BaseModel):
    chat_id: str
    messages: List[Message]
    

@app.get("/")
async def root():
    return {}

@app.post("/query")
async def query(chat: Chat) -> Message:
    message = chat.messages[-1]

    embeddings = ollama.embeddings(
        model='mxbai-embed-large',
        prompt=message.message
    )

    result = db.search(table_name, "raggaidb", embeddings["embedding"], limit=3)

    response = chat_inference(message=message.message, context=result.get("text").tolist())
    filename = result.get("filename").tolist()[0].split(".txt")[0]
    response = f"{response}- urlhttps://simpsons.fandom.com/wiki/{filename}"
    return Message(message_id="None", message=response)

if __name__ == "__main__":
    if os.listdir("database") == []:
        table_name = "embbedings"
        data_info = pickle.load(open("data.pkl", "rb"))
        db.create_table(table_name, uri="raggaidb", data=data_info)

    uvicorn.run(app, host="localhost", port=8001, workers=1)