import os
import json
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import List, Optional

# Configure your OPENAI_API_KEY 
client = OpenAI()


class FactCard(BaseModel):
    claim: str = Field(description="A afirmação factual curta e verificável.")
    provenance: Optional[str] = Field(None, description="Brief description of how the statement was obtained (e.g., 'Wikipedia', 'Report X').")
    year: Optional[int] = Field(None, description="Year related to the claim, if applicable.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence estimated by the model (0.0 to 1.0).")
    sources: List[str] = Field(default_factory=list, description="URLs or short references that support the claim. Required if confidence > 0.5")
    note: Optional[str] = Field(None, description="If the model doesn't know, it should put 'unknown' here and low confidence.")

    @field_validator("sources")
    def sources_required_if_confident(cls, v, info):
        conf = info.data.get("confidence", 0.0)
        if conf > 0.5 and (not v or len(v) == 0):
            raise ValueError("If confidence > 0.5, 'sources' cannot be empty.")
        return v

    @field_validator("year")
    def year_must_be_reasonable(cls, v):
        if v is None:
            return v
        if v < 0 or v > 2100:
            raise ValueError("year outside the plausible range.")
        return v

# --- 2) Prompt rígido que minimiza inventos ---
SYSTEM_PROMPT = """
You are a factual assistant. Always respond strictly in JSON, following the provided schema.
- If the information is uncertain, put "unknown" in the 'note' field and set confidence <= 0.5.
- NEVER invent source names or URLs. If there is no source, leave 'sources' empty and confidence low.
- Do not provide explanations outside of JSON.
"""

def generate_fact_card(query: str):
    schema = FactCard.model_json_schema()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Please generate a verifiable JSON object about: {query}. Return only JSON."}
    ]

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            # I used a "function" to force structured output (optional depending on your SDK/version)
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "fact_card",
                        "description": "Tool that produces FactCard objects in JSON.",
                        "parameters": schema
                    },
                }
            ],
            tool_choice={"type": "function", "function": {"name": "fact_card"}},
            response_format={"type": "json_object"}, 
            temperature=0.0  
        )

        # Extracts the tool call (it depends on how the SDK returns the field)
        tool_call = resp.choices[0].message.tool_calls[0]
        args_json = tool_call.function.arguments
        data = json.loads(args_json)

        fact = FactCard(**data)

        if fact.confidence <= 0.5:
            print("INFO: Model stated low confidence — do not accept unverified facts.")
            return fact.model_dump()

        for s in fact.sources:
            if not (s.startswith("http://") or s.startswith("https://")):
                # suspicious source -> consider it as a possibility of hallucination
                print("WARNING: Source without valid URL detected — treating as untrusted.")
                fact.confidence = 0.45
                fact.note = "source_format_invalid"
                fact.sources = []
                return fact.model_dump()


        print("✅ FactCard validado e plausível.")
        return fact.model_dump()

    except ValidationError as ve:
        print("❌ ValidationError: Output did not conform to schema. Treating as 'unknown'.")
        return {"claim": query, "confidence": 0.0, "sources": [], "note": "unknown_validation_failed"}
    except json.JSONDecodeError:
        print("❌ Invalid JSON returned by the model..")
        return {"claim": query, "confidence": 0.0, "sources": [], "note": "unknown_json_invalid"}
    except Exception as e:
        print(f"❌ Error in API call or processing: {e}")
        return {"claim": query, "confidence": 0.0, "sources": [], "note": "unknown_api_error"}


if __name__ == "__main__":
    consult = "In what year was the International Space Station (ISS) launched?"
    result = generate_fact_card(consult)
    print("\nResultado final:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
