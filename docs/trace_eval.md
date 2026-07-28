# Báo Cáo Trace & Đánh Giá HireMate Agent

*Role 5: Observability & Reviewer*

---

## Phase 1 - Agentic Fit

### Chủ Đề Đã Chọn

**HireMate Agent: Trợ Lý Sàng Lọc Hồ Sơ Tuyển Dụng & Hẹn Phỏng Vấn**

Bài toán mô phỏng trợ lý HR có khả năng tra cứu hồ sơ ứng viên, kiểm tra yêu cầu vị trí, chấm mức độ phù hợp và hỗ trợ tìm/đặt lịch phỏng vấn dựa trên dữ liệu mock. Agent không đọc CV thật, không gửi email thật, không truy cập hệ thống HR thật và không đưa ra quyết định tuyển dụng cuối cùng.

### Vì Sao Cần Agent Thay Vì Chỉ Chatbot?

Chatbot baseline trả lời tốt các câu hỏi kiến thức chung như “CV Data Analyst nên có gì?”, nhưng không thể tra cứu dữ liệu nội bộ. Với câu hỏi có mã ứng viên, vị trí cụ thể hoặc slot phỏng vấn, baseline phải fallback.

ReAct Agent phù hợp hơn vì cần chuỗi hành động có bằng chứng:

1. Nhận diện yêu cầu hiện tại.
2. Gọi tool phù hợp.
3. Đọc Observation.
4. Quyết định dừng, gọi tool tiếp theo hoặc fallback.
5. Trả lời cuối dựa trên dữ liệu mock thay vì bịa.

### Bảng Chấm Điểm Agentic Fit

| Tiêu chí | Điểm | Lý do |
| :--- | :---: | :--- |
| Multi-step Reasoning | 5/5 | Nhiều câu cần tra ứng viên, đối chiếu job, chấm fit rồi mới quyết định có kiểm tra lịch hay không. |
| Tool Interaction | 5/5 | Agent dùng các tool nội bộ: hồ sơ ứng viên, yêu cầu job, chấm fit, slot phỏng vấn, đặt lịch. |
| Dynamic Decision | 4/5 | Fit score quyết định có chuyển sang lịch phỏng vấn. Intent của user quyết định chỉ tìm slot hay được đặt lịch. |
| Long Horizon | 3/5 | Quy trình thường 2-4 bước, đủ thể hiện ReAct nhưng chưa phải workflow nhiều ngày. |
| Tổng | 17/20 | Phù hợp để so sánh Chatbot Baseline và ReAct Agent. |

---

## Phase 2 - Test Cases

Bộ test chính thức được rút gọn còn **7 case** trong `config/test_cases.json`, đủ các nhóm theo yêu cầu lab: câu đơn giản, multi-step, tool path, edge case và guardrail.

| ID | Nhóm | Câu hỏi | Expected Tools | Output mong muốn |
| :---: | :--- | :--- | :--- | :--- |
| 1 | General QA | CV tốt cho Data Analyst nên có gì? | Không tool | Trả lời kiến thức chung về CV, không bịa dữ liệu nội bộ. |
| 2 | Fit Screening | C001 có phù hợp Data Analyst không? | `get_candidate_profile`, `score_candidate_fit` | C001 fit 78/100, nên mời phỏng vấn, không tự tìm slot. |
| 3 | Low Fit | C003 có phù hợp Backend Developer không? | `score_candidate_fit` | C003 fit 10/100, thiếu stack backend, không kiểm tra slot. |
| 4 | Fit + Slot | C002 phù hợp thì tìm slot ngày 2026-07-30 | `score_candidate_fit`, `check_interview_slots` | C002 fit 95/100, ngày 2026-07-30 còn 09:00 và 14:00, không đặt lịch. |
| 5 | Schedule | Đặt lịch C005 QA Engineer ngày 2026-08-02 lúc 11:00 | `check_interview_slots`, `schedule_interview` | Tạo lịch thành công cho C005 lúc 11:00. |
| 6 | Edge Case | Đặt lịch C999 ngày 2026-15-99 | Không tool hoặc lỗi an toàn | Báo ngày/mã ứng viên không hợp lệ, không bịa và không đặt lịch. |
| 7 | Memory Isolation | Hỏi phân tích bài thơ Nam quốc sơn hà sau chat tuyển dụng | Không tool | Báo ngoài phạm vi HireMate, không lặp lại memory C007. |

