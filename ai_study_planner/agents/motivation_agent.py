"""
Motivation Agent
----------------

"""

TIPS = [
    "Start your day with the toughest subject when your mind is fresh.",
    "Take a 5-minute break every 25-30 minutes (Pomodoro technique).",
    "Revise yesterday's topic for 10 minutes before starting new material.",
    "Explain a concept out loud as if teaching someone - it reveals gaps fast.",
    "Keep your phone in another room while studying to avoid distractions.",
    "Sleep 7-8 hours - memory consolidation happens during sleep.",
    "Break big topics into small, specific goals for each session.",
    "Drink water and stretch between long study sessions.",
    "Review your mistakes from practice papers instead of skipping them.",
    "Celebrate small wins - finishing a topic is progress worth noticing.",
]


def get_daily_tip(day_number):
    """day_number (1-indexed) baghun TIPS list madhun cycle karto."""
    return TIPS[(day_number - 1) % len(TIPS)]


# --------------------------------------------------------------------
# OPTIONAL: Google Gemini API integration (agar user la khara AI-generated
# tip pahije asel tar). Environment madhe GEMINI_API_KEY set kel tar hे
# function वापरा, nahitar वरचा rule-based get_daily_tip() vaparat raha.
# --------------------------------------------------------------------
def get_ai_tip(subject_name, api_key=None):
    """
    api_key dila tar Gemini API la call karun subject-specific tip magto.
    Key nasel / call fail zala tar rule-based tip return karto (safe fallback).
    """
    if not api_key:
        return get_daily_tip(1)

    try:
        import requests
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-1.5-flash:generateContent?key={api_key}"
        )
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Give one short, practical study tip for revising {subject_name} in under 20 words."
                }]
            }]
        }
        response = requests.post(url, json=payload, timeout=8)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        return get_daily_tip(1)
