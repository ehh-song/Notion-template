from dataclasses import dataclass, field
from typing import List
import uuid


@dataclass
class Activity:
    date: str          # "2026-03-24"
    start_time: str    # "09:00" (24+ hour format, e.g. "25:30" = 1:30 AM next day)
    end_time: str      # "10:30"
    name: str
    tags: List[str] = field(default_factory=list)
    color: str = "#4A90D9"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class Reflection:
    activity_id: str
    good: List[str] = field(default_factory=lambda: ["", "", ""])
    bad: List[str] = field(default_factory=lambda: ["", "", ""])
    next_steps: List[str] = field(default_factory=lambda: ["", "", ""])
