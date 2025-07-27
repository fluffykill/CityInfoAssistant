import requests
import os
import json

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from tools import TOOL_MAPPING
from utils import run_tools

load_dotenv()
app = FastAPI()

OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")
OPEN_ROUTER_URL = os.getenv("OPEN_ROUTER_URL")
OPEN_ROUTER_MODEL = os.getenv("OPEN_ROUTER_MODEL")

class Message(BaseModel):
    id: str
    new_message: str
    messages: list

SYSTEM_PROMPT = "You are a city information assistant that helps users gather factual information about cities, such as weather, current local time, and basic facts"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_city_local_time",
            "description": "Gets the current local time for provided area and location",
            "parameters": {
                "type": "object",
                "properties": {
                    "area": {"type": "string","description": "The area usually a continent e.g. America or Europe"},
                    "location": {"type": "string", "description": "The location usually a city e.g. Toronto"},
                },
                "required": ["area", "location"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_city_weather",
            "description": "Get current temperature in celsius for provided coordinates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                },
                "required": ["latitude", "longitude"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_city",
            "description": "Finds the city wikiDataId for cities with a minimum population of 1000000 given the prefix of it's name",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                },
                "required": ["name"],
                "additionalProperties": False,
            },
            "strict": True,
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_city_details",
            "description": "Get basic city facts (e.g., country, population, description) from a wikiDataId",
            "parameters": {
                "type": "object",
                "properties": {
                    "wikiDataId": {"type": "string", "details": "The wikiDataId returned from the find_city tool"},
                },
                "required": ["wikiDataId"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
]

@app.post("/send_message")
def pots_message(req: Message):
    try:
      messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
      ]
      if req.messages:
          messages+=req.messages
      messages.append({"role": "user", "content": req.new_message})
      function_call_list = []

      headers = {
          "Authorization": f"Bearer {OPEN_ROUTER_API_KEY}",
          "Content-Type": "application/json"
      }
      payload = {
          "model": OPEN_ROUTER_MODEL,
          "messages": messages,
          "reasoning": {"effort": "medium"},
          "tools": TOOLS
      }
      response = requests.post(OPEN_ROUTER_URL, headers=headers, data=json.dumps(payload))
      data=response.json()
      llm_message = data.get("choices",[{}])[0].get("message",{})
      llm_error = data.get("choices",[{}])[0].get("error")
      if response.status_code != 200 or llm_error:
          print(req.id,'--',data)
          return data

      response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="How does AI work?",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0) # Disables thinking
        ),
      )

      while(llm_message.get("tool_calls")):
        messages.append(llm_message)
        run_tools(messages, llm_message.get("tool_calls",{}), function_call_list)
        response = requests.post(OPEN_ROUTER_URL, headers=headers, data=json.dumps(payload))
        data=response.json()
        llm_error = data.get("choices",[{}])[0].get("error") 
        if response.status_code != 200 or llm_error:
          print(req.id,'--',data)
          return data
        llm_message = data.get("choices",[{}])[0].get("message",{})
      messages.append(llm_message)
      response = {
          "response": llm_message.get("content",""),
          "function_calls": function_call_list,
          "thinking": llm_message.get("reasoning", "")
      }
      return response
    except Exception as error:
       return {
          "id": req.id,
          "error": error
       }
