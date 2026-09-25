import os

class Settings:
    PROJECT_NAME: str = "SignTalk Enterprise Backend"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Free Supabase Credentials (from environment or defaults)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://xyzcompany.supabase.co")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.dummy_key")

    # Free HuggingFace Inference API Key (Optional for Contextual Arabic LLM Grammar)
    HF_API_KEY: str = os.getenv("HF_API_KEY", "")
    HF_LLM_MODEL: str = "Qwen/Qwen2.5-7B-Instruct"

settings = Settings()
