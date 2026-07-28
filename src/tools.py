"""
🛠️ TOOL REGISTRY & SCHEMAS (Dành cho Role 2: Tool & Spec Engineer)
Nơi khai báo tất cả các "món đồ nghề" mà ReAct Agent có thể gọi.
"""

from datetime import datetime


# ---------------------------------------------------------------------------
# MOCK DATA - HIREMATE AGENT
# ---------------------------------------------------------------------------

CANDIDATES = {
    "C001": {
        "name": "Nguyễn Minh Anh",
        "target_role": "Data Analyst",
        "experience_years": 2,
        "skills": ["Python", "SQL", "Excel", "Tableau"],
        "highlights": [
            "Từng xây dashboard bán hàng bằng Tableau",
            "Có kinh nghiệm phân tích dữ liệu khách hàng",
        ],
    },
    "C002": {
        "name": "Trần Quốc Bảo",
        "target_role": "Backend Developer",
        "experience_years": 3,
        "skills": ["Python", "Django", "PostgreSQL", "Docker", "REST API"],
        "highlights": [
            "Từng phát triển REST API cho hệ thống e-commerce",
            "Có kinh nghiệm deploy service bằng Docker",
        ],
    },
    "C003": {
        "name": "Lê Thu Hà",
        "target_role": "Marketing Intern",
        "experience_years": 1,
        "skills": ["Communication", "Content", "Canva", "Social Media"],
        "highlights": [
            "Từng quản lý fanpage câu lạc bộ sinh viên",
            "Có portfolio nội dung social media",
        ],
    },
    "C004": {
        "name": "Phạm Gia Huy",
        "target_role": "Frontend Developer",
        "experience_years": 1,
        "skills": ["JavaScript", "HTML", "CSS", "React"],
        "highlights": [
            "Từng làm landing page bằng React",
            "Có kinh nghiệm UI component cơ bản",
        ],
    },
}


JOBS = {
    "Data Analyst": {
        "required_skills": ["Python", "SQL", "Excel", "Dashboard"],
        "nice_to_have": ["Power BI", "Tableau"],
        "min_experience_years": 1,
        "description": "Phân tích dữ liệu kinh doanh, xây dashboard và đưa insight cho team vận hành.",
    },
    "Backend Developer": {
        "required_skills": ["Python", "Django", "PostgreSQL", "REST API"],
        "nice_to_have": ["Docker", "Cloud"],
        "min_experience_years": 2,
        "description": "Xây dựng API, xử lý logic server-side và làm việc với cơ sở dữ liệu.",
    },
    "Marketing Intern": {
        "required_skills": ["Communication", "Content", "Canva"],
        "nice_to_have": ["Social Media", "SEO"],
        "min_experience_years": 0,
        "description": "Hỗ trợ viết nội dung, thiết kế ấn phẩm cơ bản và vận hành kênh social.",
    },
    "Frontend Developer": {
        "required_skills": ["JavaScript", "HTML", "CSS", "React"],
        "nice_to_have": ["TypeScript", "Figma"],
        "min_experience_years": 1,
        "description": "Phát triển giao diện web, component UI và tối ưu trải nghiệm người dùng.",
    },
}


INTERVIEW_SLOTS = {
    "2026-07-30": ["09:00", "14:00"],
    "2026-07-31": [],
    "2026-08-01": ["10:30", "15:30"],
}


def _normalize_candidate_id(candidate_id: str) -> str:
    return str(candidate_id).strip().upper()


def _find_job_title(job_title: str) -> str | None:
    normalized = str(job_title).strip().lower()
    for title in JOBS:
        if title.lower() == normalized:
            return title
    return None


def _is_valid_date(date: str) -> bool:
    try:
        parsed = datetime.strptime(str(date).strip(), "%Y-%m-%d")
        return parsed.strftime("%Y-%m-%d") == str(date).strip()
    except ValueError:
        return False


