"""
Mock data for HireMate Agent.

This file contains deterministic demo data used by tools.py. Keeping data here
makes the tool contracts easier to read and lets the lab team update candidate,
job, and interview-slot fixtures without touching tool logic.
"""

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
    "C005": {
        "name": "Đỗ Hoàng Nam",
        "target_role": "QA Engineer",
        "experience_years": 2,
        "skills": ["Manual Testing", "Test Case", "API Testing", "Selenium", "Postman"],
        "highlights": [
            "Từng viết test case cho hệ thống đặt hàng",
            "Có kinh nghiệm kiểm thử API bằng Postman",
        ],
    },
    "C006": {
        "name": "Vũ Mai Linh",
        "target_role": "Product Manager",
        "experience_years": 4,
        "skills": ["Roadmap", "User Research", "Agile", "SQL", "Stakeholder Management"],
        "highlights": [
            "Từng dẫn dắt roadmap cho sản phẩm SaaS nội bộ",
            "Có kinh nghiệm làm việc với engineering, sales và customer success",
        ],
    },
    "C007": {
        "name": "Bùi Anh Khoa",
        "target_role": "Backend Developer",
        "experience_years": 1,
        "skills": ["Python", "Flask", "MySQL"],
        "highlights": [
            "Từng làm API nhỏ bằng Flask",
            "Đang học thêm Django và PostgreSQL",
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
    "QA Engineer": {
        "required_skills": ["Manual Testing", "Test Case", "API Testing"],
        "nice_to_have": ["Selenium", "Automation", "Postman"],
        "min_experience_years": 1,
        "description": "Thiết kế test case, kiểm thử chức năng, kiểm thử API và phối hợp báo lỗi với đội phát triển.",
    },
    "Product Manager": {
        "required_skills": ["Roadmap", "User Research", "Agile", "Stakeholder Management"],
        "nice_to_have": ["SQL", "A/B Testing"],
        "min_experience_years": 3,
        "description": "Xác định bài toán sản phẩm, ưu tiên roadmap và phối hợp nhiều bên để ra quyết định.",
    },
}


INTERVIEW_SLOTS = {
    "2026-07-30": ["09:00", "14:00"],
    "2026-07-31": [],
    "2026-08-01": ["10:30", "15:30"],
    "2026-08-02": ["11:00"],
    "2026-08-03": ["13:00", "16:00"],
}
