"""
Web UI for HireMate Agent demo.

This Flask app keeps API keys on the server side and exposes a small local UI
for comparing the baseline chatbot with the ReAct agent.
"""

import os
import sys
from contextlib import redirect_stdout
from io import StringIO

from flask import Flask, jsonify, request, send_from_directory

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import load_test_cases, run_baseline_chatbot, run_react_agent
from providers import get_llm_provider


STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web_static")

web_app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")
provider = get_llm_provider()


def _capture_stdout(fn, *args):
    buffer = StringIO()
    with redirect_stdout(buffer):
        result = fn(*args)
    return result, buffer.getvalue()


@web_app.get("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@web_app.get("/api/meta")
def meta():
    return jsonify(
        {
            "provider": provider.__class__.__name__,
            "model": getattr(provider, "model_name", "Offline Mock Mode"),
            "max_iterations": __import__("prompts").MAX_ITERATIONS,
        }
    )


@web_app.get("/api/test-cases")
def test_cases():
    return jsonify(load_test_cases())


@web_app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("question", "")).strip()
    mode = str(payload.get("mode", "compare")).strip().lower()

    if not question:
        return jsonify({"error": "Vui lòng nhập câu hỏi."}), 400

    response = {"question": question, "mode": mode}

    if mode in {"baseline", "compare"}:
        baseline_answer, baseline_log = _capture_stdout(run_baseline_chatbot, question, provider)
        response["baseline"] = {
            "answer": baseline_answer,
            "log": baseline_log,
        }

    if mode in {"agent", "compare"}:
        agent_result, agent_log = _capture_stdout(run_react_agent, question, provider)
        response["agent"] = {
            "status": agent_result["status"],
            "final_answer": agent_result["final_answer"],
            "trace": agent_result["trace"],
            "log": agent_log,
        }

    if mode not in {"baseline", "agent", "compare"}:
        return jsonify({"error": "Mode không hợp lệ. Chọn baseline, agent hoặc compare."}), 400

    return jsonify(response)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5050"))
    web_app.run(host="127.0.0.1", port=port, debug=False)