---

## Phase 3 - Tools & Prompt

### Tool Registry

| Tool | Vai trò |
| :--- | :--- |
| `get_candidate_profile(candidate_id)` | Tra cứu hồ sơ ứng viên theo mã. |
| `get_job_requirements(job_title)` | Tra cứu yêu cầu vị trí tuyển dụng. |
| `score_candidate_fit(candidate_id, job_title)` | Chấm fit score 0-100 dựa trên kỹ năng, kinh nghiệm và nice-to-have. |
| `check_interview_slots(date)` | Kiểm tra slot trống theo ngày `YYYY-MM-DD`. |
| `schedule_interview(candidate_id, job_title, date, time)` | Giả lập đặt lịch phỏng vấn nếu dữ liệu hợp lệ. |

### Guardrails Đã Cài

| Guardrail | Mục đích |
| :--- | :--- |
| `MAX_ITERATIONS = 6` | Chặn loop vô hạn. |
| Tool whitelist | Chỉ gọi tool có trong `AVAILABLE_TOOLS`. |
| Parser `Action[...]` | Ép format ReAct rõ ràng. |
| Duplicate action guard | Không gọi lặp cùng tool với cùng tham số. |
| Intent guard cho `check_interview_slots` | Không tự tìm slot khi user chỉ hỏi fit. |
| Intent guard cho `schedule_interview` | Không tự đặt lịch khi user chỉ yêu cầu tìm slot hoặc chưa chọn giờ. |
| Auto-final sau `score_candidate_fit` | Nếu user chỉ hỏi phù hợp hay không, dừng ngay sau fit score. |
| Auto-final sau `check_interview_slots` | Nếu user chỉ hỏi tìm slot, dừng ngay sau danh sách slot. |
| Domain router | Câu ngoài phạm vi HireMate không dùng memory tuyển dụng cũ. |
| Memory filter | Memory theo từng session, bỏ baseline khỏi context và giới hạn độ dài message. |

---

## Phase 4 - Kết Quả Kiểm Thử

Môi trường kiểm thử:

- Ngày chạy: 2026-07-28
- Provider: `OpenAIProvider`
- Model: `gpt-4o-mini`
- Command kiểm thử: chạy `run_baseline_chatbot()` và `run_react_agent()` trên 7 case từ `config/test_cases.json`.

### Tổng Quan

| ID | Baseline | Agent | Tools thực tế | Kết quả |
| :---: | :--- | :--- | :--- | :---: |
| 1 | Trả lời được câu hỏi CV chung | Trả lời trực tiếp, không dùng tool | Không tool | Pass |
| 2 | Fallback vì không có hồ sơ nội bộ | Tra C001 và chấm fit 78/100 | `get_candidate_profile -> score_candidate_fit` | Pass |
| 3 | Fallback vì không có dữ liệu nội bộ | Chấm C003 fit 10/100 và dừng | `score_candidate_fit` | Pass |
| 4 | Fallback vì không có lịch nội bộ | Chấm C002 fit 95/100, tìm slot | `score_candidate_fit -> check_interview_slots` | Pass |
| 5 | Fallback vì không đặt lịch được | Kiểm tra slot và tạo lịch C005 | `check_interview_slots -> schedule_interview` | Pass |
| 6 | Fallback chung | Báo ngày không hợp lệ, không gọi tool | Không tool | Pass |
| 7 | Trả lời bài thơ ngoài domain | Agent từ chối ngoài phạm vi, không dùng memory cũ | Không tool | Pass |

