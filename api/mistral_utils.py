from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_mistral_client():
    try:
        api_key = os.getenv('MISTRAL_API_KEY')
        if not api_key:
            raise ValueError("Mistral API key not found in environment variables")
        return MistralClient(api_key=api_key)
    except Exception as e:
        print(f"Error in get_mistral_client: {str(e)}")
        raise

def generate_answer(query, context):
    try:
        client = get_mistral_client()
        
        # Prepare the prompt with context
        messages = [
            ChatMessage(role="system", content="You are a helpful AI assistant that provides concise and accurate answers based on the given context."),
            ChatMessage(role="user", content=f"Query: {query}\n\nContext: {context}\n\nPlease provide a clear and concise answer based on this information.")
        ]
        
        # Get response from Mistral
        chat_response = client.chat(
            model="mistral-tiny",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return chat_response.choices[0].message.content
    except Exception as e:
        print(f"Error in generate_answer: {str(e)}")
        raise 