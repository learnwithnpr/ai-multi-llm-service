from zoneinfo import ZoneInfo
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import json
from typing import Optional

load_dotenv()

client= OpenAI()

def current_date_and_time(timezone: str):
    now = datetime.now(ZoneInfo(timezone))
    return {
        "current_date":now.strftime("%Y-%m-%d"),
        "current_time":now.strftime("%H:%M:%S %p %Z"),
        "timezone":timezone
    }

def calculator( operation: str, a: float, b: float, c: float):
    if operation == "add":
        return a+b+c
    elif operation == "subtract":
        return a-b-c
    elif operation == "multiply":
        return a*b*c
    elif operation == "divide":
        return a/b/c
    else:
        return "Invalid operation"
    
    


tools=[{
    "type": "function",
    "name":"get_current_date_time",
    "description":"Returns the current date and time in the given timezone",
    "parameters":{"type":"object", 
                  "properties":{
                    "timezone":{"type":"string"}}, 
                    "required":["timezone"]
                    
                }
},
    
    {
    "type":"function",
     "name":"calculator",
     "description":"Performs a basic arithmetic operation on three numbers",
     "parameters":{"type":"object",
                   "properties":{
                    "operation":{"type":"string"},
                    "a":{"type":"number"},
                    "b":{"type":"number"},
                    "c":{"type":"number"}
                    },
                   "required":["operation","a","b","c"]
                },
    }
]

available_tools = {"get_current_date_time" : current_date_and_time, "calculator":calculator}

response = client.responses.create(model='gpt-4o-mini', input= "what is 10+89+54??", tools=tools)


print(response)

for item in response.output:
    if item.type == "function_call":
        tool = available_tools[item.name]
        arguments = json.loads(item.arguments)
        result = tool(**arguments)
        response = client.responses.create(model="gpt-4o-mini", input=[{"type":"function_call_output", "call_id":item.call_id, "output":json.dumps(result)}], previous_response_id=response.id)
        print(response.output)
        





# print(response)