**Kết quả cuối:** `7/7` test case đạt yêu cầu cơ bản về tool selection, grounding và termination.

### Trace Tiêu Biểu

#### Case 2 - Tra C001 Và Chấm Fit

```text
Thought: Tra cứu hồ sơ ứng viên C001.
Action: get_candidate_profile["C001"]
Observation: Ứng viên C001 - Nguyễn Minh Anh: mục tiêu Data Analyst, 2 năm kinh nghiệm, kỹ năng: Python, SQL, Excel, Tableau...

Thought: Đánh giá mức độ phù hợp giữa C001 và Data Analyst.
Action: score_candidate_fit["C001", "Data Analyst"]
Observation: Fit score cho ứng viên C001 với vị trí Data Analyst: 78/100...

Final Answer: Có. Fit score cho ứng viên C001 với vị trí Data Analyst: 78/100... Khuyến nghị: Nên mời phỏng vấn.
```

Nhận xét: Agent trả lời có căn cứ từ Observation, không tự kiểm tra slot vì user chỉ hỏi mức độ phù hợp.

#### Case 4 - Fit Rồi Tìm Slot, Không Đặt Lịch

```text
Thought: Chấm điểm mức độ phù hợp giữa C002 và Backend Developer.
Action: score_candidate_fit["C002", "Backend Developer"]
Observation: Fit score cho ứng viên C002 với vị trí Backend Developer: 95/100...

Thought: C002 phù hợp, kiểm tra slot phỏng vấn ngày 2026-07-30.
Action: check_interview_slots["2026-07-30"]
Observation: Ngày 2026-07-30 còn các slot phỏng vấn: 09:00, 14:00.

Final Answer: Ngày 2026-07-30 còn các slot phỏng vấn: 09:00, 14:00.
```

Nhận xét: Đây là khác biệt rõ với chatbot baseline. Baseline không có lịch nội bộ, còn agent dùng tool và dừng đúng sau slot lookup.

#### Case 5 - Đặt Lịch Thành Công

```text
Thought: Kiểm tra slot phỏng vấn ngày 2026-08-02.
Action: check_interview_slots["2026-08-02"]
Observation: Ngày 2026-08-02 còn các slot phỏng vấn: 11:00.

Thought: Slot 11:00 khả dụng, xếp lịch cho C005.
Action: schedule_interview["C005", "QA Engineer", "2026-08-02", "11:00"]
Observation: Đã tạo lịch phỏng vấn cho ứng viên C005 - Đỗ Hoàng Nam với vị trí QA Engineer vào 2026-08-02 lúc 11:00.

Final Answer: Lịch phỏng vấn cho ứng viên C005 - Đỗ Hoàng Nam với vị trí QA Engineer đã được xếp lịch vào ngày 2026-08-02 lúc 11:00.
```

Nhận xét: Agent chỉ gọi `schedule_interview` khi user đã cung cấp đủ ngày và giờ cụ thể.

#### Case 7 - Memory Isolation

```text
Thought: Current question không thuộc phạm vi HireMate, nên không dùng memory tuyển dụng cũ.
Final Answer: Mình là HireMate Agent nên chỉ hỗ trợ các tác vụ tuyển dụng như tra hồ sơ ứng viên, đánh giá độ phù hợp, kiểm tra slot và đặt lịch phỏng vấn. Câu hỏi hiện tại nằm ngoài phạm vi demo này, nên mình sẽ không dùng memory tuyển dụng cũ để trả lời sai ngữ cảnh.
```

Nhận xét: Đây là case được thêm sau khi phát hiện bug agent lặp lại kết quả C007 khi người dùng hỏi bài thơ trong cùng session.

---

## Phase 5 - Failed Trace & Cải Tiến

### Bug 1 - Agent Tự Đặt Lịch Khi User Chỉ Yêu Cầu Tìm Slot

Before:

