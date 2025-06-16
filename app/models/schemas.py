from pydantic import BaseModel
from typing import Optional, Dict, Any
from enum import Enum

class TaskType(str, Enum):
    SUMMARY = "summary"
    QA = "qa"
    ACTION_ITEMS = "action_items"

class AudioProcessRequest(BaseModel):
    audio_url: Optional[str] = None
    task_type: TaskType = TaskType.SUMMARY
    language: Optional[str] = None

class AgentState(BaseModel):
    audio_path: Optional[str] = None
    transcript: Optional[str] = None
    detected_language: Optional[str] = None
    task_type: Optional[str] = None
    processed_content: Optional[str] = None
    response_text: Optional[str] = None
    audio_response_path: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}

class ProcessResponse(BaseModel):
    success: bool
    transcript: Optional[str] = None
    response: Optional[str] = None
    audio_url: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}
