from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import time
from typing import List, Dict, Any
from ..services.llm_grammar_service import llm_grammar_service
from ..services.supabase_client import supabase_service

router = APIRouter(tags=["WebSockets Translation Broker"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[+] WebSocket Client Connected. Total Active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"[-] WebSocket Client Disconnected. Remaining: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"[!] Send error to connection: {e}")

manager = ConnectionManager()

@router.websocket("/ws/translation")
async def websocket_translation_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            raw_data = await websocket.receive_text()
            payload = json.loads(raw_data)
            
            start_time = time.time()
            session_id = payload.get("session_id", "counter_01")
            raw_keywords = payload.get("keywords", ["أنا", "طبيب", "حاجز"])
            
            # Reconstruct fluent Arabic sentence via Contextual LLM Grammar service
            reconstructed_sentence = await llm_grammar_service.reconstruct_arabic_sentence(raw_keywords)
            latency_ms = round((time.time() - start_time) * 1000, 2)

            response_payload = {
                "event": "translation_frame",
                "session_id": session_id,
                "detected_gesture": reconstructed_sentence,
                "raw_keywords": raw_keywords,
                "confidence": payload.get("confidence", 0.96),
                "latency_ms": latency_ms,
                "timestamp": int(time.time())
            }

            # Broadcast translation to all institutional reception counter displays
            await manager.broadcast(response_payload)

            # Log transaction asynchronously to Supabase
            supabase_service.log_translation_session({
                "institution_id": session_id,
                "counter_name": "Counter 01",
                "gesture_translated": reconstructed_sentence,
                "confidence": payload.get("confidence", 0.96)
            })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"[!] WebSocket Router Error: {e}")
        manager.disconnect(websocket)