def get_candidate_profile(candidate_id: str) -> str:
    """
    Tra cứu hồ sơ ứng viên theo mã ứng viên.

    Args:
        candidate_id (str): Mã ứng viên, ví dụ: "C001".

    Returns:
        str: Tóm tắt hồ sơ ứng viên nếu tìm thấy; chuỗi lỗi nghiệp vụ nếu không có dữ liệu.

    Error semantics:
        Không raise exception cho lỗi nghiệp vụ. Nếu mã ứng viên không tồn tại,
        trả về chuỗi bắt đầu bằng "LỖI:" để Agent có thể đọc và phục hồi.
    """
    cid = _normalize_candidate_id(candidate_id)
    candidate = CANDIDATES.get(cid)
    if not candidate:
        return f"LỖI: Không tìm thấy ứng viên '{candidate_id}' trong dữ liệu tuyển dụng."

    skills = ", ".join(candidate["skills"])
    highlights = "; ".join(candidate["highlights"])
    return (
        f"Ứng viên {cid} - {candidate['name']}: mục tiêu {candidate['target_role']}, "
        f"{candidate['experience_years']} năm kinh nghiệm, kỹ năng: {skills}. "
        f"Điểm nổi bật: {highlights}."
    )


def get_job_requirements(job_title: str) -> str:
    """
    Tra cứu yêu cầu tuyển dụng của một vị trí.

    Args:
        job_title (str): Tên vị trí, ví dụ: "Data Analyst".

    Returns:
        str: Mô tả yêu cầu vị trí nếu tìm thấy; chuỗi lỗi nếu vị trí không tồn tại.
    """
    title = _find_job_title(job_title)
    if not title:
        return f"LỖI: Không tìm thấy vị trí tuyển dụng '{job_title}' trong dữ liệu."

    job = JOBS[title]
    required = ", ".join(job["required_skills"])
    nice_to_have = ", ".join(job["nice_to_have"])
    return (
        f"Vị trí {title}: {job['description']} "
        f"Kỹ năng bắt buộc: {required}. Kỹ năng cộng điểm: {nice_to_have}. "
        f"Kinh nghiệm tối thiểu: {job['min_experience_years']} năm."
    )


def score_candidate_fit(candidate_id: str, job_title: str) -> str:
    """
    Chấm điểm phù hợp giữa ứng viên và vị trí tuyển dụng.

    Args:
        candidate_id (str): Mã ứng viên, ví dụ: "C001".
        job_title (str): Tên vị trí, ví dụ: "Data Analyst".

    Returns:
        str: Điểm fit 0-100, lý do, điểm mạnh/yếu và khuyến nghị phỏng vấn.

    Scoring:
        - 70 điểm từ kỹ năng bắt buộc.
        - 20 điểm từ kinh nghiệm tối thiểu.
        - 10 điểm từ kỹ năng cộng điểm.
    """
    cid = _normalize_candidate_id(candidate_id)
    candidate = CANDIDATES.get(cid)
    if not candidate:
        return f"LỖI: Không thể chấm fit vì không tìm thấy ứng viên '{candidate_id}'."

    title = _find_job_title(job_title)
    if not title:
        return f"LỖI: Không thể chấm fit vì không tìm thấy vị trí '{job_title}'."

    job = JOBS[title]
    candidate_skills = {skill.lower() for skill in candidate["skills"]}
    required_skills = job["required_skills"]
    nice_to_have = job["nice_to_have"]

    matched_required = [skill for skill in required_skills if skill.lower() in candidate_skills]
    missing_required = [skill for skill in required_skills if skill.lower() not in candidate_skills]
    matched_nice = [skill for skill in nice_to_have if skill.lower() in candidate_skills]

    skill_score = (len(matched_required) / len(required_skills)) * 70
    min_exp = job["min_experience_years"]
    exp_score = 20 if min_exp == 0 else min(candidate["experience_years"] / min_exp, 1) * 20
    bonus_score = 0 if not nice_to_have else (len(matched_nice) / len(nice_to_have)) * 10
    total_score = round(skill_score + exp_score + bonus_score)

    recommendation = (
        "Nên mời phỏng vấn"
        if total_score >= 75
        else "Cần cân nhắc thêm trước khi mời phỏng vấn"
    )
    return (
        f"Fit score cho ứng viên {cid} với vị trí {title}: {total_score}/100. "
        f"Kỹ năng bắt buộc khớp: {', '.join(matched_required) or 'Không có'}. "
        f"Kỹ năng còn thiếu: {', '.join(missing_required) or 'Không có'}. "
        f"Kỹ năng cộng điểm khớp: {', '.join(matched_nice) or 'Không có'}. "
        f"Kinh nghiệm: {candidate['experience_years']} năm so với yêu cầu tối thiểu {min_exp} năm. "
        f"Khuyến nghị: {recommendation}."
    )


