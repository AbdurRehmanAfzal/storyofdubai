from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
import structlog

logger = structlog.get_logger()


@dataclass
class ScoreResult:
    entity_id: str
    score: float
    breakdown: dict[str, float]  # component name → points awarded


class BaseScorer(ABC):
    MAX_SCORE = 100.0

    @abstractmethod
    def score(self, entity: Any) -> ScoreResult:
        """Score an entity and return breakdown"""
        pass

    def clamp(self, value: float, min_val: float = 0, max_val: float = None) -> float:
        """Clamp value between min and max"""
        max_val = max_val or self.MAX_SCORE
        return max(min_val, min(value, max_val))
