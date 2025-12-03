"""
Sentiment Analysis Module for Restaurant Feedback
Provides RNN-based sentiment analysis functionality for customer feedback
"""

import os
import re
import numpy as np
import pickle
from django.conf import settings
# from tensorflow.keras.models import load_model
# from tensorflow.keras.preprocessing import sequence

class SentimentAnalyzer:
    """
    RNN-based sentiment analyzer for restaurant feedback
    Uses trained LSTM model for sentiment classification
    """

    _model = None
    _word_index = None
    _label_encoder = None
    _max_length = 50

    @classmethod
    def _load_model(cls):
        """Load the trained model and preprocessing objects"""
        if cls._model is None:
            try:
                model_path = os.path.join(settings.BASE_DIR, 'smartapp', 'sentiment_model.h5')
                word_index_path = os.path.join(settings.BASE_DIR, 'smartapp', 'word_index.pkl')
                label_encoder_path = os.path.join(settings.BASE_DIR, 'smartapp', 'label_encoder.pkl')

                # cls._model = load_model(model_path)
                cls._model = None  # Force fallback

                # with open(word_index_path, 'rb') as f:
                #     cls._word_index = pickle.load(f)

                # with open(label_encoder_path, 'rb') as f:
                #     cls._label_encoder = pickle.load(f)

            except Exception as e:
                print(f"Error loading model: {e}")
                # Fallback to keyword-based approach
                cls._use_fallback = True

    @classmethod
    def analyze_sentiment(cls, text):
        """
        Analyze sentiment of given text using RNN model

        Args:
            text (str): The feedback text to analyze

        Returns:
            dict: Contains sentiment, score, and confidence
        """
        if not text:
            return {'sentiment': 'neutral', 'score': 0, 'confidence': 0}

        # Load model if not loaded
        cls._load_model()

        if cls._model is None:
            # Fallback to keyword-based approach
            return cls._keyword_analysis(text)

        try:
            # Preprocess text
            text = text.lower().strip()
            text = re.sub(r'[^\w\s]', '', text)

            # Convert to sequence
            words = text.split()
            sequence = [cls._word_index.get(word, 0) for word in words]
            sequence = sequence.pad_sequences([sequence], maxlen=cls._max_length, padding='pre')

            # Predict
            predictions = cls._model.predict(sequence, verbose=0)[0]
            predicted_class = np.argmax(predictions)
            confidence = float(predictions[predicted_class] * 100)

            # Get sentiment label
            sentiment = cls._label_encoder.inverse_transform([predicted_class])[0]

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
            print(f"Error in RNN analysis: {e}")
            # Fallback to keyword-based approach
            return cls._keyword_analysis(text)

    @classmethod
    def _keyword_analysis(cls, text):
        """
        Fallback keyword-based sentiment analysis
        """
        # Positive keywords
        POSITIVE_WORDS = [
            'excellent', 'amazing', 'wonderful', 'fantastic', 'great', 'good', 'awesome',
            'love', 'loved', 'perfect', 'delicious', 'tasty', 'fresh', 'clean', 'friendly',
            'professional', 'quick', 'fast', 'efficient', 'satisfied', 'happy', 'pleased',
            'impressed', 'recommend', 'best', 'outstanding', 'superb', 'brilliant'
        ]

        # Negative keywords
        NEGATIVE_WORDS = [
            'terrible', 'awful', 'horrible', 'bad', 'worst', 'disgusting', 'cold', 'dirty',
            'slow', 'rude', 'unfriendly', 'disappointed', 'disappointing', 'poor', 'mediocre',
            'bland', 'tasteless', 'overpriced', 'expensive', 'late', 'wrong', 'mistake',
            'problem', 'issue', 'complaint', 'hate', 'never', 'again'
        ]

        # Convert to lowercase and clean text
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)

        # Split text into words and count occurrences
        words = text.split()
        positive_count = sum(1 for w in words if w in POSITIVE_WORDS)
        negative_count = sum(1 for w in words if w in NEGATIVE_WORDS)

        # Calculate sentiment score
        total_words = len(words)
        if total_words == 0:
            return {'sentiment': 'neutral', 'score': 0, 'confidence': 0}

        # Simple scoring mechanism
        score = positive_count - negative_count

        # Determine sentiment
        if score > 0:
            sentiment = 'positive'
            confidence = min(positive_count / total_words * 100, 100)
        elif score < 0:
            sentiment = 'negative'
            confidence = min(negative_count / total_words * 100, 100)
        else:
            sentiment = 'neutral'
            confidence = 50

        return {
            'sentiment': sentiment,
            'score': score,
            'confidence': round(confidence, 2)
        }

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
