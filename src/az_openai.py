from openai import AzureOpenAI  
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Retrieve credentials from environment variables
api_key = os.getenv("AZURE_OPENAI_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_id = "gpt-4o"
api_version = "2025-01-01-preview"


def create_client():
    # Initialize Azure OpenAI Service client with key-based authentication    
    client = AzureOpenAI(  
        azure_endpoint=endpoint,  
        api_key=api_key,  
        api_version=api_version,
    )

    return client

def generate_response(client, text, instructions):
    #Prepare the chat prompt 
    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": instructions
                }
            ]
        }
    ] + [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": text
                }
            ]
        }
    ]

    # Generate the completion  
    completion = client.chat.completions.create(  
        model=deployment_id,
        messages=messages,
        max_tokens=800,  
        temperature=0.7,  
        top_p=0.95,  
        frequency_penalty=0,  
        presence_penalty=0,
        stop=None,  
        stream=False
    )

    # Extract the response from the completion
    return completion.choices[0].message.content
