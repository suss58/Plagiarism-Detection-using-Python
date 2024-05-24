import os
from preprocess import preprocess_text
from similarity import calculate_similarity

def load_documents(doc_path):
    documents = []
    for filename in os.listdir(doc_path):
        if filename.endswith('.txt'):
            with open(os.path.join(doc_path, filename), 'r', encoding='utf-8') as file:
                documents.append(file.read())
    return documents

def main():
    doc_path = 'data/documents'
    documents = load_documents(doc_path)
    
    processed_texts = [preprocess_text(doc) for doc in documents]

    num_documents = len(processed_texts)
    for i in range(num_documents):
        for j in range(i + 1, num_documents):
            similarity = calculate_similarity(processed_texts[i], processed_texts[j])
            print(f"Similarity between document {i + 1} and document {j + 1}: {similarity}")

if __name__ == "__main__":
    main()
