from ..config import settings

class SupabaseService:
    def __init__(self):
        self.client = None
        try:
            from supabase import create_client, Client
            self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            print("[+] Supabase Free Tier Client Initialized Successfully.")
        except Exception as e:
            print(f"[!] Supabase Client Info (Offline/Mock Mode): {e}")

    def log_translation_session(self, session_data: dict):
        """Logs an anonymized translation event to PostgreSQL for institutional analytics."""
        if self.client:
            try:
                self.client.table("translation_logs").insert(session_data).execute()
            except Exception as e:
                print(f"[!] DB Log Exception: {e}")
        else:
            # Mock log output for offline verification
            pass

supabase_service = SupabaseService()
