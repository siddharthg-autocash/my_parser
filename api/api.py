# PYTHONPATH=. uvicorn project_gamma.api.api:app --reload

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from project_gamma.src.gamma.service.script import CTPTY
from project_gamma.src.gamma.util.routines import routine2

class CTPTYRequest(BaseModel):
    narrative: str
    amount: Optional[float] = None
    tenant_id: int
    bai_code: Optional[str] = None

class CTPTYResponse(BaseModel):
    tenant_id: int
    format: str
    parsed: Dict[str, Any]
    ctpty: Dict[str, Any]

class RoutineRequest(BaseModel):
    value : str

app = FastAPI(
    title="CTPTY Resolution Service",
    description="Narrative to Payer/Payee and Counterparty Extraction ",
    version="1.0.0",
)

@app.post("/addKey")
def addKey(req: RoutineRequest):
    try:
        routine2(
            key="added via api",
            value=req.value,
            inline=False
        )
    except Exception as e:
        return {"error": str(e)}

    return {"res": "Added the key successfully!"}


@app.post("/ctpty", response_model=CTPTYResponse)
def resolve_ctpty(req: CTPTYRequest):
    result, fmt = CTPTY(req.narrative,amount=req.amount,bai_code=req.bai_code,)

    # if error comes from ctpty function, i will show error.
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    res = {
        "tenant_id": req.tenant_id,
        "format": fmt,
        "parsed": result.get("parsed"),
        "ctpty": result.get("ctpty")
        }

    return res

