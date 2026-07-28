const els = {
  providerMeta: document.querySelector("#providerMeta"),
  testCases: document.querySelector("#testCases"),
  reloadCases: document.querySelector("#reloadCases"),
  questionInput: document.querySelector("#questionInput"),
  chatForm: document.querySelector("#chatForm"),
  runButton: document.querySelector("#runButton"),
  baselineResult: document.querySelector("#baselineResult"),
  agentResult: document.querySelector("#agentResult"),
  agentStatus: document.querySelector("#agentStatus"),
  traceList: document.querySelector("#traceList"),
  clearTrace: document.querySelector("#clearTrace"),
};

let activeCaseId = null;

function selectedMode() {
  return document.querySelector("input[name='mode']:checked").value;
}

function setText(el, value, empty = false) {
  el.textContent = value;
  el.classList.toggle("empty", empty);
}

function setBusy(isBusy) {
  els.runButton.disabled = isBusy;
  els.runButton.textContent = isBusy ? "Running..." : "Run";
}

function renderTrace(trace = []) {
  els.traceList.innerHTML = "";
  if (!trace.length) {
    const empty = document.createElement("div");
    empty.className = "trace-empty";
    empty.textContent = "Không có trace cho lần chạy này.";
    els.traceList.appendChild(empty);
    return;
  }

  trace.forEach((entry, index) => {
    const step = document.createElement("div");
    step.className = "trace-step";
    if (entry.includes("LỖI") || entry.includes("Error")) {
      step.classList.add("error");
    }
    step.textContent = `#${index + 1}\n${entry}`;
    els.traceList.appendChild(step);
  });
}

async function loadMeta() {
  const res = await fetch("/api/meta");
  const meta = await res.json();
  els.providerMeta.textContent = `${meta.provider} · ${meta.model} · max ${meta.max_iterations}`;
}

async function loadTestCases() {
  els.testCases.innerHTML = "";
  const res = await fetch("/api/test-cases");
  const cases = await res.json();

  cases.forEach((testCase) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "test-case";
    button.dataset.id = testCase.id;
    button.innerHTML = `
      <span class="case-category">${testCase.category}</span>
      <span class="case-question">${testCase.question}</span>
    `;
    button.addEventListener("click", () => {
      activeCaseId = testCase.id;
      document.querySelectorAll(".test-case").forEach((item) => {
        item.classList.toggle("active", item.dataset.id === String(activeCaseId));
      });
      els.questionInput.value = testCase.question;
      els.questionInput.focus();
    });
    els.testCases.appendChild(button);
  });
}

async function runChat(event) {
  event.preventDefault();
  const question = els.questionInput.value.trim();
  if (!question) {
    els.questionInput.focus();
    return;
  }

  setBusy(true);
  els.agentStatus.textContent = "Running";
  els.agentStatus.classList.remove("error");
  setText(els.baselineResult, "Đang chạy...", false);
  setText(els.agentResult, "Đang chạy...", false);
  renderTrace([]);

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, mode: selectedMode() }),
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || "Request failed");
    }

    if (data.baseline) {
      setText(els.baselineResult, data.baseline.answer || "Không có phản hồi.", false);
    } else {
      setText(els.baselineResult, "Không chạy baseline trong mode này.", true);
    }

    if (data.agent) {
      setText(els.agentResult, data.agent.final_answer || "Không có final answer.", false);
      els.agentStatus.textContent = data.agent.status;
      els.agentStatus.classList.toggle("error", data.agent.status !== "final");
      renderTrace(data.agent.trace || []);
    } else {
      setText(els.agentResult, "Không chạy agent trong mode này.", true);
      els.agentStatus.textContent = "Skipped";
      renderTrace([]);
    }
  } catch (err) {
    setText(els.baselineResult, "Có lỗi khi gọi API.", true);
    setText(els.agentResult, err.message, false);
    els.agentStatus.textContent = "Error";
    els.agentStatus.classList.add("error");
    renderTrace([String(err.message)]);
  } finally {
    setBusy(false);
  }
}

els.chatForm.addEventListener("submit", runChat);
els.reloadCases.addEventListener("click", loadTestCases);
els.clearTrace.addEventListener("click", () => renderTrace([]));

loadMeta().catch(() => {
  els.providerMeta.textContent = "Provider unavailable";
});
loadTestCases();
