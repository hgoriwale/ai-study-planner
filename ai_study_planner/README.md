# AI Study Planner

Agentic AI-based personalized study planner built with Flask + SQLite.

## Agents
- **Planning Agent** — day-wise schedule
- **Time Management Agent** — hour allocation by subject priority
- **Revision Agent** — auto revision days before the exam
- **Motivation Agent** — daily productivity tips

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser.
