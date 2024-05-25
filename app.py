from difflib import SequenceMatcher
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from utils import check_plagiarism

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:sushil58@localhost/plagiarism_detection'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)

class FileContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

class CheckedPair(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file1_id = db.Column(db.Integer)
    file2_id = db.Column(db.Integer)
    plagiarism_detected = db.Column(db.Boolean)
    similarity_percentage = db.Column(db.Float)
    checked_at = db.Column(db.DateTime, default=datetime.utcnow)
def check_plagiarism(text1, text2, threshold=0.8):
    """
    Check plagiarism between two texts.

    Args:
    - text1 (str): The first text to compare.
    - text2 (str): The second text to compare.
    - threshold (float): The similarity threshold to consider as plagiarism.

    Returns:
    - plagiarism_detected (bool): True if plagiarism is detected, False otherwise.
    - similarity_percentage (float): The percentage of similarity between the texts.
    """
    # Use SequenceMatcher to compare the texts
    matcher = SequenceMatcher(None, text1, text2)
    similarity_ratio = matcher.ratio()

    # Determine if plagiarism is detected based on the similarity ratio and threshold
    plagiarism_detected = similarity_ratio >= threshold

    return plagiarism_detected, similarity_ratio * 100

@app.route('/')
def index():
    files = FileContent.query.all()
    return render_template('index.html', files=files)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        new_file = FileContent(filename=filename, content=content)
        db.session.add(new_file)
        db.session.commit()
        
        flash('File successfully uploaded')
        return redirect(url_for('index'))

@app.route('/view_all_files', methods=['GET'])
def view_all_files():
    files = FileContent.query.all()
    return render_template('index.html', files=files)




@app.route('/check', methods=['POST'])
def check_plagiarism_route():
    results = []
    checked_pairs = set()

    all_files = FileContent.query.all()
    filenames = [file.filename for file in all_files]
    documents = [file.content for file in all_files]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    for i, file1 in enumerate(all_files):
        for j, file2 in enumerate(all_files):
            if i != j and (i, j) not in checked_pairs and (j, i) not in checked_pairs:
                similarity_matrix = cosine_similarity(tfidf_matrix[i], tfidf_matrix[j])
                similarity_percentage = similarity_matrix[0][0] * 100
                plagiarism_detected = similarity_percentage > 50  # Adjust threshold as needed
                results.append({
                    'file1': file1.filename,
                    'file2': file2.filename,
                    'plagiarism_detected': plagiarism_detected,
                    'similarity_percentage': similarity_percentage
                })
                checked_pairs.add((i, j))

                # Store the checked pair in the database
                new_checked_pair = CheckedPair(file1_id=i, file2_id=j, plagiarism_detected=plagiarism_detected, similarity_percentage=similarity_percentage)
                db.session.add(new_checked_pair)
                db.session.commit()

    return render_template('index.html', results=results)


@app.route('/delete_file/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    file_to_delete = FileContent.query.get_or_404(file_id)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_to_delete.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.session.delete(file_to_delete)
    db.session.commit()
    flash('File successfully deleted')
    return redirect(url_for('index'))



def create_database():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    create_database()
    app.run(debug=True)