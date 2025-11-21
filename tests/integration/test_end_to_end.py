import unittest
from modules.decision.core import DecisionModule
from modules.explanation.core import ExplanationModule
from modules.responsibility.core import ResponsibilityModule


class TestEndToEndFlow(unittest.TestCase):
    """
    Integration test to validate the complete pipeline:
    Decision → Explanation → Responsibility
    """

    def setUp(self):
        # Sample input features and policy
        self.features = {"attendance": 0.82, "assignments": 0.67, "labs": 0.74}
        self.policy = {"attendance": 0.4, "assignments": 0.3, "labs": 0.3}
        self.governance = {"use_sensitive_attrs": False, "min_confidence": 0.7}

        # Initialize modules
        self.decision_module = DecisionModule(model=None, seed=42)
        self.explanation_module = ExplanationModule()
        self.responsibility_module = ResponsibilityModule(self.governance)

    def test_pipeline_flow(self):
        # Run decision
        decision = self.decision_module.run(self.features, self.policy)
        self.assertIsNotNone(decision)

        # Run explanation
        explanation = self.explanation_module.run(decision)
        self.assertEqual(explanation.trace_id, decision.trace_id)

        # Run responsibility
        verdict = self.responsibility_module.run(decision, explanation)
        self.assertEqual(verdict.trace_id, decision.trace_id)

        # Assertions across pipeline
        self.assertIsInstance(verdict.allowed, bool)
        self.assertIsInstance(verdict.reasons, list)
        self.assertIsInstance(verdict.metrics, dict)
        self.assertIsInstance(verdict.audit_bundle, dict)

        # Ensure audit bundle contains key metadata
        self.assertIn("trace_id", verdict.audit_bundle)
        self.assertIn("data_hash", verdict.audit_bundle)
        self.assertIn("model_version", verdict.audit_bundle)
        self.assertIn("confidence", verdict.audit_bundle)


if __name__ == "__main__":
    unittest.main()