import os
import json
from openai import OpenAI
from pydantic import BaseModel, Field

# using pydantic for validate output like a guardrails for a correct structure
# Configure your OPENAI_API_KEY 
client = OpenAI()

class BookCard(BaseModel):
    """
    Represents the structured data of a specific book.
    """
    title: str = Field(description="The full title of the book.")
    author: str = Field(description="The author's full name.")
    year_publication: int = Field(description="O ano em que o livro foi originalmente publicado.")
    genre: str = Field(description="The year the book was originally published.")
    short_summary: str = Field(description="A one-sentence summary of the book.")


def generate_book_card_with_tools(tema: str) -> dict:
    schema_params = BookCard.model_json_schema()

    messages = [
        {
            "role": "system",
            "content": "You are a wizard that generates book datasheets. Your output should ALWAYS be JSON that matches the provided schema.",
        },
        {
            "role": "user",
            "content": f"Generate a fictitious book sheet on the topic: {tema}",
        },
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "BookCard",
                        "description": "Generates a complete, structured data sheet for a fictional book.",
                        "parameters": schema_params,  # <-- aqui sim: JSON Schema válido
                    },
                }
            ],
            tool_choice={"type": "function", "function": {"name": "BookCard"}},
            temperature=0.5
        )

        tool_call = response.choices[0].message.tool_calls[0]
        arguments_json = tool_call.function.arguments
        data = json.loads(arguments_json)

        validated_file = BookCard(**data)  # Pydantic validate

        print("\n✅ JSON output successfully validated by Pydantic!")
        return validated_file.model_dump()

    except json.JSONDecodeError:
        print("\n❌ ERROR: GPT returned text that is NOT valid JSON.")
        return None
    except Exception as e:
        print(f"\n❌ ERROR: JSON is valid but did not follow the Pydantic schema (or other API error): {e}")
        return None



if __name__ == "__main__":
    book_card = "A robot detective in a dystopian future"
    
    print(f"Asking for a book about: '{book_card}'...")
    card = generate_book_card_with_tools(book_card)

    if card:
        print("\n--- Generated Book Record (Reliable Data) ---")
        for key, value in card.items():
            print(f" - {key.capitalize()}: {value}")
        print("-------------------------------------------------")
