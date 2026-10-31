"""
Hypothesis state tracker for maintaining competing hypotheses and revisions.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid


class Hypothesis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    root_cause: str
    confidence: float = Field(ge=0.0, le=1.0)
    supporting_evidence: List[str] = Field(default_factory=list)
    counter_evidence: List[str] = Field(default_factory=list)
    proposed_by: str
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "ACTIVE"  # ACTIVE, REVISED, REJECTED, CONFIRMED


class HypothesisTracker:
    def __init__(self):
        self.hypotheses: Dict[str, Hypothesis] = {}

    def register_hypothesis(self, root_cause: str, proposed_by: str, initial_confidence: float = 0.5) -> Hypothesis:
        hypo = Hypothesis(
            root_cause=root_cause,
            confidence=initial_confidence,
            proposed_by=proposed_by
        )
        self.hypotheses[hypo.id] = hypo
        return hypo

    def update_hypothesis(self, hypo_id: str, delta: float, new_evidence: Optional[str] = None, is_counter: bool = False):
        if hypo_id not in self.hypotheses:
            return

        h = self.hypotheses[hypo_id]
        new_conf = max(0.0, min(1.0, h.confidence + delta))
        h.confidence = round(new_conf, 3)
        h.last_updated = datetime.now(timezone.utc).isoformat()

        if new_evidence:
            if is_counter:
                h.counter_evidence.append(new_evidence)
            else:
                h.supporting_evidence.append(new_evidence)

        if h.confidence >= 0.85:
            h.status = "CONFIRMED"
        elif h.confidence <= 0.15:
            h.status = "REJECTED"
        else:
            h.status = "REVISED"

    def get_leading_hypothesis(self) -> Optional[Hypothesis]:
        if not self.hypotheses:
            return None
        return max(self.hypotheses.values(), key=lambda h: h.confidence)

    def export_state(self) -> List[Dict[str, Any]]:
        return [h.model_dump() for h in self.hypotheses.values()]