"""
Script to train and export the sentiment analysis model using sklearn.
This is a fallback solution when TensorFlow is not available.
"""

import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# Load and preprocess data
data = pd.read_csv('smartapp/swiggy.csv')
print(f"Loaded {len(data)} records from swiggy.csv")

# Clean and prepare data
data["Review"] = data["Review"].str.lower()
data["Review"] = data["Review"].replace(r'[^a-z0-9\s]', '', regex=True)


def label_sentiment_num(rating):
    if rating <= 2.5:
        return "negative"
    elif rating <= 3.5:
        return "neutral"
    else:
        return "positive"


data['sentiment'] = data['Avg Rating'].apply(label_sentiment_num)
data = data.dropna()
data = data.dropna(subset=['Review'])
print(f"After preprocessing: {len(data)} records")

# Features and labels
X = data['Review'].values
y = data['sentiment'].values

print(f"X shape: {len(X)}, y shape: {len(y)}")

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Create TF-IDF vectorizer
vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

print(f"Vocabulary size: {len(vectorizer.vocabulary_)}")

# Train Logistic Regression model
model = LogisticRegression(max_iter=1000, random_state=42)
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

# Test the model
test_reviews = [
    "The food was amazing and delicious!",
    "Terrible service and cold food",
    "It was okay, nothing special"
]

print("\nTesting saved model:")
for review in test_reviews:
    review_tfidf = vectorizer.transform([review])
    pred = model.predict(review_tfidf)[0]
    proba = model.predict_proba(review_tfidf)[0]
    confidence = float(max(proba) * 100)
    print(f"'{review}' -> {pred} ({confidence:.1f}%)")

print("\nModel export complete!")
