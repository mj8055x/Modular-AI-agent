import unittest
from modules.decision.core import DecisionModule
from modules.explanation.core import ExplanationModule
from modules.responsibility.core import ResponsibilityModule


class TestDecisionModule(unittest.TestCase):
    def setUp(self):
        self.features = {"attendance": 0.82, "assignments": 0.67, "labs": 0.74}
        self.policy = {"attendance": 0.4, "assignments": 0.3, "labs": 0.3}
        self.module = DecisionModule(model=None, seed=42)

    def test_run_outputs_decision(self):
        decision = self.module.run(self.features, self.policy)
        self.assertIsNotNone(decision.prediction)
        self.assertGreaterEqual(decision.confidence, 0.0)
        self.assertLessEqual(decision.confidence, 1.0)
        self.assertEqual(set(decision.feature_importance.keys()), set(self.features.keys()))
        self.assertTrue(decision.trace_id.startswith("trace-"))
        self.assertEqual(decision.model_version, "v1.0")


class TestExplanationModule(unittest.TestCase):
    def setUp(self):
        features = {"attendance": 0.82, "assignments": 0.67, "labs": 0.74}
        policy = {"attendance": 0.4, "assignments": 0.3, "labs": 0.3}
        decision = DecisionModule(model=None, seed=42).run(features, policy)
        self.decision = decision
        self.module = ExplanationModule()

    def test_run_outputs_explanation(self):
        explanation = self.module.run(self.decision)
        self.assertIn("Prediction", explanation.summary or "")
        self.assertIn("confidence", explanation.technical)
        self.assertIsInstance(explanation.counterfactuals, list)
        self.assertIsInstance(explanation.caveats, list)
        self.assertEqual(explanation.trace_id, self.decision.trace_id)


class TestResponsibilityModule(unittest.TestCase):
    def setUp(self):
        features = {"attendance": 0.82, "assignments": 0.67, "labs": 0.74}
        policy = {"attendance": 0.4, "assignments": 0.3, "labs": 0.3}
        decision = DecisionModule(model=None, seed=42).run(features, policy)
        explanation = ExplanationModule().run(decision)
        self.decision = decision
        self.explanation = explanation
        self.governance = {"use_sensitive_attrs": False, "min_confidence": 0.7}
        self.module = ResponsibilityModule(self.governance)

    def test_run_outputs_verdict(self):
        verdict = self.module.run(self.decision, self.explanation)
        self.assertIsInstance(verdict.allowed, bool)
        self.assertIsInstance(verdict.reasons, list)
        self.assertIsInstance(verdict.metrics, dict)
        self.assertIsInstance(verdict.audit_bundle, dict)
        self.assertEqual(verdict.trace_id, self.decision.trace_id)


if __name__ == "__main__":
    unittest.main()