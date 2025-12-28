# planner.py

from typing import List, Dict

class Planner:
    def __init__(self):
        self.plans = []

    def create_plan(self, title: str, tasks: List[str]) -> Dict:
        plan = {
            'title': title,
            'tasks': tasks,
            'completed': False
        }
        self.plans.append(plan)
        return plan

    def complete_plan(self, title: str) -> bool:
        for plan in self.plans:
            if plan['title'] == title:
                plan['completed'] = True
                return True
        return False

    def get_plans(self) -> List[Dict]:
        return self.plans

    def summarize_plans(self) -> str:
        summary = "Plans Summary:\n"
        for plan in self.plans:
            status = "Completed" if plan['completed'] else "Pending"
            summary += f"- {plan['title']}: {status} with tasks {plan['tasks']}\n"
        return summary.strip()