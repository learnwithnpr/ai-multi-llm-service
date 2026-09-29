from openai import OpenAI
from dotenv import load_dotenv
import json
from tools_definition import tools, tools_available


load_dotenv()


def openai_agent():

    client = OpenAI()

    response = client.responses.create(
        model="gpt-4o-mini",
        input="If I buy 2 Apple AirPods Pro with WELCOME10 discount, what is the final price?",
        tools=tools,
        tool_choice="auto"
    )

    max_steps = 5
    step = 0

    print("-----------------Response 1st----------------")
    print(response)
    print("-----------------Response 1st----------------")

    print("-----------------Response output----------------")
    print(response.output)
    print("-----------------Response output----------------")


    while step < max_steps:
        step += 1
        print("step :", step)

        has_tool_call = False
        tools_output = []

        for item in response.output:
            if item.type == "function_call":
                has_tool_call = True
                tool = tools_available[item.name]
                arguments = json.loads(item.arguments)
                result = tool(**arguments)
                tools_output.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(result)
                })

            elif item.type == "message":
                for text_chunk in item.content:
                    print(f"\n Agent: {text_chunk.text}")
        print("-----------------tools output----------------")
        print(tools_output)
        print("-----------------tools output----------------")

        if not has_tool_call:
            break

        response = client.responses.create(
            model="gpt-4o-mini",
            input=tools_output,
            previous_response_id=response.id
        )


if __name__ == "__main__":
    openai_agent()
