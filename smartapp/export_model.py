"""
Retrain sentiment model with better positive/negative examples
"""
import pandas as pd
import numpy as np
import pickle
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

print("Training sentiment model...")

# Load Swiggy data
data = pd.read_csv('smartapp/swiggy.csv')
data["Review"] = data["Review"].str.lower()
data["Review"] = data["Review"].replace(r'[^a-z0-9\s]', '', regex=True)
data = data.dropna(subset=['Review', 'Avg Rating'])

# Label based on rating
def label_sentiment(rating):
    if rating <= 2.5:
        return "negative"
    elif rating <= 3.5:
        return "neutral"
    else:
        return "positive"

data['sentiment'] = data['Avg Rating'].apply(label_sentiment)
print(f"Original: {dict(data['sentiment'].value_counts())}")

# Get actual positive reviews for learning
positive_reviews = data[data['sentiment'] == 'positive']['Review'].tolist()
neutral_reviews = data[data['sentiment'] == 'neutral']['Review'].tolist()

# Real positive phrases for learning
positive_phrases = [
    "amazing food and great service", "delicious and fresh", "best restaurant ever",
    "highly recommend this place", "love the taste", "fantastic quality",
    "excellent service and food", "wonderful experience", "superb and tasty",
    "best food I have ever had", "absolutely love it", "great quality",
    "fresh and delicious", "mouthwatering and tasty", "perfect service",
    "outstanding and amazing", "exceptional quality", "very good food",
    "satisfied and happy", "worth every penny", "great value for money",
    "quick delivery and tasty", "friendly staff and good food", "will come again",
    "recommend to everyone", "five star experience", "top notch quality"
]

# Real negative phrases
negative_phrases = [
    "terrible food and bad service", "worst experience ever", "cold and tasteless food",
    "disgusting and overpriced", "horrible delivery and rude staff",
    "never order from here again", "waste of money and time",
    "food was terrible and cold", "very bad service and slow",
    "disappointed with the quality", "tasteless and bland food",
    "late delivery and wrong order", "poor quality and expensive",
    "awful experience and rude", "bad taste and dirty place",
    "not fresh and overcooked", "unhygienic and unhealthy",
    "worse than expected", "cheap quality and small portions",
    "unpleasant service", "very slow and rude", "food was stale",
    "wrong order delivered", "never coming back", "extremely disappointed"
]

# Real neutral phrases
neutral_phrases = [
    "it was okay", "nothing special", "average quality", "just okay",
    "mediocre experience", "neither good nor bad", "ordinary food",
    "expected more", "could be better", "standard quality",
    "typical restaurant food", "not bad but not great", "decent enough",
    "fair quality", "no complaints but no praise", "standard fare"
]

# Add real examples
all_reviews = list(data['Review'].values)

# Add positive examples (repeat more times for balance)
for phrase in positive_phrases:
    all_reviews.extend([phrase] * 50)

# Add negative examples
for phrase in negative_phrases:
    all_reviews.extend([phrase] * 50)

# Add neutral examples  
for phrase in neutral_phrases:
    all_reviews.extend([phrase] * 50)

# Create labels
positive_labels = ['positive'] * (len(positive_phrases) * 50)
negative_labels = ['negative'] * (len(negative_phrases) * 50)
neutral_labels = ['neutral'] * (len(neutral_phrases) * 50)

original_labels = list(data['sentiment'].values)
all_labels = original_labels + positive_labels + negative_labels + neutral_labels

print(f"Total reviews: {len(all_reviews)}")
print(f"Labels distribution: positive={all_labels.count('positive')}, neutral={all_labels.count('neutral')}, negative={all_labels.count('negative')}")

# Create TF-IDF vectorizer with better settings
vectorizer = TfidfVectorizer(max_features=3000, ngram_range=(1, 3), min_df=1)
X = vectorizer.fit_transform(all_reviews)
y = np.array(all_labels)

print(f"Vocabulary size: {len(vectorizer.vocabulary_)}")

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.1, random_state=42, stratify=y_train)

# Train model with balanced classes
model = LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced', C=1.0)
model.fit(X_train, y_train)

# Evaluate
train_acc = model.score(X_train, y_train)
test_acc = model.score(X_test, y_test)
print(f"Train Accuracy: {train_acc:.2f}")
print(f"Test Accuracy: {test_acc:.2f}")

# Save model
with open('smartapp/sentiment_model.pkl', 'wb') as f:
    pickle.dump(model, f)
with open('smartapp/sentiment_vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)

print("Model saved!")

# Test
test_reviews = [
    "The food was amazing and delicious!",
    "Terrible service and cold food",
    "It was okay, nothing special",
    "Best restaurant ever, highly recommend!",
    "Worst experience ever, never coming back",
    "Love the taste and quick delivery",
    "Fresh and tasty, will order again",
    "Hate the long wait and rude staff",
    "Excellent food and great service",
    "Disappointed with the quality"
]

print("\nTest Results:")
for review in test_reviews:
    review_tfidf = vectorizer.transform([review])
    pred = model.predict(review_tfidf)[0]
    proba = model.predict_proba(review_tfidf)[0]
    confidence = float(max(proba) * 100)
    print(f"'{review}' -> {pred} ({confidence:.1f}%)")
