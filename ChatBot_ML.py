import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3

file_path = "/content/drive/MyDrive/Colab Notebooks/train.csv"
df = pd.read_csv(file_path, encoding="ISO-8859-1")

complaints = df["SentimentText"].astype(str).tolist()

vectorizer = TfidfVectorizer(stop_words="english")
X = vectorizer.fit_transform(complaints)

conn = sqlite3.connect("complaints.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_complaint TEXT,
        category TEXT
    )
''')
conn.commit()

def categorize_complaint(user_query):
    query_vector = vectorizer.transform([user_query])  # Convert query to vector
    similarities = cosine_similarity(query_vector, X)  # Compute similarity
    best_match_index = similarities.argmax()  # Find the best match
    similarity_score = similarities[0, best_match_index]  # Get similarity score

    # Categorizes the complaints according to the similarity score
    if similarity_score > 0.5:
        category = "Priority Complaint"
    else:
        category = "Normal Complaint"

    # Store in database
    cursor.execute("INSERT INTO complaints (user_complaint, category) VALUES (?, ?)",
                   (user_query, category))
    conn.commit()

    return category

def file_comlaint():
    print("🚆 Railway Complaint Chatbot (Type 'exit' to stop) 🚆")

    while True:
        user_query = input("\nEnter your railway complaint: ")

        if user_query.lower() == "exit":
            print("🔴 Thank you for your patience! All complaints are stored in the database.")
            break

        category = categorize_complaint(user_query)
        print(f"✅ Your complaint is categorized as: {category}")


def display_comlaints():
    cursor.execute("SELECT user_complaint, category FROM complaints")
    records = cursor.fetchall()

    priority_complaints = [row[0] for row in records if row[1] == "Priority Complaint"]
    normal_complaints = [row[0] for row in records if row[1] == "Normal Complaint"]

    print("\n🔴 Priority Complaints")
    print("-" * 30)
    for complaint in priority_complaints:
        print(complaint)

    print("\n🟢 Normal Complaints")
    print("-" * 30)
    for complaint in normal_complaints:
        print(complaint)


def delete_all_complaints():
    conn = sqlite3.connect("complaints.db")
    cursor = conn.cursor()


    cursor.execute("DELETE FROM complaints")
    conn.commit()

    print("✅ All complaints have been deleted from the database.")