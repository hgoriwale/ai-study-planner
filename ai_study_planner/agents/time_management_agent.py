"""
Time Management Agent
----------------------

"""


def allocate_hours(subjects_with_priority, daily_hours):
    """
    subjects_with_priority: [{"name": "Maths", "priority": 5}, ...]
    daily_hours: total study hours available per day (float)

    return: {"Maths": 2.3, "Physics": 1.7, ...}  (hours per day per subject)
    """
    total_priority = sum(s["priority"] for s in subjects_with_priority)
    if total_priority == 0:
        equal_share = round(daily_hours / len(subjects_with_priority), 2)
        return {s["name"]: equal_share for s in subjects_with_priority}

    allocation = {}
    for s in subjects_with_priority:
        share = (s["priority"] / total_priority) * daily_hours
        allocation[s["name"]] = round(share, 2)

    return allocation
