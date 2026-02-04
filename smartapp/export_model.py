"""
Script to train and export the sentiment analysis model using sklearn.
Includes synthetic negative examples since the Swiggy dataset has no negative reviews.
"""

import pandas as pd
import numpy as np
import pickle
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Load and preprocess data
data = pd.read_csv('smartapp/swiggy.csv')
print(f"Loaded {len(data)} records from swiggy.csv")

# Clean and prepare data
data["Review"] = data["Review"].str.lower()
data["Review"] = data["Review"].replace(r'[^a-z0-9\s]', '', regex=True)
data = data.dropna(subset=['Review', 'Avg Rating'])

def label_sentiment_num(rating):
    if rating <= 2.5:
        return "negative"
    elif rating <= 3.5:
        return "neutral"
    else:
        return "positive"

data['sentiment'] = data['Avg Rating'].apply(label_sentiment_num)
print(f"Original sentiment distribution:\n{data['sentiment'].value_counts()}")

# Check if we have negative examples
negative_count = len(data[data['sentiment'] == 'negative'])

if negative_count == 0:
    print("No negative examples found in dataset. Adding synthetic negative examples...")
    
    # Create synthetic negative examples using common negative phrases
    negative_phrases = [
        "terrible food and bad service",
        "worst experience ever",
        "cold and tasteless food",
        "disgusting and overpriced",
        "horrible delivery and rude staff",
        "never order from here again",
        "waste of money and time",
        "food was terrible and cold",
        "very bad service and slow",
        "disappointed with the quality",
        "tasteless and bland food",
        "late delivery and wrong order",
        "poor quality and expensive",
        "awful experience and rude",
        "bad taste and dirty place",
        "not fresh and overcooked",
        "unhygienic and unhealthy",
        "worse than expected and cold",
        "cheap quality and small portions",
        "unpleasant and frustrating service"
    ]
    
    # Add synthetic negative examples
    synthetic_negative = pd.DataFrame({
        'Review': negative_phrases * 100,  # Repeat to get enough examples
        'sentiment': ['negative'] * (len(negative_phrases) * 100)
    })
    
    # Add to original data
    data = pd.concat([data[['Review', 'sentiment']], synthetic_negative], ignore_index=True)
    print(f"After adding synthetic negatives:\n{data['sentiment'].value_counts()}")

# Features and labels
X = data['Review'].values
y = data['sentiment'].values

print(f"X shape: {len(X)}, y shape: {len(y)}")

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Train distribution:\n{pd.Series(y_train).value_counts()}")
print(f"Test distribution:\n{pd.Series(y_test).value_counts()}")

# Create TF-IDF vectorizer
vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

print(f"Vocabulary size: {len(vectorizer.vocabulary_)}")

# Train Logistic Regression model with class weights
model = LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced')
model.fit(X_train_tfidf, y_train)

# Evaluate
train_acc = model.score(X_train_tfidf, y_train)
test_acc = model.score(X_test_tfidf, y_test)
print(f"Train Accuracy: {train_acc:.2f}")
print(f"Test Accuracy: {test_acc:.2f}")

# Save model and artifacts
with open('smartapp/sentiment_vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)
print("Saved vectorizer to smartapp/sentiment_vectorizer.pkl")

with open('smartapp/sentiment_model.pkl', 'wb') as f:
    pickle.dump(model, f)
print("Saved model to smartapp/sentiment_model.pkl")

# Test the model with diverse examples
test_reviews = [
    "The food was amazing and delicious!",
    "Terrible service and cold food",
    "It was okay, nothing special",
    "Best restaurant ever, highly recommend!",
    "Worst experience ever, never coming back",
    "Average food, nothing special",
    "Love the taste and quick delivery",
    "Hate the long wait and rude staff",
    "Fresh and tasty, will order again",
    "Stale food and dirty packaging"
]

print("\nTesting saved model:")
for review in test_reviews:
    review_tfidf = vectorizer.transform([review])
    pred = model.predict(review_tfidf)[0]
    proba = model.predict_proba(review_tfidf)[0]
    confidence = float(max(proba) * 100)
    print(f"'{review}' -> {pred} ({confidence:.1f}%)")

print("\nModel export complete!")
