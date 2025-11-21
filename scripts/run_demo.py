from modules.decision.core import DecisionModule
from modules.explanation.core import ExplanationModule
from modules.responsibility.core import ResponsibilityModule

# Sample input features (non-sensitive)
features = {
    "attendance": 0.82,
    "assignments": 0.67,
    "labs": 0.74
}

# Explicit policy weights
policy = {
    "attendance": 0.4,
    "assignments": 0.3,
    "labs": 0.3
}

# Governance rules
governance = {
    "use_sensitive_attrs": False,
    "min_confidence": 0.7
}

# Run decision module
decision = DecisionModule(model=None).run(features, policy)

# Run explanation module
explanation = ExplanationModule().run(decision)

# Run responsibility module
verdict = ResponsibilityModule(governance).run(decision, explanation)

# Display results
print("\n=== DECISION OUTPUT ===")
print(f"Prediction: {decision.prediction:.4f}")
print(f"Confidence: {decision.confidence:.4f}")
print(f"Feature Importance: {decision.feature_importance}")
print(f"Trace ID: {decision.trace_id}")
print(f"Data Hash: {decision.data_hash}")
print(f"Model Version: {decision.model_version}")
print(f"Timestamp: {decision.timestamp:.2f}")

print("\n=== EXPLANATION OUTPUT ===")
print(f"Summary: {explanation.summary}")
print(f"Technical: {explanation.technical}")
print(f"Counterfactuals: {explanation.counterfactuals}")
print(f"Caveats: {explanation.caveats}")
print(f"Trace ID: {explanation.trace_id}")

print("\n=== RESPONSIBILITY VERDICT ===")
print(f"Allowed: {verdict.allowed}")
print(f"Reasons: {verdict.reasons}")
print(f"Metrics: {verdict.metrics}")
print(f"Audit Bundle: {verdict.audit_bundle}")
print(f"Trace ID: {verdict.trace_id}")