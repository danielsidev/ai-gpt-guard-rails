import os
from openai import OpenAI
from typing import List, Dict, Any

# Configure your OPENAI_API_KEY 
try:
    client = OpenAI()
except Exception as e:
    print(f"Error initializing OpenAI client. Check if the API key is configured. Details: {e}")
    exit()


# GPT uses a list of dictionaries to understand context.
# Each dictionary has a 'role' and 'content'.
# 'system' = defines the assistant's persona/behavior.
# 'user' = your message (what you send).
# 'assistant' = GPT's response (what you receive).
MESSAGES_HISTORY: List[Dict[str, str]] = [
    {
        "role": "system", 
        "content": "You're a helpful AI assistant and a Python expert. Please answer clearly and objectively."
    }
]

def send_message(user_input: str) -> str:
    MESSAGES_HISTORY.append({"role": "user", "content": user_input})
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  
            messages=MESSAGES_HISTORY,
            temperature=0.7,      # Creativity level (0.0=focused, 1.0=creative)
        )

        gpt_response_content = response.choices[0].message.content
        
        MESSAGES_HISTORY.append({"role": "assistant", "content": gpt_response_content})
        
        return gpt_response_content

    except Exception as e:
        # Removes the user's last message if the API fails, to avoid polluting the history
        MESSAGES_HISTORY.pop() 
        return f"Error connecting to API: {e}"


if __name__ == "__main__":
    print("--- PYTHON CHATBOT STARTED ---")
    

    pergunta_1 = "What are the three best practices when starting a FastAPI project?"
    print(f"\nUser: {pergunta_1}")
    resposta_1 = send_message(pergunta_1)
    print(f"GPT: {resposta_1}")
    
    # Second message (GPT should use the context of the first question)
    pergunta_2 = "And why is the first one you mentioned so important?"
    print(f"\nUser: {pergunta_2}")
    resposta_2 = send_message(pergunta_2)
    print(f"GPT: {resposta_2}")

    print("\n--- END OF SESSION ---")