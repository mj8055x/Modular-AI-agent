from dataclasses import dataclass
from typing import List, Dict


@dataclass(frozen=True)
class ResponsibilityVerdict:
    """
    Immutable verdict artifact from responsibility module.
    """
    allowed: bool
    reasons: List[str]
    metrics: Dict[str, float]
    audit_bundle: Dict[str, any]
    trace_id: str


class ResponsibilityModule:
    """
    Responsibility module:
    - Applies ethical and governance filters to decision artifacts
    - Flags low-confidence or policy-violating outputs
    - Produces audit bundles for traceability and review
    """

    def __init__(self, governance: Dict[str, any]):
        self.governance = governance

    def _check_confidence(self, confidence: float) -> bool:
        """
        Enforce minimum confidence threshold.
        """
        min_conf = self.governance.get("min_confidence", 0.7)
        return confidence >= min_conf

    def _check_sensitive_usage(self) -> bool:
        """
        Enforce exclusion of sensitive attributes.
        """
        return not self.governance.get("use_sensitive_attrs", False)

    def _generate_reasons(self, decision, explanation) -> List[str]:
        """
        Collect reasons for blocking or flagging.
        """
        reasons = []
        if not self._check_sensitive_usage():
            reasons.append("Sensitive attributes were used.")
        if not self._check_confidence(decision.confidence):
            reasons.append(f"Confidence {decision.confidence:.2f} is below threshold.")
        return reasons

    def _generate_metrics(self, decision) -> Dict[str, float]:
        """
        Extract key metrics for audit.
        """
        top_feats = sorted(decision.feature_importance.items(), key=lambda kv: -abs(kv[1]))[:3]
        return {
            "confidence": decision.confidence,
            "top_feature_1": top_feats[0][1] if len(top_feats) > 0 else 0.0,
            "top_feature_2": top_feats[1][1] if len(top_feats) > 1 else 0.0,
            "top_feature_3": top_feats[2][1] if len(top_feats) > 2 else 0.0,
        }

    def _generate_audit_bundle(self, decision, explanation) -> Dict[str, any]:
        """
        Compose audit bundle with traceable metadata.
        """
        return {
            "trace_id": decision.trace_id,
            "data_hash": decision.data_hash,
            "model_version": decision.model_version,
            "timestamp": decision.timestamp,
            "summary": explanation.summary,
            "caveats": explanation.caveats,
            "feature_importance": decision.feature_importance,
            "confidence": decision.confidence
        }

    def run(self, decision, explanation) -> ResponsibilityVerdict:
        """
        Apply governance filters and produce verdict.

        Args:
            decision: DecisionOutput
            explanation: ExplanationOutput

        Returns:
            ResponsibilityVerdict with policy verdict, reasons, metrics, and audit bundle.
        """
        reasons = self._generate_reasons(decision, explanation)
        allowed = len(reasons) == 0
        metrics = self._generate_metrics(decision)
        audit_bundle = self._generate_audit_bundle(decision, explanation)

        return ResponsibilityVerdict(
            allowed=allowed,
            reasons=reasons,
            metrics=metrics,
            audit_bundle=audit_bundle,
            trace_id=decision.trace_id
        )