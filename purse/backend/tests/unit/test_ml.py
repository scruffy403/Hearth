import pytest
from app.services.ml import MLService, MLPrediction


def make_training_data() -> list[dict]:
    """Synthetic training corpus covering several categories."""
    return [
        {"merchant_clean": "Tesco", "category": "Groceries"},
        {"merchant_clean": "Sainsbury's", "category": "Groceries"},
        {"merchant_clean": "Asda", "category": "Groceries"},
        {"merchant_clean": "Lidl", "category": "Groceries"},
        {"merchant_clean": "Morrisons", "category": "Groceries"},
        {"merchant_clean": "Costa Coffee", "category": "Eating Out"},
        {"merchant_clean": "McDonald's", "category": "Eating Out"},
        {"merchant_clean": "Starbucks", "category": "Eating Out"},
        {"merchant_clean": "Pret A Manger", "category": "Eating Out"},
        {"merchant_clean": "Caffe Nero", "category": "Eating Out"},
        {"merchant_clean": "Netflix", "category": "Subscriptions"},
        {"merchant_clean": "Spotify", "category": "Subscriptions"},
        {"merchant_clean": "Amazon Prime Video", "category": "Subscriptions"},
        {"merchant_clean": "Microsoft 365", "category": "Subscriptions"},
        {"merchant_clean": "Disney Plus", "category": "Subscriptions"},
        {"merchant_clean": "Shell", "category": "Transport"},
        {"merchant_clean": "Trainline", "category": "Transport"},
        {"merchant_clean": "Avanti West Coast", "category": "Transport"},
        {"merchant_clean": "South Western Railway", "category": "Transport"},
        {"merchant_clean": "Esso", "category": "Transport"},
    ]


class TestMLService:
    def test_train_requires_minimum_samples(self):
        """Model should not train on fewer than min_samples."""
        service = MLService(min_samples=5)
        tiny_corpus = [
            {"merchant_clean": "Tesco", "category": "Groceries"},
            {"merchant_clean": "Costa", "category": "Eating Out"},
        ]
        result = service.train(tiny_corpus)
        assert result.success is False
        assert "insufficient" in result.message.lower()

    def test_train_succeeds_with_sufficient_data(self):
        service = MLService(min_samples=5)
        result = service.train(make_training_data())
        assert result.success is True
        assert result.sample_count == 20

    def test_predict_returns_prediction_object(self):
        service = MLService(min_samples=5)
        service.train(make_training_data())
        prediction = service.predict("Waitrose")
        assert isinstance(prediction, MLPrediction)
        assert prediction.category in [
            "Groceries", "Eating Out", "Subscriptions", "Transport", "Other"
        ]
        assert 0.0 <= prediction.confidence <= 1.0
        assert prediction.source == "ml"

    def test_predict_groceries(self):
        service = MLService(min_samples=5)
        service.train(make_training_data())
        prediction = service.predict("Tesco Express")
        assert prediction.category == "Groceries"

    def test_predict_eating_out(self):
        service = MLService(min_samples=5)
        service.train(make_training_data())
        prediction = service.predict("Costa")
        assert prediction.category == "Eating Out"

    def test_predict_batch_returns_list(self):
        service = MLService(min_samples=5)
        service.train(make_training_data())
        merchants = ["Tesco", "Netflix", "Shell"]
        predictions = service.predict_batch(merchants)
        assert len(predictions) == 3
        assert all(isinstance(p, MLPrediction) for p in predictions)

    def test_predict_without_training_returns_other(self):
        """Untrained model should return Other rather than raising."""
        service = MLService(min_samples=5)
        prediction = service.predict("Some Merchant")
        assert prediction.category == "Other"
        assert prediction.source == "ml_untrained"

    def test_train_result_contains_category_distribution(self):
        service = MLService(min_samples=5)
        result = service.train(make_training_data())
        assert result.success is True
        assert "Groceries" in result.category_distribution
        assert result.category_distribution["Groceries"] == 5