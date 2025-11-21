import unittest
from modules.decision.core import DecisionModule
from modules.explanation.core import ExplanationModule
from modules.responsibility.core import ResponsibilityModule


class TestGovernanceCompliance(unittest.TestCase):
    """
    Compliance tests to ensure governance rules are enforced:
    - Confidence thresholds
    - Sensitive attribute usage
    """

    def setUp(self):
        self.features = {"attendance": 0.50, "assignments": 0.40, "labs": 0.45}
        self.policy = {"attendance": 0.4, "assignments": 0.3, "labs": 0.3}
        self.decision_module = DecisionModule(model=None, seed=42)
        self.explanation_module = ExplanationModule()

    def test_low_confidence_blocked(self):
        governance = {"use_sensitive_attrs": False, "min_confidence": 0.9}
        decision = self.decision_module.run(self.features, self.policy)
        explanation = self.explanation_module.run(decision)
        responsibility_module = ResponsibilityModule(governance)
        verdict = responsibility_module.run(decision, explanation)

        self.assertFalse(verdict.allowed)
        self.assertIn("Confidence", " ".join(verdict.reasons))

    def test_sensitive_attribute_blocked(self):
        governance = {"use_sensitive_attrs": True, "min_confidence": 0.7}
        decision = self.decision_module.run(self.features, self.policy)
        explanation = self.explanation_module.run(decision)
        responsibility_module = ResponsibilityModule(governance)
        verdict = responsibility_module.run(decision, explanation)

        self.assertFalse(verdict.allowed)
        self.assertIn("Sensitive", " ".join(verdict.reasons))

    def test_valid_decision_allowed(self):
        governance = {"use_sensitive_attrs": False, "min_confidence": 0.5}
        decision = self.decision_module.run(self.features, self.policy)
        explanation = self.explanation_module.run(decision)
        responsibility_module = ResponsibilityModule(governance)
        verdict = responsibility_module.run(decision, explanation)

        self.assertTrue(verdict.allowed)
        self.assertEqual(verdict.reasons, [])


if __name__ == "__main__":
    unittest.main()