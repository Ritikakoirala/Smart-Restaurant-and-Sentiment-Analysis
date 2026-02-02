"""
Sentiment Analysis Module for Restaurant Feedback
Provides ML-based sentiment analysis functionality for customer feedback
Uses trained Logistic Regression model with TF-IDF features
"""

import os
import re
import pickle
from django.conf import settings

# Try to import sklearn - required for model-based analysis
try:
    import sklearn.feature_extraction.text
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not installed. "
          "Install with: pip install scikit-learn")


class SentimentAnalyzer:
    """
    ML-based sentiment analyzer for restaurant feedback
    Uses trained Logistic Regression model with TF-IDF features
    """

    _model = None
    _vectorizer = None
    _model_loaded = False

    @classmethod
    def _load_model(cls):
        """Load the trained model and vectorizer"""
        if cls._model_loaded:
            return

        if not SKLEARN_AVAILABLE:
            raise RuntimeError(
                "scikit-learn is not installed. "
                "The sentiment model requires scikit-learn. "
                "Please install it with: pip install scikit-learn"
            )

        try:
            model_path = os.path.join(
                settings.BASE_DIR, 'smartapp', 'sentiment_model.pkl')
            vectorizer_path = os.path.join(
                settings.BASE_DIR, 'smartapp', 'sentiment_vectorizer.pkl')

            # Load the trained model
            with open(model_path, 'rb') as f:
                cls._model = pickle.load(f)

            # Load the vectorizer
            with open(vectorizer_path, 'rb') as f:
                cls._vectorizer = pickle.load(f)

            cls._model_loaded = True
            print(f"Model loaded successfully from {model_path}")
            vocab_size = len(cls._vectorizer.vocabulary_)
            print(f"Vectorizer vocabulary size: {vocab_size}")

        except FileNotFoundError as e:
            raise RuntimeError(
                f"Model file not found: {e}. "
                "Please run 'python smartapp/export_model.py' to "
                "train and export the model."
            )
        except Exception as e:
            raise RuntimeError(f"Error loading model: {e}")

    @classmethod
    def analyze_sentiment(cls, text):
        """
        Analyze sentiment of given text using trained model

        Args:
            text (str): The feedback text to analyze

        Returns:
            dict: Contains sentiment, score, and confidence
        """
        if not text:
            return {'sentiment': 'neutral', 'score': 0, 'confidence': 0}

        # Load model if not loaded
        cls._load_model()

        try:
            # Preprocess text
            text = text.lower().strip()
            text = re.sub(r'[^\w\s]', '', text)

            # Convert to TF-IDF features
            text_tfidf = cls._vectorizer.transform([text])

            # Predict
            sentiment = cls._model.predict(text_tfidf)[0]

            # Get confidence
            proba = cls._model.predict_proba(text_tfidf)[0]
            confidence = float(max(proba) * 100)

            # Convert to score (-1 to 1 range)
            if sentiment == 'positive':
                score = 1
            elif sentiment == 'negative':
                score = -1
            else:
                score = 0

            return {
                'sentiment': sentiment,
                'score': score,
                'confidence': round(confidence, 2)
            }

        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            raise RuntimeError(f"Sentiment analysis failed: {str(e)}")

    @classmethod
    def get_sentiment_description(cls, sentiment):
        """
        Get human-readable description for sentiment

        Args:
            sentiment (str): The sentiment value

        Returns:
            str: Human-readable description
        """
        descriptions = {
            'positive': 'Customer expressed satisfaction',
            'negative': 'Customer expressed dissatisfaction',
            'neutral': 'Customer provided neutral feedback'
        }
        return descriptions.get(sentiment, 'Sentiment not determined')
