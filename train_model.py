
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle

print("Loading dataset...")

data = pd.read_csv("dataset/combined_sms_spam.csv")

# Drop rows where label or message is missing
data = data.dropna(subset=['label', 'message'])

# Convert labels to numbers
data['label'] = data['label'].map({'ham':0, 'spam':1, 'scam':1})

# Drop any rows where mapping failed (in case some label is neither ham nor spam)
data = data.dropna(subset=['label'])

X = data['message']
y = data['label']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Convert text to numbers
vectorizer = TfidfVectorizer()

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Train model
model = MultinomialNB()
model.fit(X_train_vec, y_train)

accuracy = model.score(X_test_vec, y_test)

print("Model accuracy:", accuracy)

# Save model
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

print("Model saved successfully!")