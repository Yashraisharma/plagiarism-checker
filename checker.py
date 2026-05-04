import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(text1, text2):
    """Calculates Cosine Similarity between two strings."""
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    # Compute similarity between the first and second vector
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return similarity[0][0]

def get_reference_files(directory="database"):
    """Reads all text files in the database folder for comparison."""
    files = [f for f in os.listdir(directory) if f.endswith('.txt')]
    docs = []
    for f in files:
        with open(os.path.join(directory, f), 'r', encoding='utf-8') as file:
            docs.append({"name": f, "content": file.read()})
    return docs
