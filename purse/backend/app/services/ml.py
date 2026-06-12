from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline


@dataclass
class MLPrediction:
    category: str
    confidence: float
    source: str  # 'ml' | 'ml_untrained'


@dataclass
class MLTrainingResult:
    success: bool
    message: str
    sample_count: int = 0
    category_distribution: dict[str, int] = field(default_factory=dict)


class MLService:
    """
    Lightweight ML categorisation pipeline.

    Uses TF-IDF character n-grams (2-4) + Logistic Regression to
    predict dashboard categories from normalised merchant names.

    Training data comes from YNAB-approved transactions — every
    transaction a human has confirmed or corrected is a training sample.
    """

    def __init__(self, min_samples: int = 5) -> None:
        self.min_samples = min_samples
        self._pipeline: Optional[Pipeline] = None
        self._classes: list[str] = []

    def train(self, corpus: list[dict]) -> MLTrainingResult:
        """
        Train the model on a list of merchant/category dicts.

        Args:
            corpus: List of {'merchant_clean': str, 'category': str} dicts

        Returns:
            MLTrainingResult with success status and metrics
        """
        if len(corpus) < self.min_samples:
            return MLTrainingResult(
                success=False,
                message=f"Insufficient training data: {len(corpus)} samples, "
                        f"minimum is {self.min_samples}",
                sample_count=len(corpus),
            )

        merchants = [item["merchant_clean"] for item in corpus]
        categories = [item["category"] for item in corpus]

        # Category distribution for the training log
        distribution: dict[str, int] = {}
        for cat in categories:
            distribution[cat] = distribution.get(cat, 0) + 1

        # Build and train the pipeline
        self._pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                analyzer="char",
                ngram_range=(2, 4),
                min_df=1,
            )),
            ("clf", LogisticRegression(
                max_iter=1000,
                random_state=42,
            )),
        ])

        self._pipeline.fit(merchants, categories)
        self._classes = list(self._pipeline.classes_)

        return MLTrainingResult(
            success=True,
            message=f"Trained on {len(corpus)} samples "
                    f"across {len(distribution)} categories",
            sample_count=len(corpus),
            category_distribution=distribution,
        )

    def predict(self, merchant_clean: str) -> MLPrediction:
        """
        Predict the category for a single merchant name.

        Returns MLPrediction with category, confidence score, and source.
        If the model hasn't been trained, returns Other with source
        'ml_untrained' rather than raising an exception.
        """
        if self._pipeline is None:
            return MLPrediction(
                category="Other",
                confidence=0.0,
                source="ml_untrained",
            )

        proba = self._pipeline.predict_proba([merchant_clean])[0]
        max_idx = int(proba.argmax())
        category = self._classes[max_idx]
        confidence = float(proba[max_idx])

        return MLPrediction(
            category=category,
            confidence=confidence,
            source="ml",
        )

    def predict_batch(self, merchants: list[str]) -> list[MLPrediction]:
        """
        Predict categories for a list of merchant names.

        More efficient than calling predict() in a loop since it
        runs the TF-IDF transform once for the whole batch.
        """
        if self._pipeline is None:
            return [
                MLPrediction(category="Other", confidence=0.0, source="ml_untrained")
                for _ in merchants
            ]

        probas = self._pipeline.predict_proba(merchants)
        predictions = []

        for proba in probas:
            max_idx = int(proba.argmax())
            predictions.append(MLPrediction(
                category=self._classes[max_idx],
                confidence=float(proba[max_idx]),
                source="ml",
            ))

        return predictions

    @property
    def is_trained(self) -> bool:
        return self._pipeline is not None