import json
import os
from datetime import datetime
from modules.decision.core import DecisionModule
from modules.explanation.core import ExplanationModule
from modules.responsibility.core import ResponsibilityModule


def export_audit(decision, explanation, verdict, output_dir="reports/audits"):
    """
    Export audit bundle as a JSON file for compliance and review.
    """
    os.makedirs(output_dir, exist_ok=True)

    audit_data = {
        "trace_id": verdict.trace_id,
        "decision": {
            "prediction": decision.prediction,
            "confidence": decision.confidence,
            "feature_importance": decision.feature_importance,
            "model_version": decision.model_version,
            "data_hash": decision.data_hash,
            "timestamp": decision.timestamp,
        },
        "explanation": {
            "summary": explanation.summary,
            "technical": explanation.technical,
            "counterfactuals": explanation.counterfactuals,
            "caveats": explanation.caveats,
        },
        "responsibility": {
            "allowed": verdict.allowed,
            "reasons": verdict.reasons,
            "metrics": verdict.metrics,
        },
        "audit_bundle": verdict.audit_bundle,
        "exported_at": datetime.utcnow().isoformat()
    }

    filename = f"{output_dir}/audit_{verdict.trace_id}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(audit_data, f, indent=4)

    print(f"Audit bundle exported to {filename}")


if __name__ == "__main__":
    # Example run with dummy data
    features = {"attendance": 0.82, "assignments": 0.67, "labs": 0.74}
    policy = {"attendance": 0.4, "assignments": 0.3, "labs": 0.3}
    governance = {"use_sensitive_attrs": False, "min_confidence": 0.7}

    decision = DecisionModule(model=None).run(features, policy)
    explanation = ExplanationModule().run(decision)
    verdict = ResponsibilityModule(governance).run(decision, explanation)

    export_audit(decision, explanation, verdict)