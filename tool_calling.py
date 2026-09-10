from zoneinfo import ZoneInfo
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

client= OpenAI()

def current_date_and_time(timezone: str):
    now = datetime.now(ZoneInfo(timezone))
    return {
        "current_date":now.strftime("%Y-%m-%d"),
        "current_time":now.strftime("%H:%M:%S %p %Z"),
        "timezone":timezone
    } 

tools=[{
    "type": "function",
    "name":"get_current_date_time",
    "description":"Returns the current date and time in the given timezone",
    "parameters":{"type":"object", 
                  "properties":{
                    "timezone":{"type":"string"}}, 
                    "required":["timezone"]
                    
                }
}]

available_tools = {"get_current_date_time" : current_date_and_time}

response = client.responses.create(model='gpt-4o-mini', input= "what is the current date and time in texas, US??", tools=tools)

for item in response.output:
    if item.type == "function_call":
        tool = available_tools[item.name]
        arguments = json.loads(item.arguments)
        result = tool(**arguments)
        response = client.responses.create(model="gpt-4o-mini", input=[{"type":"function_call_output", "call_id":item.call_id, "output":json.dumps(result)}], previous_response_id=response.id)
        print(response.output)
        





# print(response)
