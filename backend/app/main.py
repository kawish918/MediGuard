from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
from typing import List
from sqlmodel import Session, select
from app.graph.graph import app as langgraph_app
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import init_db, get_session
from app.db.models import Session as DBSession

app = FastAPI(title="MediGuard Backend")

# Initialize database on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class MediGuardRequest(BaseModel):
    transcript: str
    image_findings: str

@app.post("/run")
def run_medigaurd(req: MediGuardRequest, db: Session = Depends(get_session)):
    initial_state = {
        "transcript": req.transcript,
        "image_findings": req.image_findings,
        "past_context": "",
        "draft_note": "",
        "risk_flags": [],
        "confidence_score": 0.0,
        "clinical_threats": [],
        "confidence_detail": {},
        "hallucination_risk": False,
    }

    result = langgraph_app.invoke(initial_state)

    # Save session to database
    db_session = DBSession(
        transcript=req.transcript,
        image_findings=req.image_findings,
        draft_note=result["draft_note"],
        past_context=result["past_context"],
        risk_flags=result["risk_flags"],
        confidence_score=result["confidence_score"],
        confidence_detail=result.get("confidence_detail", {}),
        clinical_threats=result.get("clinical_threats", []),
        hallucination_risk=result.get("hallucination_risk", False),
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    return {
        "session_id": db_session.id,
        "draft_note": result["draft_note"],
        "risk_flags": result["risk_flags"],
        "confidence_score": result["confidence_score"],
        "confidence_detail": result.get("confidence_detail", {}),
        "past_context": result["past_context"],
        "clinical_threats": result.get("clinical_threats", []),
        "hallucination_risk": result.get("hallucination_risk", False),
    }

@app.post("/run-stream")
async def run_medigaurd_stream(req: MediGuardRequest, db: Session = Depends(get_session)):
    final_result = None
    
    async def event_generator():
        nonlocal final_result
        initial_state = {
            "transcript": req.transcript,
            "image_findings": req.image_findings,
            "past_context": "",
            "draft_note": "",
            "risk_flags": [],
            "confidence_score": 0.0,
            "clinical_threats": [],
            "confidence_detail": {},
            "hallucination_risk": False,
        }

        for event in langgraph_app.stream(initial_state):
            # Extract node name and state from event
            for node_name, node_state in event.items():
                final_result = node_state  # Keep track of final state
                data = {
                    "node": node_name,
                    "output": node_state
                }
                yield f"data: {json.dumps(data)}\n\n"
        
        # Save session to database
        if final_result:
            db_session = DBSession(
                transcript=req.transcript,
                image_findings=req.image_findings,
                draft_note=final_result.get("draft_note", ""),
                past_context=final_result.get("past_context", ""),
                risk_flags=final_result.get("risk_flags", []),
                confidence_score=final_result.get("confidence_score", 0.0),
                confidence_detail=final_result.get("confidence_detail", {}),
                clinical_threats=final_result.get("clinical_threats", []),
                hallucination_risk=final_result.get("hallucination_risk", False),
            )
            db.add(db_session)
            db.commit()
            db.refresh(db_session)
            
            # Send completion event with session ID
            yield f"data: {json.dumps({'node': 'complete', 'output': {'session_id': db_session.id}})}\n\n"
        else:
            yield f"data: {json.dumps({'node': 'complete', 'output': {}})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
@app.get("/sessions")
def get_sessions(db: Session = Depends(get_session)):
    """Get all past sessions"""
    statement = select(DBSession).order_by(DBSession.timestamp.desc())
    sessions = db.exec(statement).all()
    return sessions

@app.get("/sessions/{session_id}")
def get_session_by_id(session_id: str, db: Session = Depends(get_session)):
    """Get a specific session by ID"""
    session = db.get(DBSession, session_id)
    if not session:
        return {"error": "Session not found"}
    return session

@app.get("/sessions")
def get_sessions(db: Session = Depends(get_session)):
    """Get all past sessions"""
    statement = select(DBSession).order_by(DBSession.timestamp.desc())
    sessions = db.exec(statement).all()
    return sessions

@app.get("/sessions/{session_id}")
def get_session_by_id(session_id: str, db: Session = Depends(get_session)):
    """Get a specific session by ID"""
    session = db.get(DBSession, session_id)
    if not session:
        return {"error": "Session not found"}
    return session
