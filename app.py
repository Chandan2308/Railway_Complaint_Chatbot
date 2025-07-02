import numpy as np
from flask import Flask,request, jsonify, render_template
import pickle
import os
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Dummy credentials for admin login
ADMIN_CREDENTIALS = {"admin": "password123"}

# ✅ Define the ComplaintClassifier class before unpickling
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


# Define a helper function to load the model safely
def load_model(file_path):
    with open(file_path, "rb") as file:
        return pickle.load(file)

""" Load the trained model """
model_path = os.path.abspath("D:/Projects/Chatbot/model.pkl")

try:
    model = load_model(model_path)  # ✅ This should now load without errors!
except AttributeError:
    print("Error: Could not recognize the 'ComplaintClassifier' class. Make sure it is defined when pickling.")


def get_db_connection():
    conn = sqlite3.connect("complaints.db",check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # cursor = conn.cursor()
    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS complaints (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         user_complaint TEXT,
    #         category TEXT
    #     )
    # ''')
    # conn.commit()
    return conn 

flask_app = Flask(__name__)

@flask_app.route("/")
def Home():
    return render_template("index.html")

@flask_app.route("/about")
def About():
    return render_template("about.html")


@flask_app.route("/process_complaint",methods=["post"])
def process_complaint():
    if request.content_type == "application/json":
        data = request.get_json()
        user_query = data.get("complaint", "")
    else:
        user_query = request.form.get("complaint", "")

    if not user_query:
        return jsonify({"error": "No input provided."}), 400

    category = model.categorize_complaint(user_query)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO complaints (user_complaint, category) VALUES (?, ?)",
                   (user_query, category))
    conn.commit()
    conn.close()

    # Return JSON response
    return jsonify({
        "response": "Thank you! Your complaint has been registered.",
        "category": f"The complaint is of category: {category}"
    })


@flask_app.route("/view_complaints")
def view_complaints():
    return render_template("view.html")

@flask_app.route("/admin_login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
            return jsonify({"success": True})  # Frontend will handle redirection
        else:
            return jsonify({"success": False})  # Invalid login
        
    return render_template("admin_login.html")


if __name__ == "__main__":
    flask_app.run(debug=True)