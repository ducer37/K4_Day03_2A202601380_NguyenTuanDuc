"""
🚀 CORE AGENT APP (Dành cho Role 4: Core Agent Developer)
File chính ghép nối tất cả các thành phần: Tools + Prompts + Test Cases + Multi-Provider.
"""

import ast
import math
import inspect
import json
import os
import re
import sys
from dotenv import load_dotenv

# Đảm bảo import các module cùng thư mục src/ hoạt động mượt mà
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Import các thành phần từ file của Role 2, Role 3 & Multi-Provider Adapter
from tools import AVAILABLE_TOOLS
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider

load_dotenv()


ACTION_PATTERN = re.compile(r"Action:\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\[(.*)\]", re.DOTALL)
FINAL_PATTERN = re.compile(r"Final Answer:\s*(.*)", re.DOTALL)

SCHEDULE_INTENTS = [
    "đặt lịch",
    "xếp lịch",
    "sắp xếp lịch",
    "tạo lịch",
    "chốt lịch",
    "book lịch",
    "schedule",
]
SLOT_LOOKUP_INTENTS = [
    "tìm slot",
    "kiểm tra slot",
    "xem slot",
    "slot phỏng vấn",
    "lịch trống",
    "slot trống",
    "khung giờ",
    "còn slot",
    "còn lịch",
]
HR_DOMAIN_TERMS = [
    "cv",
    "resume",
    "hồ sơ",
    "ứng viên",
    "candidate",
    "tuyển dụng",
    "phỏng vấn",
    "interview",
    "fresher",
    "intern",
    "vị trí",
    "job",
    "nghề nghiệp",
    "kỹ năng",
    "kinh nghiệm",
    "fit",
    "backend",
    "frontend",
    "data analyst",
    "qa engineer",
    "product manager",
]
OUT_OF_SCOPE_ANSWER = (
    "Mình là HireMate Agent nên chỉ hỗ trợ các tác vụ tuyển dụng như tra hồ sơ ứng viên, "
    "đánh giá độ phù hợp, kiểm tra slot và đặt lịch phỏng vấn. Câu hỏi hiện tại nằm ngoài "
    "phạm vi demo này, nên mình sẽ không dùng memory tuyển dụng cũ để trả lời sai ngữ cảnh."
)


def estimate_tokens(text: str) -> int:
    """Ước lượng token đơn giản khi provider không trả usage metadata."""
    if not text:
        return 0
    return max(1, math.ceil(len(str(text)) / 4))


def provider_usage_or_estimate(provider, input_text: str, output_text: str, system_prompt: str = "") -> dict:
    """Ưu tiên usage thật từ provider; fallback về ước lượng token đơn giản."""
    usage = getattr(provider, "last_usage", None)
    if usage:
        input_tokens = int(usage.get("input_tokens", 0) or 0)
        output_tokens = int(usage.get("output_tokens", 0) or 0)
        total_tokens = int(usage.get("total_tokens", input_tokens + output_tokens) or 0)
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "source": usage.get("source", "provider"),
        }

    input_tokens = estimate_tokens(system_prompt) + estimate_tokens(input_text)
    output_tokens = estimate_tokens(output_text)
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "source": "estimate",
    }


