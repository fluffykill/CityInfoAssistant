import json

from tools import TOOL_MAPPING

def run_tools(messages, tool_calls, function_call_list):
  for tool_call in tool_calls:
    tool_name = tool_call.get("function",{}).get("name","")
    tool_args = json.loads(tool_call.get("function",{}).get("arguments",""))
    tool_response = TOOL_MAPPING[tool_name](**tool_args)
    function_call_list.append({"tool": tool_name, "parameters": tool_args })
    messages.append({
      "role": "tool",
      "tool_call_id": tool_call.get("id",""),
      "name": tool_name,
      "content": json.dumps(tool_response),
    })