def check_interview_slots(date: str) -> str:
    """
    Kiểm tra slot phỏng vấn còn trống theo ngày.

    Args:
        date (str): Ngày phỏng vấn theo định dạng YYYY-MM-DD.

    Returns:
        str: Danh sách slot còn trống; chuỗi lỗi nếu ngày sai định dạng.
    """
    date_text = str(date).strip()
    if not _is_valid_date(date_text):
        return f"LỖI: Ngày phỏng vấn '{date}' không hợp lệ. Vui lòng dùng định dạng YYYY-MM-DD."

    slots = INTERVIEW_SLOTS.get(date_text, [])
    if not slots:
        return f"Ngày {date_text} hiện không còn slot phỏng vấn trống."
    return f"Ngày {date_text} còn các slot phỏng vấn: {', '.join(slots)}."


def schedule_interview(candidate_id: str, job_title: str, date: str, time: str) -> str:
    """
    Giả lập tạo lịch phỏng vấn cho ứng viên.

    Args:
        candidate_id (str): Mã ứng viên.
        job_title (str): Vị trí tuyển dụng.
        date (str): Ngày phỏng vấn theo định dạng YYYY-MM-DD.
        time (str): Giờ phỏng vấn, ví dụ: "09:00".

    Returns:
        str: Xác nhận đặt lịch nếu hợp lệ; chuỗi lỗi nếu dữ liệu không hợp lệ.
    """
    cid = _normalize_candidate_id(candidate_id)
    if cid not in CANDIDATES:
        return f"LỖI: Không thể đặt lịch vì không tìm thấy ứng viên '{candidate_id}'."

    title = _find_job_title(job_title)
    if not title:
        return f"LỖI: Không thể đặt lịch vì không tìm thấy vị trí '{job_title}'."

    date_text = str(date).strip()
    if not _is_valid_date(date_text):
        return f"LỖI: Ngày phỏng vấn '{date}' không hợp lệ. Vui lòng dùng định dạng YYYY-MM-DD."

    time_text = str(time).strip()
    slots = INTERVIEW_SLOTS.get(date_text, [])
    if time_text not in slots:
        return f"LỖI: Slot {time_text} ngày {date_text} không khả dụng."

    slots.remove(time_text)
    return (
        f"Đã tạo lịch phỏng vấn cho ứng viên {cid} - {CANDIDATES[cid]['name']} "
        f"với vị trí {title} vào {date_text} lúc {time_text}."
    )


# ---------------------------------------------------------------------------
# LEGACY DEMO TOOLS
# Giữ tạm để src/app.py hiện tại chưa bị lỗi import trước khi chuyển hẳn
# sang ReAct loop của đề tài HireMate ở phase sau.
# ---------------------------------------------------------------------------

def get_weather(location: str) -> str:
    """Legacy demo tool: tra cứu thời tiết mẫu."""
    loc_lower = location.lower()
    if "hà nội" in loc_lower or "ha noi" in loc_lower:
        return "Thời tiết Hà Nội: 28°C, Nắng nhẹ, Độ ẩm 65%."
    return f"LỖI: Không tìm thấy dữ liệu thời tiết cho địa điểm '{location}'."


def search_flights(origin: str, destination: str) -> str:
    """Legacy demo tool: tra cứu chuyến bay mẫu."""
    return (
        f"Chuyến bay từ {origin} -> {destination} ngày mai:\n"
        f"1. VN123 (08:00) - Giá: 1,500,000 VNĐ (Còn vé)\n"
        f"2. VJ456 (14:30) - Giá: 1,200,000 VNĐ (Còn vé)"
    )


# Danh sách các tool được đăng ký để HireMate Agent sử dụng
AVAILABLE_TOOLS = {
    "get_candidate_profile": get_candidate_profile,
    "get_job_requirements": get_job_requirements,
    "score_candidate_fit": score_candidate_fit,
    "check_interview_slots": check_interview_slots,
    "schedule_interview": schedule_interview,
}
