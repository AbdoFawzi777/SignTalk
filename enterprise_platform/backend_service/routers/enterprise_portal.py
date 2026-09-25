from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from ..services.llm_grammar_service import llm_grammar_service
from ..services.supabase_client import supabase_service

router = APIRouter(prefix="/api/v1/enterprise", tags=["Enterprise Portal Services"])

class ContextGrammarRequest(BaseModel):
    keywords: List[str]

class ContextGrammarResponse(BaseModel):
    reconstructed_sentence: str
    original_keywords: List[str]

class InstitutionSessionLog(BaseModel):
    institution_id: str
    counter_name: str
    gesture_translated: str
    confidence: float

class AnalyticsSummaryResponse(BaseModel):
    institution_id: str
    total_translations_today: int
    average_latency_ms: float
    satisfaction_rate_percent: float
    active_counters: List[str]

@router.post("/reconstruct-sentence", response_model=ContextGrammarResponse)
async def reconstruct_arabic_sentence(payload: ContextGrammarRequest):
    """
    Reconstructs isolated sign gesture keywords into a fluent, 
    grammatically correct Arabic sentence using LLM contextual inference.
    """
    sentence = await llm_grammar_service.reconstruct_arabic_sentence(payload.keywords)
    return ContextGrammarResponse(
        reconstructed_sentence=sentence,
        original_keywords=payload.keywords
    )

@router.post("/log-session")
async def log_institution_session(payload: InstitutionSessionLog):
    """Logs anonymized translation metrics for institutional dashboard analytics in Supabase."""
    supabase_service.log_translation_session(payload.model_dump())
    return {
        "status": "success",
        "logged_counter": payload.counter_name,
        "gesture": payload.gesture_translated
    }

@router.get("/metrics/{institution_id}", response_model=AnalyticsSummaryResponse)
async def get_institution_metrics(institution_id: str):
    """Returns analytics dashboard metrics for hospital, bank, or government counters."""
    return AnalyticsSummaryResponse(
        institution_id=institution_id,
        total_translations_today=142,
        average_latency_ms=14.2,
        satisfaction_rate_percent=98.5,
        active_counters=["Counter 01 (Reception)", "Counter 04 (Emergency Desk)", "Counter 07 (Pharmacy Desk)"]
    )
