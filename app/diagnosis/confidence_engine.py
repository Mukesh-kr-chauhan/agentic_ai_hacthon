from typing import Dict, List, Tuple
from app.protocols.message_schema import EvidenceItem

class ConfidenceEngine:
    @staticmethod
    def calculate_confidence(
        supporting_evidence: List[EvidenceItem],
        contributing_agents: List[str],
        contradictions_present: bool,
        is_missing_telemetry: bool,
        metrics_count: int
    ) -> Tuple[float, str, str, str]:
        """
        Returns (confidence_score, category, explanation, status)
        Status: 'healthy', 'diagnosed', or 'insufficient_evidence'
        """
        # Rule 1: Sparse/Missing critical telemetry cannot claim healthy operation
        if is_missing_telemetry or metrics_count < 2:
            return 0.15, "Insufficient evidence", "Critical baseline telemetry missing. System cannot confirm root cause or normal operation.", "insufficient_evidence"

        # Rule 2: Normal operation when data is present and no anomalies fired
        if len(supporting_evidence) == 0:
            return 0.92, "High confidence", f"All {metrics_count} monitored baseline metrics are within normal campus tolerances.", "healthy"

        # Rule 3: Fault diagnosis scoring
        score = 0.20
        ev_weight = min(0.35, len(supporting_evidence) * 0.08)
        score += ev_weight

        unique_agents = len(set(contributing_agents))
        if unique_agents >= 3:
            score += 0.30
        elif unique_agents == 2:
            score += 0.20
        elif unique_agents == 1:
            score += 0.05

        penalties = []
        if contradictions_present:
            score -= 0.25
            penalties.append("conflicting agent findings (-0.25)")

        score = max(0.10, min(0.98, round(score, 2)))

        if score >= 0.80:
            category = "High confidence"
        elif score >= 0.60:
            category = "Medium confidence"
        elif score >= 0.40:
            category = "Low confidence"
        else:
            category = "Insufficient evidence"

        penalty_text = f", penalized for {', '.join(penalties)}" if penalties else ""
        explanation = (
            f"Synthesized from {len(supporting_evidence)} evidence points across {unique_agents} specialized agents"
            f"{penalty_text}. Categorized as {category}."
        )

        status = "diagnosed" if score >= 0.40 else "insufficient_evidence"
        return score, category, explanation, status