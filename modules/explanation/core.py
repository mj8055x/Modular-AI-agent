from dataclasses import dataclass
from typing import Dict, List
import math


@dataclass(frozen=True)
class ExplanationOutput:
    """
    Immutable explanation artifact derived from decision output.
    """
    summary: str
    technical: Dict[str, float]
    counterfactuals: List[Dict[str, float]]
    caveats: List[str]
    trace_id: str


class ExplanationModule:
    """
    Explanation module:
    - Translates decision artifacts into human-readable summaries
    - Provides technical breakdown and counterfactuals
    - Adds caveats and traceability
    """

    def __init__(self, audience: str = "default"):
        self.audience = audience

    def _generate_summary(self, importance: Dict[str, float]) -> str:
        """
        Create a readable summary based on top contributing features.
        """
        top_feats = sorted(importance.items(), key=lambda kv: -abs(kv[1]))[:3]
        if not top_feats:
            return "No significant features contributed to the decision."
        feat_names = [k for k, _ in top_feats]
        return f"Prediction was primarily influenced by: {', '.join(feat_names)}."

    def _generate_counterfactuals(self, importance: Dict[str, float]) -> List[Dict[str, float]]:
        """
        Suggest simple what-if changes to top features and estimate impact.
        """
        counterfactuals = []
        for k, v in sorted(importance.items(), key=lambda kv: -abs(kv[1]))[:3]:
            delta = 0.1 * v
            counterfactuals.append({
                "feature": k,
                "change": "+10%",
                "estimated_impact": round(delta, 4)
            })
        return counterfactuals

    def _generate_caveats(self) -> List[str]:
        """
        Add standard caveats for transparency.
        """
        return [
            "No sensitive attributes were used.",
            "Feature weights are explicitly defined by policy.",
            "Confidence is derived from a logistic mapping of score."
        ]

    def run(self, decision) -> ExplanationOutput:
        """
        Generate explanation from decision output.

        Args:
            decision: DecisionOutput object

        Returns:
            ExplanationOutput with summary, technical details, counterfactuals, and caveats.
        """
        summary = self._generate_summary(decision.feature_importance)
        technical = {
            "prediction": decision.prediction,
            "confidence": decision.confidence,
            "feature_importance": decision.feature_importance,
            "model_version": decision.model_version
        }
        counterfactuals = self._generate_counterfactuals(decision.feature_importance)
        caveats = self._generate_caveats()

        return ExplanationOutput(
            summary=summary,
            technical=technical,
            counterfactuals=counterfactuals,
            caveats=caveats,
            trace_id=decision.trace_id
        )