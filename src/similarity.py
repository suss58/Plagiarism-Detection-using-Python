from src.preprocess import preprocess_text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(text1, text2):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return cosine_sim[0][0]

def perform_plagiarism_check(files):
    similarity_scores = {}
    for i, file1 in enumerate(files):
        for j, file2 in enumerate(files):
            if i != j:
                text1 = preprocess_text(file1.content)
                text2 = preprocess_text(file2.content)
                similarity = calculate_similarity(text1, text2)
                similarity_scores[(file1.id, file2.id)] = similarity
    return similarity_scores
