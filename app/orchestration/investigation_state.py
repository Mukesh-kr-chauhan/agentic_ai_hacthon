"""
Maintains dynamic multi-round state machine for adaptive agent investigations.
"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid


class TurnRecord(BaseModel):
    turn_id: int
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    active_agent: str
    action_type: str  # PLAN, HYPOTHESIZE, CRITIQUE, REVISE, EVIDENCE_REQUEST
    input_state: Dict[str, Any] = Field(default_factory=dict)
    output_state: Dict[str, Any] = Field(default_factory=dict)
    rationale: str = ""


class InvestigationState(BaseModel):
    incident_id: str
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    current_round: int = 1
    max_rounds: int = 4
    status: str = "INITIALIZED"  # INITIALIZED, INVESTIGATING, CONVERGED, FAILED
    collected_evidence: Dict[str, Any] = Field(default_factory=dict)
    active_hypotheses: List[Dict[str, Any]] = Field(default_factory=list)
    history: List[TurnRecord] = Field(default_factory=list)
    consensus_reached: bool = False

    def log_turn(self, agent: str, action: str, inputs: Dict[str, Any], outputs: Dict[str, Any], rationale: str = ""):
        record = TurnRecord(
            turn_id=len(self.history) + 1,
            active_agent=agent,
            action_type=action,
            input_state=inputs,
            output_state=outputs,
            rationale=rationale
        )
        self.history.append(record)

    def add_evidence(self, metric_key: str, data: Any):
        self.collected_evidence[metric_key] = data

    def advance_round(self):
        self.current_round += 1
        if self.current_round > self.max_rounds:
            self.status = "CONVERGED" if self.consensus_reached else "FAILED"