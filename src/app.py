"""
🚀 CORE AGENT APP (Dành cho Role 4: Core Agent Developer)
File chính ghép nối tất cả các thành phần: Tools + Prompts + Test Cases + Multi-Provider.
"""

import ast
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


def render_react_prompt(user_query: str, scratchpad: list[str]) -> str:
    """Tạo prompt mỗi vòng lặp, kèm scratchpad Thought/Action/Observation trước đó."""
    history = "\n".join(scratchpad) if scratchpad else "Chưa có bước nào."
    return f"""Question: {user_query}

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


def run_baseline_chatbot(user_query: str, provider) -> str:
    """
    Dựng Chatbot gốc (Baseline) không có công cụ.
    Baseline chỉ gọi LLM đúng một lần và không gọi AVAILABLE_TOOLS.
    """
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")

    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot trả lời:\n{response}")
    return response


def run_react_agent(user_query: str, provider) -> dict:
    """
    Dựng vòng lặp ReAct Agent thật: Thought -> Action -> Observation -> Final Answer.
    """
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")
    scratchpad: list[str] = []
    executed_actions: set[tuple[str, tuple[str, ...]]] = set()

    for step in range(1, MAX_ITERATIONS + 1):
        print(f"\n--- 🔄 Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")

        prompt = render_react_prompt(user_query, scratchpad)
        raw_output = provider.generate(prompt, system_prompt=REACT_SYSTEM_PROMPT)
        llm_output = str(raw_output or "[LLM Empty Response]: Provider không trả về nội dung.").strip()
        print(llm_output)

        final_answer = parse_final_answer(llm_output)
        if final_answer:
            return {
                "status": "final",
                "final_answer": final_answer,
                "trace": scratchpad + [llm_output],
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
            observation_text = execute_tool(tool_name, args)

        observation = f"Observation: {observation_text}"
        print(f"👁️ {observation}")
        scratchpad.extend([llm_output, observation])

    fallback = (
        f"Xin lỗi, tôi chưa thể hoàn tất tác vụ sau {MAX_ITERATIONS} bước an toàn. "
        "Vui lòng kiểm tra lại mã ứng viên, vị trí tuyển dụng hoặc ngày phỏng vấn."
    )
    print(f"\n🛡️ GUARDRAIL TRIGGERED: {fallback}")
    return {
        "status": "guardrail",
        "final_answer": fallback,
        "trace": scratchpad,
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
