from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from src.preprocess import preprocess_text
from src.similarity import calculate_similarity
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:sushil58@localhost/plag'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

# Push the application context
app.app_context().push()

# Create the SQLAlchemy instance
db = SQLAlchemy(app)

UPLOAD_FOLDER = 'data/documents'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define the Document model
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    content = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create all tables
db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Save uploaded files
        files = request.files.getlist('file')
        if len(files) > 50:
            return "Maximum 50 files are allowed."
        
        # Store uploaded files in the database
        for file in files:
            if file.filename != '':
                filename = secure_filename(file.filename)
                content = file.read().decode('utf-8')
                document = Document(filename=filename, content=content)
                db.session.add(document)
                db.session.commit()

        return redirect(url_for('results'))
    
    return render_template('index.html')

@app.route('/results')
def results():
    documents = Document.query.all()
    processed_texts = [preprocess_text(doc.content) for doc in documents]
    
    similarities = []
    num_documents = len(processed_texts)
    for i in range(num_documents):
        for j in range(i + 1, num_documents):
            similarity = calculate_similarity(processed_texts[i], processed_texts[j])
            similarities.append((documents[i].filename, documents[j].filename, similarity))
    
    return render_template('results.html', similarities=similarities)

if __name__ == "__main__":
    app.run(debug=True)
