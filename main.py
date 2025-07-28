import requests
import os
import json

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from services import city_information_agent

# TODO: Add logging
load_dotenv()
app = FastAPI()

class Message(BaseModel):
    id: str
    new_message: str
    messages: list

@app.post("/send_message")
def pots_message(req: Message):
    try:
      return StreamingResponse(city_information_agent(req))
    except Exception as error:
       raise HTTPException(status_code=500, detail="Something went wrong")