#This example demonstrates an interactive chat session using the requests library:

import json
import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True) # Load env vars, .env takes precedence

APPKEY = os.getenv("BRIDGE_API_APP_KEY")
api_key = os.getenv("AZURE_OPENAI_API_KEY") # This is your access token

MODEL_NAME = "gpt-4o"
API_URL = f"https://chat-ai.cisco.com/openai/deployments/{MODEL_NAME}/chat/completions?api-version=2025-04-01-preview"

def chat_with_circuit():
   print("Cisco CircuIT GPT Chatbot (type 'exit' to quit)")
   messages = [{"role": "system", "content": "You are a helpful assistant."}]
   headers = {
      'Content-Type': 'application/json',
      'api-key': api_key
   }

   while True:
       user_input = input("You: ")
       if user_input.lower() in {"exit", "quit"}:
           break

       messages.append({"role": "user", "content": user_input})

       payload = {
           "user": json.dumps({"appkey": APPKEY}),
           "messages": messages
       }

       try:
           response = requests.post(API_URL, json=payload, headers=headers)
           response.raise_for_status()
           data = response.json()
           reply = data["choices"]["message"]["content"]
           messages.append({"role": "assistant", "content": reply})
           print("AI:", reply.strip())

       except requests.exceptions.HTTPError as e:
           print("API request error:", e)
           print("Status code:", e.response.status_code)
           print("Response content:", e.response.text)
       except requests.exceptions.RequestException as e:
           print("API request error:", e)
           break
       except (KeyError, IndexError) as e:
           print("Unexpected response format:", e)
           break

if __name__ == "__main__":
   chat_with_circuit()


  # When using Azure, this uses the OpenAI Python SDK specifically for Azure-hosted models:

import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()
appkey = os.getenv("BRIDGE_API_APP_KEY")
access_token = os.getenv("AZURE_OPENAI_API_KEY") # Your access token

client = AzureOpenAI(
   azure_endpoint = 'https://chat-ai.cisco.com/',
   api_key = access_token, # Can also be set via AZURE_OPENAI_API_KEY env var
   api_version="2025-04-01-preview", # Can also be set via OPENAI_API_VERSION env var
)
messages = [
   {"role": "system", "content": "You are a helpful assistant."}
]

user_input = input("You: ")
messages.append({"role": "user", "content": user_input})

response = client.chat.completions.create(
   model="gpt-4o", # Model name
   messages = messages,
   temperature = 0,
   user=f'{{"appkey": "{appkey}", "user": "ddamerji@cisco.com"}}' # Optional user ID
)

print(response.choices.message.content)

# This LangChain wrapper provides a tailored experience for conversational AI applications:

from langchain_openai import AzureChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv

load_dotenv()
app_key = os.getenv("BRIDGE_API_APP_KEY")
userid = os.getenv("CISCO_BRAIN_USER_ID") # Your Cisco CEC ID
access_token = os.getenv("AZURE_OPENAI_API_KEY") # Your access token

model = AzureChatOpenAI(
   model="gpt-4.1", # Model name
   azure_endpoint = 'https://chat-ai.cisco.com',
   api_version="2024-12-01-preview",
   openai_api_key=access_token, # Pass the access token
   model_kwargs=dict(
       user = f'{{"appkey": "{app_key}", "user": "{userid}"}}'
   )
)

msgs = [
   SystemMessage(content="You are a helpful assistant."),
   HumanMessage(content="Translate to French: Hello, how are you?")
]

print (model.invoke(msgs)) # Recommended approach
print (model.invoke("Tell me who is the president of USA for 2024"))