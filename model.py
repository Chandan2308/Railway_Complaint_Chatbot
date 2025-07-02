import pickle
import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ✅ Define the ComplaintClassifier class
class ComplaintClassifier:
    def __init__(self, vectorizer, X):
        self.vectorizer = vectorizer
        self.X = X

    def categorize_complaint(self, user_query):
        query_vector = self.vectorizer.transform([user_query])
        similarities = cosine_similarity(query_vector, self.X)
        best_match_index = similarities.argmax()
        similarity_score = similarities[0, best_match_index]

        return "Priority Complaint" if similarity_score > 0.5 else "Normal Complaint"

""" Load and preprocess data """
file_path = os.path.abspath("D:/Projects/Chatbot/dataset/train.csv")
df = pd.read_csv(file_path, encoding="ISO-8859-1")

# Convert complaints to list
complaints = df["SentimentText"].astype(str).tolist()

# Convert complaints to TF-IDF vectors
vectorizer = TfidfVectorizer(stop_words="english")
X = vectorizer.fit_transform(complaints)

# ✅ Train & Save Model
model = ComplaintClassifier(vectorizer, X)
model_path = os.path.abspath("D:/Projects/Chatbot/model.pkl")

with open(model_path, "wb") as file:
    pickle.dump(model, file)

print("Model has been successfully trained and saved! 🎉")
