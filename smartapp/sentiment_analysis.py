"""
Sentiment Analysis Module for Restaurant Feedback
Provides RNN-based sentiment analysis functionality for customer feedback
Uses trained LSTM model for sentiment classification (no fallback)
"""

import os
import re
import numpy as np
import pickle
from django.conf import settings

# Try to import TensorFlow - required for model-based analysis
try:
    from tensorflow.keras.models import load_model
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("Warning: TensorFlow not installed. Install with: pip install tensorflow")

class SentimentAnalyzer:
    """
    RNN-based sentiment analyzer for restaurant feedback
    Uses trained LSTM model for sentiment classification
    """

    _model = None
    _word_index = None
    _label_encoder = None
    _max_length = 200  # Must match training max_length
    _max_features = 5000  # Must match training max_features

    @classmethod
    def _load_model(cls):
        """Load the trained model and preprocessing objects"""
        if cls._model is None:
            if not TENSORFLOW_AVAILABLE:
                raise RuntimeError(
                    "TensorFlow is not installed. The trained LSTM model requires TensorFlow. "
                    "Please install it with: pip install tensorflow"
                )
            
            try:
                model_path = os.path.join(settings.BASE_DIR, 'smartapp', 'sentiment_model.h5')
                word_index_path = os.path.join(settings.BASE_DIR, 'smartapp', 'word_index.pkl')
                label_encoder_path = os.path.join(settings.BASE_DIR, 'smartapp', 'label_encoder.pkl')

                # Load the trained model
                cls._model = load_model(model_path)

                # Load word index for text preprocessing
                with open(word_index_path, 'rb') as f:
                    cls._word_index = pickle.load(f)

                # Load label encoder for decoding predictions
                with open(label_encoder_path, 'rb') as f:
                    cls._label_encoder = pickle.load(f)

                print(f"Model loaded successfully from {model_path}")
                print(f"Vocabulary size: {len(cls._word_index)}")
                print(f"Label classes: {cls._label_encoder.classes_}")

            except FileNotFoundError as e:
                raise RuntimeError(
                    f"Model file not found: {e}. "
                    "Please run 'python smartapp/export_model.py' to train and export the model."
                )
            except Exception as e:
                raise RuntimeError(f"Error loading model: {e}")

    @classmethod
    def analyze_sentiment(cls, text):
        """
        Analyze sentiment of given text using trained RNN model

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

            # Convert to sequence using word_index
            words = text.split()
            sequence_list = [cls._word_index.get(word, 0) for word in words]

            # Pad/truncate sequence to max_length
            if len(sequence_list) < cls._max_length:
                sequence_list = [0] * (cls._max_length - len(sequence_list)) + sequence_list
            else:
                sequence_list = sequence_list[:cls._max_length]

            # Make prediction
            sequence_array = np.array([sequence_list])
            predictions = cls._model.predict(sequence_array, verbose=0)[0]
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
            # Raise error instead of falling back - we want to use the model
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
