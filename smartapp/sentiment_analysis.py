"""
Sentiment Analysis Module for Restaurant Feedback
Uses trained model from Swiggy dataset for sentiment classification
"""

import os
import re
import pickle
from django.conf import settings

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class SentimentAnalyzer:
    """
    ML-based sentiment analyzer trained on Swiggy dataset
    Classifies feedback into: positive, negative, neutral
    """

    _model = None
    _vectorizer = None
    _model_loaded = False

    @classmethod
    def _load_model(cls):
        if cls._model_loaded:
            return
        
        if not SKLEARN_AVAILABLE:
            raise RuntimeError("scikit-learn not installed")
        
        try:
            model_path = os.path.join(settings.BASE_DIR, 'smartapp', 'sentiment_model.pkl')
            vectorizer_path = os.path.join(settings.BASE_DIR, 'smartapp', 'sentiment_vectorizer.pkl')

            with open(model_path, 'rb') as f:
                cls._model = pickle.load(f)
            with open(vectorizer_path, 'rb') as f:
                cls._vectorizer = pickle.load(f)

            cls._model_loaded = True
            print(f"Model loaded successfully!")
            print(f"Classes: {cls._model.classes_}")

        except FileNotFoundError as e:
            raise RuntimeError(f"Model not found. Run: python smartapp/export_model.py")
        except Exception as e:
            raise RuntimeError(f"Error loading model: {e}")

    @classmethod
    def analyze_sentiment(cls, text):
        if not text:
            return {'sentiment': 'neutral', 'score': 0, 'confidence': 0}

        cls._load_model()

        try:
            text = text.lower().strip()
            text = re.sub(r'[^\w\s]', '', text)

            text_tfidf = cls._vectorizer.transform([text])
            sentiment = cls._model.predict(text_tfidf)[0]
            proba = cls._model.predict_proba(text_tfidf)[0]
            confidence = float(max(proba) * 100)

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
            raise RuntimeError(f"Sentiment analysis failed: {str(e)}")

    @classmethod
    def get_sentiment_description(cls, sentiment):
        descriptions = {
            'positive': 'Customer expressed satisfaction',
            'negative': 'Customer expressed dissatisfaction',
            'neutral': 'Customer provided neutral feedback'
        }
        return descriptions.get(sentiment, 'Sentiment not determined')
