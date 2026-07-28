# 📊 BÁO CÁO GIÁM SÁT & ĐÁNH GIÁ (OBSERVABILITY TRACE LOGS)
*Dành cho Role 5: Observability & Reviewer*

---

## 🎯 PHASE 1 - ĐỊNH HÌNH BÀI TOÁN & AGENTIC FIT

### 1. Chủ Đề Đã Chọn

**HireMate Agent: Trợ Lý Sàng Lọc Hồ Sơ Tuyển Dụng & Hẹn Phỏng Vấn**

Bài toán mô phỏng một trợ lý HR có khả năng hỗ trợ nhà tuyển dụng tra cứu hồ sơ ứng viên, kiểm tra yêu cầu của vị trí tuyển dụng, chấm mức độ phù hợp giữa ứng viên và công việc, sau đó đề xuất slot phỏng vấn nếu ứng viên đủ điều kiện.

Phạm vi của bài lab được giới hạn ở dữ liệu giả lập trong chương trình. Agent không đọc CV thật, không gửi email thật, không truy cập hệ thống HR thật và không đưa ra quyết định tuyển dụng cuối cùng. Agent chỉ đóng vai trò hỗ trợ sàng lọc ban đầu dựa trên kỹ năng, kinh nghiệm và yêu cầu công việc.

---

### 2. Mô Tả Bài Toán

Người dùng mục tiêu là nhân sự tuyển dụng hoặc hiring manager. Họ có thể hỏi các câu như:

- "Ứng viên C001 có phù hợp vị trí Data Analyst không?"
- "Nếu ứng viên C002 phù hợp Backend Developer, hãy tìm slot phỏng vấn ngày 2026-07-30."
- "Hãy xếp lịch phỏng vấn cho ứng viên C999."

Chatbot baseline chỉ có thể đưa lời khuyên tuyển dụng chung chung vì không có quyền truy cập dữ liệu nội bộ như hồ sơ ứng viên, yêu cầu vị trí hoặc lịch phỏng vấn. Với các câu hỏi cần dữ liệu cụ thể, chatbot dễ trả lời thiếu căn cứ hoặc phải fallback.

ReAct Agent phù hợp hơn vì có thể thực hiện từng bước có bằng chứng:

1. Tra cứu hồ sơ ứng viên.
2. Tra cứu yêu cầu vị trí tuyển dụng.
3. Chấm mức độ phù hợp dựa trên kỹ năng và kinh nghiệm.
4. Quyết định có nên kiểm tra lịch phỏng vấn hay không.
5. Đề xuất slot phỏng vấn hoặc giải thích vì sao chưa nên phỏng vấn.

---

### 3. Bảng Chấm Điểm Agentic Fit

| Tiêu chí | Điểm (1-5) | Lý do đánh giá |
| :--- | :---: | :--- |
| 🧠 **Multi-step Reasoning** | `5/5` | Bài toán cần nhiều bước liên tiếp: tra hồ sơ ứng viên, tra yêu cầu công việc, chấm độ phù hợp, rồi mới quyết định có nên tìm lịch phỏng vấn không. |
| 🛠️ **Tool Interaction** | `5/5` | Agent cần truy cập dữ liệu nội bộ giả lập qua các tool như candidate database, job requirements và interview slots. |
| 🔀 **Dynamic Decision** | `4/5` | Kết quả chấm fit quyết định bước tiếp theo: nếu đủ điểm thì kiểm tra lịch phỏng vấn, nếu chưa đủ thì giải thích lý do chưa phù hợp. |
| ⏳ **Long Horizon** | `3/5` | Quy trình thường gồm 3-4 bước, đủ để thể hiện vòng lặp ReAct nhưng chưa phải bài toán dài hạn nhiều ngày. |
| **TỔNG ĐIỂM FIT** | **17/20** | **KẾT LUẬN: Bài toán rất phù hợp để dùng ReAct Agent thay vì chỉ dùng chatbot baseline.** |

---

### 4. Danh Sách Tool Dự Kiến

| Tool | Mục đích | Khi nào dùng |
| :--- | :--- | :--- |
| `get_candidate_profile(candidate_id)` | Tra cứu hồ sơ ứng viên theo mã ứng viên. | Khi câu hỏi nhắc đến ứng viên cụ thể như `C001`, `C002`, `C999`. |
| `get_job_requirements(job_title)` | Tra cứu yêu cầu kỹ năng và kinh nghiệm của vị trí tuyển dụng. | Khi cần so sánh ứng viên với một job cụ thể như `Data Analyst` hoặc `Backend Developer`. |
| `score_candidate_fit(candidate_id, job_title)` | Chấm điểm phù hợp giữa ứng viên và vị trí dựa trên kỹ năng, kinh nghiệm. | Sau khi đã xác định ứng viên và vị trí cần đánh giá. |
| `check_interview_slots(date)` | Kiểm tra các slot phỏng vấn còn trống trong một ngày. | Chỉ dùng khi ứng viên đủ phù hợp để chuyển sang vòng phỏng vấn. |
| `schedule_interview(candidate_id, job_title, date, time)` | Giả lập tạo lịch phỏng vấn. | Tool bonus nếu nhóm muốn thể hiện thao tác có side effect được kiểm soát. |

---

### 5. Failure Modes & Guardrails Dự Kiến

| Failure Mode | Ví dụ | Cách xử lý mong muốn |
| :--- | :--- | :--- |
| Ứng viên không tồn tại | `C999` | Tool trả lỗi rõ ràng, Agent không bịa hồ sơ ứng viên. |
| Vị trí tuyển dụng không tồn tại | `AI Wizard` | Agent báo không tìm thấy job trong dữ liệu giả lập. |
| Điểm fit thấp | Ứng viên thiếu nhiều kỹ năng bắt buộc | Agent giải thích lý do chưa nên phỏng vấn và gợi ý bổ sung kỹ năng. |
| Ngày phỏng vấn sai định dạng | `2026-15-99` | Tool trả lỗi ngày không hợp lệ, Agent không tiếp tục đặt lịch. |
| Không còn slot trống | Ngày hợp lệ nhưng full lịch | Agent báo hết slot và đề xuất chọn ngày khác. |
| Thiên kiến tuyển dụng | Người dùng yêu cầu đánh giá theo giới tính, ngoại hình, quê quán | Agent từ chối tiêu chí không phù hợp và chỉ đánh giá theo kỹ năng, kinh nghiệm, yêu cầu công việc. |
| Lặp tool không cần thiết | Agent gọi cùng một tool với cùng tham số nhiều lần | Guardrail `MAX_ITERATIONS` ngắt vòng lặp và trả fallback lịch sự. |

---

### 6. Smoke Test Môi Trường

Đã chạy thử `python src/app.py` thành công với `MockProvider`. Repo hiện có thể chạy offline, nhưng app vẫn đang là demo mẫu theo chủ đề thời tiết/chuyến bay. Các phase tiếp theo sẽ cần cập nhật `config/test_cases.json`, `src/tools.py`, `src/prompts.py` và `src/app.py` theo đề tài HireMate Agent.

---

## 🔍 PHASE 2+ - TRACE LOG & EVALUATION

Phần này sẽ được hoàn thiện sau khi đã triển khai test cases, tools, prompts và ReAct loop cho đề tài HireMate Agent.

### Test Case #1

*Chưa chạy trong Phase 1.*

### Test Case #2

*Chưa chạy trong Phase 1.*

### Test Case #3

*Chưa chạy trong Phase 1.*

### Test Case #4

*Chưa chạy trong Phase 1.*

### Test Case #5

*Chưa chạy trong Phase 1.*