def load_test_cases():
    """Đọc bộ test cases từ config/test_cases.json của Role 1."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")

    if not os.path.exists(config_path):
        config_path = "test_cases.json"

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_final_answer(llm_output: str) -> str | None:
    """Trích xuất Final Answer từ output của LLM nếu có."""
    match = FINAL_PATTERN.search(llm_output)
    if not match:
        return None
    return match.group(1).strip()


def _fallback_parse_args(args_text: str) -> list[str]:
    """Parser dự phòng cho trường hợp LLM quên quote tham số."""
    if not args_text.strip():
        return []
    return [part.strip().strip("\"'") for part in args_text.split(",")]


def parse_action(llm_output: str) -> tuple[str, list[str]] | None:
    """
    Trích xuất Action theo format: tool_name["arg1", "arg2"].

    Parser ưu tiên ast.literal_eval để tránh split chuỗi thủ công khi tham số
    có dấu phẩy bên trong. Nếu model sinh thiếu quote, dùng fallback đơn giản.
    """
    match = ACTION_PATTERN.search(llm_output)
    if not match:
        return None

    tool_name = match.group(1).strip()
    args_text = match.group(2).strip()

    try:
        parsed_args = ast.literal_eval(f"[{args_text}]")
        if not isinstance(parsed_args, list):
            parsed_args = [parsed_args]
        return tool_name, [str(arg) for arg in parsed_args]
    except (SyntaxError, ValueError):
        return tool_name, _fallback_parse_args(args_text)


def render_react_prompt(user_query: str, scratchpad: list[str], memory_context: str = "") -> str:
    """Tạo prompt mỗi vòng lặp, kèm scratchpad Thought/Action/Observation trước đó."""
    history = "\n".join(scratchpad) if scratchpad else "Chưa có bước nào."
    memory_block = (
        f"Conversation memory (chỉ tham khảo, ưu tiên thấp hơn current question):\n{memory_context}\n\n"
        if memory_context
        else ""
    )
    return f"""{memory_block}Current question (yêu cầu duy nhất cần xử lý):
{user_query}

Scratchpad:
{history}

