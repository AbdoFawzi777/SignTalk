import json
import urllib.request
from ..config import settings

class LLMContextualGrammarService:
    def __init__(self):
        self.api_url = f"https://api-inference.huggingface.co/models/{settings.HF_LLM_MODEL}"
        self.headers = {"Authorization": f"Bearer {settings.HF_API_KEY}"} if settings.HF_API_KEY else {}

    async def reconstruct_arabic_sentence(self, keywords: list[str]) -> str:
        """
        Converts isolated sign keywords (e.g. ['أنا', 'طبيب', 'حاجز'])
        into a grammatically correct Arabic sentence (e.g. 'أنا بحاجة لمقابلة الطبيب لو سمحت').
        """
        if not keywords:
            return ""

        input_text = " ".join(keywords)

        # Smart rule-based local reconstruction fallback (zero latency & 100% free)
        rule_based_mappings = {
            "أنا طبيب حاجز": "أنا بحاجة لمقابلة الطبيب لو سمحت",
            "ماء أنا عطشان": "هل يمكنني الحصول على كوب ماء؟",
            "مساعدة شرطة حريق": "أطلب المساعدة! يوجد حريق والشرطة مطلوبة",
            "أين مستشفى قريب": "أين تقع أقرب مستشفى هنا؟",
        }

        if input_text in rule_based_mappings:
            return rule_based_mappings[input_text]

        if not settings.HF_API_KEY:
            return f"إشارة مترجمة: {input_text}"

        prompt = f"قم بإعادة ترتيب وصياغة الكلمات التالية إلى جملة عربية فصيحة ومفيدة: {input_text}"
        payload = json.dumps({"inputs": prompt, "parameters": {"max_new_tokens": 50, "temperature": 0.3}}).encode('utf-8')

        try:
            req = urllib.request.Request(self.api_url, data=payload, headers=self.headers)
            with urllib.request.urlopen(req, timeout=3) as response:
                if response.status == 200:
                    res_body = json.loads(response.read().decode('utf-8'))
                    if isinstance(res_body, list) and "generated_text" in res_body[0]:
                        return res_body[0]["generated_text"].replace(prompt, "").strip()
        except Exception as e:
            print(f"[!] LLM API Warning: {e}")

        return f"{input_text}"

llm_grammar_service = LLMContextualGrammarService()
