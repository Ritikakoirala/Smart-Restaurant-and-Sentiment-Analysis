import pickle
import sys
sys.path.insert(0, '.')

# Load model
with open('smartapp/sentiment_model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('smartapp/sentiment_vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

print(f'Classes: {model.classes_}')

# Test
tests = [
    'Amazing food great service',
    'Terrible cold food bad service',
    'Okay nothing special',
    'Best restaurant ever',
    'Worst experience never back'
]

for t in tests:
    tfidf = vectorizer.transform([t])
    pred = model.predict(tfidf)[0]
    proba = model.predict_proba(tfidf)[0]
    conf = max(proba) * 100
    print(f'{t} -> {pred} ({conf:.1f}%)')
