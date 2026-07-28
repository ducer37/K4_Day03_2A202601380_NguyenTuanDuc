"""
🔌 MULTI-PROVIDER LLM ADAPTER (OpenAI, Gemini, Anthropic, OpenRouter & Offline Mock)
Hỗ trợ chuyển đổi linh hoạt giữa các nhà cung cấp AI chỉ bằng cách đổi biến môi trường LLM_PROVIDER.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

class BaseLLMProvider:
    """Interface cơ sở cho tất cả các LLM Provider"""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Provider"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gemini-2.5-flash"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return "[Gemini Error]: Chưa cấu hình GEMINI_API_KEY trong file .env!"
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(
                model=self.model_name,
                contents=contents
            )
            return response.text
        except Exception as e:
            return f"[Gemini Exception]: {str(e)}"


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Provider (GPT-4o, GPT-3.5-turbo, etc.)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return "[OpenAI Error]: Chưa cấu hình OPENAI_API_KEY trong file .env!"
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[OpenAI Exception]: {str(e)}"


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude Provider (Claude 3.5 Sonnet, Claude 3 Haiku)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "claude-3-haiku-20240307"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_anthropic_api_key_here":
            return "[Anthropic Error]: Chưa cấu hình ANTHROPIC_API_KEY trong file .env!"
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            kwargs = {
                "model": self.model_name,
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            }
            if system_prompt:
                kwargs["system"] = system_prompt
                
            response = client.messages.create(**kwargs)
            return response.content[0].text
        except Exception as e:
            return f"[Anthropic Exception]: {str(e)}"


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter Provider (Hỗ trợ gọi mọi model qua OpenRouter API)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "google/gemini-2.5-flash"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openrouter_api_key_here":
            return "[OpenRouter Error]: Chưa cấu hình OPENROUTER_API_KEY trong file .env!"
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model_name,
                "messages": messages
            }
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"[OpenRouter API Error {res.status_code}]: {res.text}"
        except Exception as e:
            return f"[OpenRouter Exception]: {str(e)}"


class MockProvider(BaseLLMProvider):
    """Offline Mock Provider (Cho bài test không cần kết nối API)"""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if "HireMate Chatbot Baseline" in system_prompt:
            return self._baseline_response(prompt)
        if "HireMate ReAct Agent" in system_prompt:
            return self._react_response(prompt)
        return "🤖 [Mock Provider]: Phản hồi giả lập offline cho bài test."

    def _baseline_response(self, prompt: str) -> str:
        text = prompt.lower()
        if "cv tốt" in text and "data analyst" in text:
            return (
                "Một CV tốt cho vị trí Data Analyst nên có: phần tóm tắt ngắn, "
                "kỹ năng phân tích dữ liệu, công cụ như Python/SQL/Excel, dự án dashboard, "
                "kinh nghiệm liên quan và kết quả định lượng."
            )
        if "fresher" in text and "phỏng vấn" in text:
            return (
                "Ba lưu ý khi phỏng vấn ứng viên fresher: đánh giá nền tảng và tư duy học hỏi, "
                "hỏi dự án/case nhỏ thay vì chỉ hỏi kinh nghiệm, và quan sát thái độ phản hồi khi nhận góp ý."
            )
        if any(token in text for token in ["c001", "c002", "c003", "c004", "c999", "slot", "xếp lịch"]):
            return (
                "Tôi là chatbot baseline nên không có quyền truy cập hồ sơ ứng viên, "
                "yêu cầu tuyển dụng nội bộ hoặc lịch phỏng vấn. Tôi không thể tra cứu/chấm điểm/đặt lịch "
                "cho trường hợp này nếu không có công cụ hỗ trợ."
            )
        return "Tôi có thể hỗ trợ các câu hỏi tuyển dụng chung, nhưng không thể tra cứu dữ liệu nội bộ."

    def _react_response(self, prompt: str) -> str:
        text = prompt.lower()
        observation_count = text.count("observation:")

        if "c999" in text:
            if observation_count == 0:
                return "Thought: Cần kiểm tra hồ sơ ứng viên C999 trước khi xếp lịch.\nAction: get_candidate_profile[\"C999\"]"
            return (
                "Thought: Tool đã báo lỗi ứng viên không tồn tại, nên không được tiếp tục đặt lịch.\n"
                "Final Answer: Tôi chưa thể xếp lịch phỏng vấn vì không tìm thấy ứng viên C999 trong dữ liệu tuyển dụng. "
                "Vui lòng kiểm tra lại mã ứng viên trước khi đặt lịch."
            )

        if "c002" in text and "backend developer" in text:
            if observation_count == 0:
                return "Thought: Cần tra hồ sơ ứng viên C002 trước.\nAction: get_candidate_profile[\"C002\"]"
            if observation_count == 1:
                return "Thought: Cần tra yêu cầu vị trí Backend Developer để so sánh.\nAction: get_job_requirements[\"Backend Developer\"]"
            if observation_count == 2:
                return "Thought: Đã có hồ sơ và yêu cầu vị trí, cần chấm độ phù hợp.\nAction: score_candidate_fit[\"C002\", \"Backend Developer\"]"
            if observation_count == 3:
                return "Thought: Fit score cho thấy ứng viên phù hợp, cần kiểm tra slot phỏng vấn ngày 2026-07-30.\nAction: check_interview_slots[\"2026-07-30\"]"
            return (
                "Thought: Tôi đã có đủ thông tin về độ phù hợp và slot phỏng vấn.\n"
                "Final Answer: Ứng viên C002 phù hợp vị trí Backend Developer với fit score cao. "
                "Ngày 2026-07-30 còn slot 09:00 và 14:00, nên có thể đề xuất một trong hai khung giờ này để phỏng vấn."
            )

        if "c001" in text and "data analyst" in text:
            if observation_count == 0:
                return "Thought: Cần tra hồ sơ ứng viên C001 trước.\nAction: get_candidate_profile[\"C001\"]"
            if observation_count == 1:
                return "Thought: Cần tra yêu cầu vị trí Data Analyst để có tiêu chí so sánh.\nAction: get_job_requirements[\"Data Analyst\"]"
            if observation_count == 2:
                return "Thought: Đã có hồ sơ và yêu cầu vị trí, cần chấm độ phù hợp.\nAction: score_candidate_fit[\"C001\", \"Data Analyst\"]"
            return (
                "Thought: Tôi đã có đủ thông tin để trả lời.\n"
                "Final Answer: Ứng viên C001 phù hợp khá tốt với vị trí Data Analyst. "
                "Hồ sơ có Python, SQL, Excel và Tableau, kinh nghiệm 2 năm vượt yêu cầu tối thiểu. "
                "Điểm cần lưu ý là kỹ năng Dashboard trong yêu cầu được thể hiện gián tiếp qua kinh nghiệm Tableau. "
                "Khuyến nghị: nên mời phỏng vấn vòng tiếp theo."
            )

        if "cv tốt" in text or "fresher" in text:
            return (
                "Thought: Đây là câu hỏi tư vấn chung, không cần dùng dữ liệu nội bộ hay tool.\n"
                "Final Answer: Với câu hỏi tuyển dụng chung này, chatbot baseline đã đủ phù hợp. "
                "Không cần gọi ReAct tool vì không có mã ứng viên, vị trí cụ thể hoặc lịch phỏng vấn cần tra cứu."
            )

        return (
            "Thought: Tôi chưa xác định được dữ liệu nội bộ cần tra cứu.\n"
            "Final Answer: Tôi cần thêm mã ứng viên, vị trí tuyển dụng hoặc ngày phỏng vấn cụ thể để hỗ trợ chính xác."
        )


def get_llm_provider(provider_name: str = None) -> BaseLLMProvider:
    """Factory function tự chọn Provider từ biến môi trường LLM_PROVIDER"""
    name = (provider_name or os.getenv("LLM_PROVIDER") or "mock").lower().strip()
    
    if name == "gemini":
        return GeminiProvider()
    elif name == "openai":
        return OpenAIProvider()
    elif name == "anthropic":
        return AnthropicProvider()
    elif name == "openrouter":
        return OpenRouterProvider()
    else:
        return MockProvider()


if __name__ == "__main__":
    print("=== TEST MULTI-PROVIDER LLM ADAPTER ===")
    provider = get_llm_provider()
    print(f"✅ Provider đang dùng: {provider.__class__.__name__}")
    print(f"🤖 User Query: Hello")
    print(f"💬 Response  : {provider.generate('Hello')}")
