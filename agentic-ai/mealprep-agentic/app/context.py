# app/context.py
from dataclasses import dataclass

@dataclass
class AppContext:
    user_id: str
    locale: str = "en"
    unit_system: str = "metric"
    session_role: str = "user"   # user, coach, admin