import os
import json
import requests

from tools import TOOLS_DEFINITION
from utils import run_tools

OPEN_ROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY")
OPEN_ROUTER_URL = os.getenv("OPEN_ROUTER_URL")
OPEN_ROUTER_MODEL = os.getenv("OPEN_ROUTER_MODEL")

SYSTEM_PROMPT = "You are a city information assistant that helps users gather factual information about cities, such as weather, current local time, and basic facts"

async def city_information_agent(req):
  try:
    messages = [
      {"role": "system", "content": SYSTEM_PROMPT}
    ]
    if req.messages:
        messages+=req.messages
    messages.append({"role": "user", "content": req.new_message})
    function_call_list = []
    response = {
      "thinking": "",
      "function_calls": function_call_list,
      "response": "",
      "messages": messages
    }

    headers = {
        "Authorization": f"Bearer {OPEN_ROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": OPEN_ROUTER_MODEL,
        "messages": messages,
        "reasoning": {"effort": "low"},
        "tools": TOOLS_DEFINITION
    }
    llm_response = requests.post(OPEN_ROUTER_URL, headers=headers, data=json.dumps(payload))
    data=llm_response.json()
    llm_message = data.get("choices",[{}])[0].get("message",{})
    llm_error = data.get("choices",[{}])[0].get("error")
    if llm_response.status_code != 200 or llm_error:
        print(req.id,'--',data)
        yield json.dumps(data)
    response["thinking"] = llm_message.get("reasoning", "")
    yield json.dumps(response)

    # TODO: Maybe add a cap on number of tool calls to reduce llm demand
    while(llm_message.get("tool_calls")):
      messages.append(llm_message)
      run_tools(messages, llm_message.get("tool_calls",{}), function_call_list)
      llm_response = requests.post(OPEN_ROUTER_URL, headers=headers, data=json.dumps(payload))
      data=llm_response.json()
      llm_error = data.get("choices",[{}])[0].get("error") 
      if llm_response.status_code != 200 or llm_error:
        print(req.id,'--',data)
        yield json.dumps(data)
      llm_message = data.get("choices",[{}])[0].get("message",{})
      response["thinking"] = llm_message.get("reasoning", "")
      yield json.dumps(response)

    messages.append(llm_message)
    response["response"] = llm_message.get("content","")
    yield json.dumps(response)
  except Exception as error:
    print(req.id,"-",error)
    err_resp = {
      "id": req.id,
      "error": str(error)
    }
    yield json.dumps(err_resp)