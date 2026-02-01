"""
Script to train and export the LSTM sentiment analysis model.
Run this script to generate the model files for use in the Django app.
"""

import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from tensorflow.keras.models import load_model

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
print(f"After preprocessing: {len(data)} records")

# Build vocabulary
max_features = 5000
max_length = 200

def build_vocab(texts, max_features=None):
    word_counts = {}
    for text in texts:
        for word in text.split():
            word_counts[word] = word_counts.get(word, 0) + 1
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    if max_features:
        sorted_words = sorted_words[:max_features]
    word_index = {word: idx+1 for idx, (word, _) in enumerate(sorted_words)}
    return word_index

word_index = build_vocab(data["Review"].tolist(), max_features=max_features)
print(f"Vocabulary size: {len(word_index)}")

# Convert texts to sequences
def texts_to_sequences(texts, word_index):
    sequences = []
    for text in texts:
        seq = [word_index.get(word, 0) for word in text.split()]
        sequences.append(seq)
    return sequences

sequences = texts_to_sequences(data["Review"].tolist(), word_index)

# Pad sequences
def pad_sequences_custom(sequences, maxlen):
    padded = []
    for seq in sequences:
        if len(seq) < maxlen:
            seq = [0]*(maxlen - len(seq)) + seq
        else:
            seq = seq[:maxlen]
        padded.append(seq)
    return np.array(padded)

X = pad_sequences_custom(sequences, max_length)
y = data['sentiment'].values

print(f"X shape: {X.shape}, y shape: {y.shape}")

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
X_train, X_val, y_train, y_val = train_test_split(
    X_train, y_train, test_size=0.1, random_state=42, stratify=y_train
)

# Encode labels
encoder = LabelEncoder()
y_train = encoder.fit_transform(y_train)
y_val = encoder.transform(y_val)
y_test = encoder.transform(y_test)

print(f"Label classes: {encoder.classes_}")

# Build and train model
embedding_dim = 128
model = Sequential([
    Embedding(input_dim=max_features, output_dim=embedding_dim),
    LSTM(128, return_sequences=True),
    Dropout(0.3),
    LSTM(64),
    Dropout(0.3),
    Dense(64, activation="relu"),
    Dense(3, activation="softmax")
])

model.compile(
    loss="sparse_categorical_crossentropy",
    optimizer="adam",
    metrics=["accuracy"]
)

model.summary()

print("Training model...")
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=10,
    batch_size=64
)

# Evaluate
loss, acc = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {acc:.2f}")

# Save model and artifacts
model.save('smartapp/sentiment_model.h5')
print("Saved model to smartapp/sentiment_model.h5")

with open('smartapp/word_index.pkl', 'wb') as f:
    pickle.dump(word_index, f)
print("Saved word_index to smartapp/word_index.pkl")

with open('smartapp/label_encoder.pkl', 'wb') as f:
    pickle.dump(encoder, f)
print("Saved label_encoder to smartapp/label_encoder.pkl")

# Test the model
test_reviews = [
    "The food was amazing and delicious!",
    "Terrible service and cold food",
    "It was okay, nothing special"
]

def preprocess_text(text, word_index, max_length):
    text = text.lower().strip()
    text = ''.join(c for c in text if c.isalnum() or c.isspace())
    words = text.split()
    sequence = [word_index.get(word, 0) for word in words]
    sequence = sequence + [0] * (max_length - len(sequence))
    return np.array([sequence])

print("\nTesting saved model:")
for review in test_reviews:
    seq = preprocess_text(review, word_index, max_length)
    pred = model.predict(seq, verbose=0)[0]
    pred_class = np.argmax(pred)
    sentiment = encoder.inverse_transform([pred_class])[0]
    confidence = float(pred[pred_class] * 100)
    print(f"'{review}' -> {sentiment} ({confidence:.1f}%)")

print("\nModel export complete!")
