from typing import List, Dict, Any

class Ranker:
    def __init__(self, retrieval_results: List[Dict[str, Any]] | None = None):
        self.retrieval_results = retrieval_results or []

    def rank(self, items: List[Dict[str, Any]] | None = None) -> List[Dict[str, Any]]:
        data = items if items is not None else self.retrieval_results
        return sorted(data, key=lambda x: x.get('score', 0), reverse=True)

    def get_top_n(self, n: int) -> List[Dict[str, Any]]:
        return self.rank()[:n]