from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Plan:
    title: str
    tasks: List[str] = field(default_factory=list)
    completed: bool = False
    summary: Optional[str] = None

class Planner:
    def __init__(self):
        self._plans: Dict[str, Plan] = {}

    def create_plan(self, slug: str, tasks: Optional[List[str]] = None) -> Plan:
        if not slug:
            raise ValueError("slug required")
        if slug in self._plans:
            raise FileExistsError(slug)
        plan = Plan(title=slug, tasks=tasks or ["task 1", "task 2"], summary=f"summary for {slug}")
        self._plans[slug] = plan
        return plan

    def get_summary(self, slug: str) -> Optional[str]:
        p = self._plans.get(slug)
        return p.summary if p else None

    def complete_plan(self, slug: str) -> bool:
        p = self._plans.get(slug)
        if p:
            p.completed = True
            return True
        return False

    def get_plans(self) -> List[Plan]:
        return list(self._plans.values())