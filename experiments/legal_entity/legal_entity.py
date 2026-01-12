import json
import os
from typing import Optional, Dict
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv

from project_gamma.src.gamma.util.util import normalize


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

JSON_FILE = os.path.join(
    os.path.dirname(__file__),
    "legal_entities.json"
)

cache: Dict[str, str] = {}

class legalModel(BaseModel):
    legal_name: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)

def look() -> Dict[str, Dict]:
    if not os.path.exists(JSON_FILE): return {}
    if os.path.getsize(JSON_FILE) == 0: return {}
    with open(JSON_FILE, "r") as f:
        return json.load(f)

def put(store: Dict[str, Dict]):
    with open(JSON_FILE, "w") as f:
        json.dump(store, f, indent=4)
        
def callLLM(cpty: str) -> legalModel:
    resp = client.responses.create(
        model="gpt-4.1",
        input=[
            {
                "role": "system",
                "content": (
                    "You are an entity normalization system. "
                    "If given name is not a company name, return empty for all fields."
                    "Given a company name, return:\n"
                    "1. The official registered legal entity name\n"
                    "2. The registered city and state (or country if state not applicable)\n\n"
                    "Rules:\n"
                    "- Use government business registry information only (MCA India, SEC US, Companies House UK).\n"
                    "- DO NOT provide street names, building numbers, or postal addresses.\n"
                    "- Output ONLY city and state/country.\n"
                    "Return STRICT JSON with keys: legal_name, location."
                ),
            },
            {"role": "user", "content": cpty},
        ],
    )

    text = resp.output_text
    data = json.loads(text)
    return legalModel(**data)


def Legalise(cpty: str):
    global cache

    norm_cpty = normalize(cpty)

    store = look()
    cache = {
        normalize(name): legal
        for legal, data in store.items()
        for name in data.get("known_as", [])
    }

    canonical = cache.get(norm_cpty)
    if canonical:
        return store[canonical]

    resolved = callLLM(cpty).model_dump()
    legal = resolved.get("legal_name")

    if not legal:
        return resolved

    if legal in store:
        known = store[legal].get("known_as", [])
        if norm_cpty not in map(normalize, known):
            store[legal]["known_as"].append(norm_cpty)
    else:
        store[legal] = {
            "legal_name": legal,
            "location": resolved.get("location"),
            "known_as": [norm_cpty],
        }

    put(store)
    cache[norm_cpty] = legal

    return store[legal]

if __name__ == '__main__':
    print(Legalise(input()))
