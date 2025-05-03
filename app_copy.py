from fastapi import FastAPI
from pydantic import BaseModel
import openai
import json
import requests
from call_rag_func_new import Insurance_Agent_Rag
from bs4 import BeautifulSoup

from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize FastAPI app
app = FastAPI()




# Agent functions
def agent_about_myself(prompt):
    print('... running agent_about_myself')
    return ("""I am Developed and Designed by AI/ML enthusiast named Kamran. I'm an AI language model created to assist with a variety of tasks and answer questions.
            I can provide information on a wide range of topics, help with problem-solving, offer suggestions,
            and even engage in creative writing. If you have any specific questions or need assistance, feel free to ask!""")


    
def agent_get_weather(latitude, longitude):
    print('... running agent_get_weather')
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    )
    data = response.json()
    return f"The current temperature is {data['current_weather']['temperature']}°C."

def agent_addition(num1, num2):
    print('... running agent_addition')
    return f"The sum is {num1 + num2}."

def agent_substraction(num1, num2):
    print('... running agent_substraction')
    return f"The result of subtraction is {num1 - num2}."

def best_ai_practices(prompt):
    print('... running best_ai_practices')
    URL = 'https://training.safetyculture.com/blog/ai-best-practices/'
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, 'html.parser')
    section = soup.find('section', class_='sc-8a6eda5-9 bBycdY')
    if section:
        h2_tags = section.find_all('h2')
        best_list = [tag.text for tag in h2_tags]
        return f"AI Best Practices:\n" + "\n".join(best_list)
    return "Could not find best AI practices."


# Define function registry
function_registry = {
    "agent_about_myself":agent_about_myself,
    "agent_get_weather": agent_get_weather,
    "agent_addition": agent_addition,
    "agent_substraction": agent_substraction,
    "Insurance_Agent_Rag": Insurance_Agent_Rag,
    "best_ai_practices": best_ai_practices
}


# Define function schemas
tools = [
        {
        "type": "function",
        "name": "agent_about_myself",
        "description": "Explaining about myself",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string"}
            },
            "required": ["prompt"]
        }
    },
    
    {
        "type": "function",
        "name": "agent_get_weather",
        "description": "Get current temperature for provided coordinates in Celsius.",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number"},
                "longitude": {"type": "number"}
            },
            "required": ["latitude", "longitude"]
        }
    },
    {
        "type": "function",
        "name": "agent_addition",
        "description": "Add two numbers.",
        "parameters": {
            "type": "object",
            "properties": {
                "num1": {"type": "number"},
                "num2": {"type": "number"}
            },
            "required": ["num1", "num2"]
        }
    },
    {
        "type": "function",
        "name": "agent_substraction",
        "description": "Subtract two numbers.",
        "parameters": {
            "type": "object",
            "properties": {
                "num1": {"type": "number"},
                "num2": {"type": "number"}
            },
            "required": ["num1", "num2"]
        }
    },
    {
        "type": "function",
        "name": "Insurance_Agent_Rag",
        "description": "you are an expert who knows everything about hospitals and doctors",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string"}
            },
            "required": ["prompt"]
        }
    },
    {
        "type": "function",
        "name": "best_ai_practices",
        "description": "Retrieve best practices for AI development.",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string"}
            },
            "required": ["prompt"]
        }
    }
]


def get_ai_response(prompt):
    response = openai.responses.create(
        model="gpt-4.1-nano",
        input=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        tools=tools
    )
    return response.output[0]



# Define request model
class PromptRequest(BaseModel):
    prompt: str

# Define chat endpoint
@app.post("/chat/")
async def chat_with_bot(req: PromptRequest):
    try:
        # 🧠 Parse the tool call
        tool_call = get_ai_response(req.prompt)
        print("\n------------------------\n")
        print(tool_call)
        print("\n------------------------\n")

        function_name = tool_call.name
        args = json.loads(tool_call.arguments)
        
        # 🔁 Call the function dynamically
        if function_name in function_registry:
            result = function_registry[function_name](**args)
            # print(f"Result from '{function_name}':", result)
            return result
        else:
            print("Function not found.")
    except:
        exception_chat = get_ai_response(req.prompt)
        return (exception_chat.content[0].text)

# Define root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the chatbot API!"}
