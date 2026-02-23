from fastapi import FastAPI, Depends, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import shutil
from pathlib import Path
from typing import List
from sqlmodel import Session, select
from app.graph.graph import app as langgraph_app
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import init_db, get_session
from app.db.models import Session as DBSession
from app.models.kaggle_adapter import load_kaggle_output

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

@app.get("/kaggle-case")
def get_kaggle_case():
    """Get the current case data from Kaggle output"""
    try:
        data = load_kaggle_output()
        return {
            "transcript": data["input"]["transcript"],
            "image_findings": data["input"]["image_findings"],
            "session_id": data["session_id"],
            "timestamp": data["timestamp"],
            "model_metadata": data["model_metadata"],
            "performance": data["performance"]
        }
    except FileNotFoundError:
        return {"error": "No Kaggle output file found. Please upload mediguard_output.json from Kaggle"}

@app.post("/upload-kaggle-json")
async def upload_kaggle_json(file: UploadFile = File(...)):
    """Upload Kaggle output JSON file"""
    try:
        # Validate file is JSON
        if not file.filename.endswith('.json'):
            return {"error": "File must be a JSON file"}
        
        # Read and validate JSON structure
        content = await file.read()
        data = json.loads(content)
        
        # Validate required fields
        required_fields = ["input", "agents", "model_metadata"]
        if not all(field in data for field in required_fields):
            return {"error": "Invalid Kaggle output format. Missing required fields."}
        
        # Save to data directory
        data_dir = Path(__file__).parent / "data"
        data_dir.mkdir(exist_ok=True)
        output_path = data_dir / "mediguard_output.json"
        
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        
        # Return the loaded case data
        return {
            "success": True,
            "message": "Kaggle output uploaded successfully",
            "data": {
                "transcript": data["input"]["transcript"],
                "image_findings": data["input"]["image_findings"],
                "session_id": data.get("session_id", "uploaded"),
                "timestamp": data.get("timestamp", ""),
                "model_metadata": data.get("model_metadata", {}),
                "performance": data.get("performance", {})
            }
        }
    except json.JSONDecodeError:
        return {"error": "Invalid JSON file"}
    except Exception as e:
        return {"error": f"Failed to upload file: {str(e)}"}