Hãy trả lời bước tiếp theo theo đúng format ReAct."""


def execute_tool(tool_name: str, args: list[str]) -> str:
    """Gọi tool thật từ AVAILABLE_TOOLS và chuyển mọi lỗi thành Observation an toàn."""
    tool = AVAILABLE_TOOLS.get(tool_name)
    if tool is None:
        valid_tools = ", ".join(AVAILABLE_TOOLS.keys())
        return f"LỖI: Tool '{tool_name}' không tồn tại. Các tool hợp lệ gồm: {valid_tools}."

    expected_arg_count = len(inspect.signature(tool).parameters)
    if len(args) != expected_arg_count:
        return (
            f"LỖI: Tool '{tool_name}' cần {expected_arg_count} tham số "
            f"nhưng nhận được {len(args)} tham số: {args}."
        )

    try:
        return tool(*args)
    except Exception as exc:
        return f"LỖI: Tool '{tool_name}' gặp exception: {exc}"


def has_calendar_intent(user_query: str) -> bool:
    """True nếu câu hiện tại thật sự yêu cầu thao tác với lịch/slot."""
    query = user_query.lower()
    return any(intent in query for intent in SCHEDULE_INTENTS + SLOT_LOOKUP_INTENTS)


def has_schedule_intent(user_query: str) -> bool:
    """True nếu câu hiện tại yêu cầu đặt/xếp lịch rõ ràng."""
    query = user_query.lower()
    return any(intent in query for intent in SCHEDULE_INTENTS)


def has_selected_time(user_query: str) -> bool:
    """True nếu câu hiện tại đã có khung giờ dạng HH:MM."""
    return re.search(r"\b\d{1,2}:\d{2}\b", user_query) is not None


def is_hiremate_domain_query(user_query: str) -> bool:
    """Nhận diện câu hỏi thuộc phạm vi demo HireMate dựa trên câu hiện tại."""
    query = user_query.lower()
    if re.search(r"\bc\d{3}\b", query, flags=re.IGNORECASE):
        return True
    return any(term in query for term in HR_DOMAIN_TERMS + SCHEDULE_INTENTS + SLOT_LOOKUP_INTENTS)


def format_fit_final_answer(observation_text: str) -> str:
    """Biến kết quả score_candidate_fit thành câu trả lời cuối ổn định cho UI demo."""
    if "Khuyến nghị: Nên mời phỏng vấn" in observation_text:
        return f"Có. {observation_text}"
    return observation_text


def validate_action_against_user_request(user_query: str, tool_name: str, args: list[str]) -> str | None:
    """
    Guardrail tầng application để ngăn model làm quá yêu cầu.

    Ví dụ: user chỉ nói "tìm slot" thì Agent được check_interview_slots,
    nhưng không được tự ý gọi schedule_interview.
    """
    query = user_query.lower()

    has_schedule_intent = any(intent in query for intent in SCHEDULE_INTENTS)
    has_slot_lookup_intent = any(intent in query for intent in SLOT_LOOKUP_INTENTS)
    is_lookup_only = has_slot_lookup_intent and not has_schedule_intent

    if tool_name == "check_interview_slots" and not (has_schedule_intent or has_slot_lookup_intent):
        return (
            "LỖI: Người dùng chỉ yêu cầu tra cứu/đánh giá mức độ phù hợp của ứng viên, "
            "không yêu cầu kiểm tra slot phỏng vấn. Hãy trả Final Answer dựa trên dữ liệu "
            "hồ sơ, yêu cầu vị trí và fit score đã có; không gọi check_interview_slots."
        )

    if tool_name != "schedule_interview":
        return None

    requested_time = len(args) >= 4 and str(args[3]).strip() in query

    if is_lookup_only or not has_schedule_intent:
        return (
            "LỖI: Người dùng chỉ yêu cầu tìm/kiểm tra slot phỏng vấn, "
            "không yêu cầu đặt lịch. Hãy trả Final Answer bằng các slot đã tìm được; "
            "không gọi schedule_interview."
        )

    if not requested_time:
        return (
            "LỖI: Người dùng chưa chọn khung giờ cụ thể để đặt lịch. "
            "Hãy đề xuất các slot khả dụng và yêu cầu người dùng chọn giờ."
        )

    return None


def run_baseline_chatbot(user_query: str, provider, memory_context: str = "") -> str:
    """
    Dựng Chatbot gốc (Baseline) không có công cụ.
    Baseline chỉ gọi LLM đúng một lần và không gọi AVAILABLE_TOOLS.
    """
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")

    prompt = (
        f"Conversation memory:\n{memory_context}\n\nCurrent question: {user_query}"
        if memory_context
        else user_query
    )
    response = provider.generate(prompt, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot trả lời:\n{response}")
    return response


def run_react_agent(user_query: str, provider, memory_context: str = "") -> dict:
    """
    Dựng vòng lặp ReAct Agent thật: Thought -> Action -> Observation -> Final Answer.
    """
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")
    scratchpad: list[str] = []
    executed_actions: set[tuple[str, tuple[str, ...]]] = set()
    usage = {"input_tokens": 0, "output_tokens": 0, "llm_calls": 0}

    if not is_hiremate_domain_query(user_query):
        final_step = (
            "Thought: Current question không thuộc phạm vi HireMate, nên không dùng memory tuyển dụng cũ.\n"
            f"Final Answer: {OUT_OF_SCOPE_ANSWER}"
        )
        print(final_step)
        return {
            "status": "final",
            "final_answer": OUT_OF_SCOPE_ANSWER,
            "trace": [final_step],
            "usage": usage,
        }

    for step in range(1, MAX_ITERATIONS + 1):
        print(f"\n--- 🔄 Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")

        prompt = render_react_prompt(user_query, scratchpad, memory_context)
        raw_output = provider.generate(prompt, system_prompt=REACT_SYSTEM_PROMPT)
        llm_output = str(raw_output or "[LLM Empty Response]: Provider không trả về nội dung.").strip()
        call_usage = provider_usage_or_estimate(provider, prompt, llm_output, REACT_SYSTEM_PROMPT)
        usage["input_tokens"] += call_usage["input_tokens"]
        usage["output_tokens"] += call_usage["output_tokens"]
        usage["source"] = call_usage["source"]
        usage["llm_calls"] += 1
        print(llm_output)

        final_answer = parse_final_answer(llm_output)
        if final_answer:
            return {
                "status": "final",
                "final_answer": final_answer,
                "trace": scratchpad + [llm_output],
                "usage": usage,
            }

        action = parse_action(llm_output)
        if not action:
            observation = (
                "Observation: LỖI: Không parse được Action hoặc Final Answer. "
                "Hãy dùng đúng format ReAct."
            )
            print(f"👁️ {observation}")
            scratchpad.extend([llm_output, observation])
            continue

        tool_name, args = action
        action_key = (tool_name, tuple(args))
        if action_key in executed_actions:
            observation_text = (
                f"LỖI: Action {tool_name}{args} đã được gọi trước đó. "
                "Không lặp lại cùng một tool với cùng tham số."
            )
        else:
            executed_actions.add(action_key)
            policy_error = validate_action_against_user_request(user_query, tool_name, args)
            observation_text = policy_error or execute_tool(tool_name, args)

        observation = f"Observation: {observation_text}"
        print(f"👁️ {observation}")
        scratchpad.extend([llm_output, observation])

        if tool_name == "score_candidate_fit" and not observation_text.startswith("LỖI:") and not has_calendar_intent(user_query):
            final_answer = format_fit_final_answer(observation_text)
            final_step = (
                "Thought: Tôi đã có đủ thông tin để trả lời.\n"
                f"Final Answer: {final_answer}"
            )
            print(final_step)
            scratchpad.append(final_step)
            return {
                "status": "final",
                "final_answer": final_answer,
                "trace": scratchpad,
                "usage": usage,
            }

        if tool_name == "check_interview_slots" and not observation_text.startswith("LỖI:"):
            if not has_schedule_intent(user_query):
                final_answer = observation_text
            elif not has_selected_time(user_query):
                final_answer = f"{observation_text} Vui lòng chọn một khung giờ cụ thể để tôi xếp lịch."
            else:
                final_answer = None

            if final_answer:
                final_step = (
                    "Thought: Tôi đã có đủ thông tin để trả lời.\n"
                    f"Final Answer: {final_answer}"
                )
                print(final_step)
                scratchpad.append(final_step)
                return {
                    "status": "final",
                    "final_answer": final_answer,
                    "trace": scratchpad,
                    "usage": usage,
                }

    fallback = (
        f"Xin lỗi, tôi chưa thể hoàn tất tác vụ sau {MAX_ITERATIONS} bước an toàn. "
        "Vui lòng kiểm tra lại mã ứng viên, vị trí tuyển dụng hoặc ngày phỏng vấn."
    )
    print(f"\n🛡️ GUARDRAIL TRIGGERED: {fallback}")
    return {
        "status": "guardrail",
        "final_answer": fallback,
        "trace": scratchpad,
        "usage": usage,
    }


def run_all_tests(tests: list[dict], provider) -> list[dict]:
    """Chạy baseline và ReAct Agent trên toàn bộ test cases."""
    results = []
    for test in tests:
        print("\n" + "=" * 78)
        print(f"🧪 TEST CASE #{test['id']}: {test['category']}")
        print(f"🎯 Expected tools: {test.get('expected_tools', [])}")
        print(f"📌 Evaluation focus: {test.get('evaluation_focus', 'N/A')}")

        baseline_answer = run_baseline_chatbot(test["question"], provider)
        agent_result = run_react_agent(test["question"], provider)

        results.append(
            {
                "id": test["id"],
                "question": test["question"],
                "baseline_answer": baseline_answer,
                "agent_result": agent_result,
            }
        )
    return results


if __name__ == "__main__":
    print("==================================================")
    print("🏫 ĐẠI HỌC VINUNI - BÀI LAB 3: CHATBOT VS REACT AGENT")
    print("==================================================")

    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(f"🔌 LLM Provider đang hoạt động: {provider.__class__.__name__} (Model: {model_name})")

    tests = load_test_cases()
    print(f"✅ Đã tải thành công {len(tests)} Test Cases từ config/test_cases.json")

    run_all_tests(tests, provider)
