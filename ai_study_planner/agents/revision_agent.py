"""
Revision Agent
--------------

"""

import math


def apply_revision(schedule, total_days):
    """
    schedule: planning_agent.generate_schedule() cha output (list)
    total_days: total number of study days

    Prataek day dict madhe "session_type" key add karto:
    "study" (normal) kiva "revision" (exam javal).
    """
    revision_days = max(2, math.ceil(total_days * 0.2))
    revision_start_day = total_days - revision_days + 1

    for day in schedule:
        if day["day_number"] >= revision_start_day:
            day["session_type"] = "revision"
        else:
            day["session_type"] = "study"

    return schedule
