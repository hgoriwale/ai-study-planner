"""
Planning Agent
--------------

"""

from datetime import date, timedelta


def generate_schedule(subjects_with_priority, exam_date_str, hours_per_subject):
    """
    subjects_with_priority: [{"name": "Maths", "priority": 5}, ...]
    exam_date_str: "YYYY-MM-DD"
    hours_per_subject: {"Maths": 2.3, ...}  <- Time Management Agent cha output

    return: list of day dicts:
        [{"day_number": 1, "date": "2026-07-07",
          "sessions": [{"subject": "Maths", "hours": 2.3}, ...]}, ...]
    """
    exam_date = date.fromisoformat(exam_date_str)
    today = date.today()
    total_days = (exam_date - today).days

    if total_days <= 0:
        total_days = 1  # exam date aajच असel tar minimum 1 day

    schedule = []
    for day_num in range(1, total_days + 1):
        current_date = today + timedelta(days=day_num - 1)
        sessions = [
            {"subject": s["name"], "hours": hours_per_subject.get(s["name"], 0)}
            for s in subjects_with_priority
        ]
        schedule.append({
            "day_number": day_num,
            "date": current_date.isoformat(),
            "sessions": sessions,
        })

    return schedule, total_days
