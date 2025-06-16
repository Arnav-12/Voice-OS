import whisper
import os
import tempfile
import logging
from gtts import gTTS
from langchain.llms import OpenAI
from langchain.schema import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from app.models.schemas import AgentState
import asyncio
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Initialize models
whisper_model = None
llm = None

def get_whisper_model():
    global whisper_model
    if whisper_model is None:
        whisper_model = whisper.load_model("base")
    return whisper_model

def get_llm():
    global llm
    if llm is None:
        try:
            llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI LLM: {e}")
            # Fallback to a mock LLM for testing
            llm = MockLLM()
    return llm

class MockLLM:
    """Mock LLM for testing when OpenAI API is not available"""
    def invoke(self, messages):
        if isinstance(messages, list) and len(messages) > 0:
            content = messages[0].content if hasattr(messages[0], 'content') else str(messages[0])
            if "summarize" in content.lower():
                return type('Response', (), {'content': 'This is a mock summary of the provided content.'})()
            elif "action items" in content.lower():
                return type('Response', (), {'content': 'Mock action items: 1. Review content 2. Take notes'})()
            else:
                return type('Response', (), {'content': 'This is a mock response to your query.'})()
        return type('Response', (), {'content': 'Mock response'})()

async def transcribe_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Transcribe audio to text using Whisper"""
    try:
        logger.info("Starting transcription...")
        
        if not state.get("audio_path"):
            return {**state, "error": "No audio path provided"}
        
        model = get_whisper_model()
        result = model.transcribe(state["audio_path"])
        transcript = result["text"].strip()
        detected_language = result.get("language", "en")
        
        logger.info(f"Transcription completed. Language: {detected_language}")
        
        return {
            **state,
            "transcript": transcript,
            "detected_language": detected_language,
            "metadata": {**state.get("metadata", {}), "transcription_confidence": "high"}
        }
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return {**state, "error": f"Transcription failed: {str(e)}"}

async def language_detector_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Detect language (already done by Whisper, so this is a pass-through)"""
    try:
        if not state.get("detected_language"):
            # Fallback language detection if needed
            state["detected_language"] = "en"
        
        logger.info(f"Language detected: {state['detected_language']}")
        return state
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        return {**state, "error": f"Language detection failed: {str(e)}"}

async def task_router_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Route task based on content or explicit task type"""
    try:
        transcript = state.get("transcript", "")
        
        # Simple rule-based routing (can be enhanced with LLM)
        if "summary" in transcript.lower() or state.get("task_type") == "summary":
            task_type = "summary"
        elif any(word in transcript.lower() for word in ["action", "todo", "task", "next steps"]):
            task_type = "action_items"
        elif "?" in transcript:
            task_type = "qa"
        else:
            task_type = "summary"  # default
        
        logger.info(f"Task routed to: {task_type}")
        return {**state, "task_type": task_type}
    except Exception as e:
        logger.error(f"Task routing error: {e}")
        return {**state, "error": f"Task routing failed: {str(e)}"}

async def summarizer_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Summarize the transcript"""
    try:
        transcript = state.get("transcript", "")
        if not transcript:
            return {**state, "error": "No transcript to summarize"}
        
        llm_instance = get_llm()
        
        prompt = f"Please provide a concise summary of the following text:\n\n{transcript}"
        messages = [HumanMessage(content=prompt)]
        
        response = llm_instance.invoke(messages)
        summary = response.content if hasattr(response, 'content') else str(response)
        
        logger.info("Summary generated successfully")
        return {**state, "processed_content": summary}
    except Exception as e:
        logger.error(f"Summarization error: {e}")
        return {**state, "error": f"Summarization failed: {str(e)}"}

async def qa_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Answer questions based on the transcript"""
    try:
        transcript = state.get("transcript", "")
        if not transcript:
            return {**state, "error": "No transcript for Q&A"}
        
        llm_instance = get_llm()
        
        prompt = f"Based on the following content, provide helpful answers and insights:\n\n{transcript}"
        messages = [HumanMessage(content=prompt)]
        
        response = llm_instance.invoke(messages)
        answer = response.content if hasattr(response, 'content') else str(response)
        
        logger.info("Q&A response generated successfully")
        return {**state, "processed_content": answer}
    except Exception as e:
        logger.error(f"Q&A error: {e}")
        return {**state, "error": f"Q&A failed: {str(e)}"}

async def action_items_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Extract action items from the transcript"""
    try:
        transcript = state.get("transcript", "")
        if not transcript:
            return {**state, "error": "No transcript for action items"}
        
        llm_instance = get_llm()
        
        prompt = f"Extract actionable items, tasks, and next steps from the following text. Format as a numbered list:\n\n{transcript}"
        messages = [HumanMessage(content=prompt)]
        
        response = llm_instance.invoke(messages)
        actions = response.content if hasattr(response, 'content') else str(response)
        
        logger.info("Action items extracted successfully")
        return {**state, "processed_content": actions}
    except Exception as e:
        logger.error(f"Action items extraction error: {e}")
        return {**state, "error": f"Action items extraction failed: {str(e)}"}

async def tts_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Convert text to speech"""
    try:
        content = state.get("processed_content", "")
        if not content:
            return {**state, "error": "No content for TTS"}
        
        # Create temporary file for audio output
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            audio_path = tmp_file.name
        
        # Generate speech
        tts = gTTS(text=content, lang=state.get("detected_language", "en"))
        tts.save(audio_path)
        
        logger.info(f"TTS audio generated: {audio_path}")
        return {
            **state,
            "audio_response_path": audio_path,
            "response_text": content
        }
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return {**state, "error": f"TTS failed: {str(e)}"}

def should_continue(state: Dict[str, Any]) -> str:
    """Determine the next step in the workflow"""
    if state.get("error"):
        return "error"
    
    task_type = state.get("task_type")
    if not task_type:
        return "route_task"
    
    if not state.get("processed_content"):
        if task_type == "summary":
            return "summarize"
        elif task_type == "qa":
            return "qa"
        elif task_type == "action_items":
            return "action_items"
    
    if not state.get("audio_response_path"):
        return "tts"
    
    return "end"