```text
Action: check_interview_slots["2026-07-30"]
Observation: Ngày 2026-07-30 còn các slot phỏng vấn: 09:00, 14:00.
Action: schedule_interview["C002", "Backend Developer", "2026-07-30", "09:00"]
Observation: LỖI: Người dùng chỉ yêu cầu tìm/kiểm tra slot phỏng vấn...
```

Root cause: Prompt có rule nhưng LLM vẫn tự mở rộng từ “tìm slot” sang “đặt lịch”.

Fix:

- Thêm policy guard cho `schedule_interview`.
- Thêm auto-final sau `check_interview_slots` nếu câu hiện tại không có intent đặt lịch.

After:

```text
Action: score_candidate_fit["C002", "Backend Developer"]
Observation: Fit score ... 95/100.
Action: check_interview_slots["2026-07-30"]
Observation: Ngày 2026-07-30 còn các slot phỏng vấn: 09:00, 14:00.
Final Answer: Ngày 2026-07-30 còn các slot phỏng vấn: 09:00, 14:00.
```

### Bug 2 - Memory Kéo Sai Ngữ Cảnh

Before:

```text
user: Ứng viên C007 có đủ mạnh cho vị trí Backend Developer không?
agent: Fit score cho ứng viên C007 ... 28/100.

user: Hãy phân tích bài thơ Nam quốc sơn hà cho tôi.
agent: Fit score cho ứng viên C007 ... 28/100.
```

Root cause: Agent đưa toàn bộ memory session vào prompt nhưng chưa kiểm tra current question có thuộc domain HireMate không.

Fix:

- Thêm domain router `is_hiremate_domain_query()`.
- Nếu câu ngoài phạm vi, trả out-of-scope ngay và không gọi LLM.
- Memory context chỉ lấy message trong session hiện tại, bỏ baseline và giới hạn độ dài từng message.

After:

```text
Final Answer: Câu hỏi hiện tại nằm ngoài phạm vi demo HireMate, nên không dùng memory tuyển dụng cũ để trả lời sai ngữ cảnh.
```

---

## So Sánh Baseline vs Agent

| Tiêu chí | Chatbot Baseline | ReAct Agent |
| :--- | :--- | :--- |
| Câu hỏi chung | Trả lời tốt, nhanh | Trả lời tốt, không cần tool |
| Hồ sơ ứng viên cụ thể | Không truy cập được, phải fallback | Gọi tool lấy dữ liệu mock và trả lời có căn cứ |
| Chấm fit | Không có dữ liệu để chấm | Chấm bằng `score_candidate_fit` |
| Slot phỏng vấn | Không truy cập được | Gọi `check_interview_slots` |
| Đặt lịch | Không thực hiện được | Gọi `schedule_interview` khi đủ thông tin |
| Guardrail | Chủ yếu dựa vào prompt | Có prompt + application guardrail + max iterations |
| Observability | Không có trace hành động | Có ReAct Trace: Thought, Action, Observation, Final Answer |

Kết luận: Baseline phù hợp cho câu hỏi kiến thức chung. ReAct Agent phù hợp hơn cho nghiệp vụ có dữ liệu nội bộ, nhiều bước và cần kiểm soát hành động.

---

## Checklist Hoàn Thiện Báo Cáo

- [x] Chọn chủ đề và mô tả bài toán.
- [x] Chấm Agentic Fit theo 4 tiêu chí.
- [x] Thiết kế 7 test cases trong `config/test_cases.json`.
- [x] Tách mock data sang `src/mock_data.py`.
- [x] Khai báo tool contract trong `src/tools.py`.
- [x] Hoàn thiện prompt và guardrails trong `src/prompts.py`.
- [x] Chạy ReAct loop và ghi trace trong `src/app.py`.
- [x] Có frontend demo stream, memory, history, metrics, cost và ReAct Trace.
- [x] Có failed trace before/after.
- [x] Có hybrid flowchart trong `docs/hybrid_flowchart.mermaid`.

