from dataclasses import dataclass
from typing import Dict, Any, Optional
import numpy as np
import hashlib
import json
import time


def stable_hash(obj: Any) -> str:
    """
    Create a stable hex hash for any JSON-serializable object.
    Ensures deterministic data hashing across runs and platforms.
    """
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class DecisionOutput:
    """
    Immutable decision artifact passed to downstream modules.
    """
    prediction: float
    confidence: float
    feature_importance: Dict[str, float]
    trace_id: str
    model_version: str
    data_hash: str
    timestamp: float


class DecisionModule:
    """
    Decision module:
    - Deterministic inference (seeded) for reproducibility
    - Transparent feature weighting via provided 'policy' dict
    - Emits traceable artifacts (trace_id, data_hash, model_version)
    """

    def __init__(self, model: Optional[Any] = None, model_version: str = "v1.0", seed: int = 42):
        # Seed numpy for deterministic behavior
        np.random.seed(seed)
        self.model = model
        self.model_version = model_version

    def _score_with_policy(self, features: Dict[str, float], policy: Dict[str, float]) -> float:
        """
        Compute a simple, transparent score using policy weights.
        Score is the weighted dot product normalized by weight vector norm.
        """
        keys = list(features.keys())
        weights = np.array([policy.get(k, 1.0) for k in keys], dtype=float)
        xs = np.array([features[k] for k in keys], dtype=float)

        # Avoid divide-by-zero with small epsilon
        norm = float(np.linalg.norm(weights) + 1e-9)
        score = float(np.dot(weights, xs) / norm)
        return score

    def _confidence(self, score: float) -> float:
        """
        Map score to [0,1] using a logistic function.
        """
        return float(1.0 / (1.0 + np.exp(-score)))

    def _feature_importance(self, features: Dict[str, float], policy: Dict[str, float]) -> Dict[str, float]:
        """
        Simple importance: product of feature value and its explicit policy weight.
        """
        return {k: float(policy.get(k, 1.0) * v) for k, v in features.items()}

    def _trace_id(self, features: Dict[str, float], policy: Dict[str, float]) -> str:
        """
        Compose a trace id from hashed feature/policy payload and timestamp bucket.
        """
        payload = {"features": features, "policy": policy}
        base = stable_hash(payload)
        # Keep it short for readability
        return f"trace-{base[:16]}"

    def run(self, features: Dict[str, float], policy: Dict[str, float]) -> DecisionOutput:
        """
        Execute deterministic scoring and produce decision artifacts.

        Args:
            features: sanitized, non-sensitive feature values (name -> float)
            policy: explicit weights and constraints (name -> float)

        Returns:
            DecisionOutput with prediction, confidence, importance, and trace metadata.
        """
        # Optional: if a real model is provided, you could combine model output with policy score
        # For transparency, we use policy-only scoring here.
        score = self._score_with_policy(features, policy)
        conf = self._confidence(score)
        importance = self._feature_importance(features, policy)

        # Data hash for audit reproducibility
        data_hash = stable_hash({"features": features})

        # Trace id (policy + features)
        trace_id = self._trace_id(features, policy)

        ts = time.time()

        return DecisionOutput(
            prediction=score,
            confidence=conf,
            feature_importance=importance,
            trace_id=trace_id,
            model_version=self.model_version,
            data_hash=data_hash,
            timestamp=ts,
        )