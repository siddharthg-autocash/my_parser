# uvicorn api:app --reload 

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from script import CTPTY,parse

# -----------------------------
# Request / Response Models
# -----------------------------
class CTPTYRequest(BaseModel):
    narrative: str
    amount: Optional[float] = None


class CTPTYResponse(BaseModel):
    format: str
    parsed: Dict[str, Any]
    ctpty: Dict[str, Any]


# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(
    title="CTPTY Resolution Service",
    description="Narrative → Format Detection → Parsing → Payer/Payee Extraction",
    version="1.0.0"
)


# -----------------------------
# Main Endpoint
# -----------------------------
@app.post("/ctpty", response_model=CTPTYResponse)
def resolve_ctpty(req: CTPTYRequest):

    if not req.narrative or not req.narrative.strip():
        raise HTTPException(status_code=400, detail="Narrative is required")

    try:
        result, fmt = CTPTY(req.narrative,amount=req.amount)

        return {
            "format": fmt,
            "parsed": result.get("parsed"),
            "ctpty": result.get("ctpty")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
