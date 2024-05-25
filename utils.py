from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk import download

download('punkt')
download('stopwords')

def check_plagiarism(content1, content2):
    # Tokenize the contents into words
    words1 = word_tokenize(content1.lower())
    words2 = word_tokenize(content2.lower())
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    words1 = [word for word in words1 if word.isalnum() and word not in stop_words]
    words2 = [word for word in words2 if word.isalnum() and word not in stop_words]
    
    # Find consecutive 5-word sequences
    sequences1 = set(tuple(words1[i:i+5]) for i in range(len(words1) - 4))
    sequences2 = set(tuple(words2[i:i+5]) for i in range(len(words2) - 4))
    
    # Calculate the intersection (common sequences) and union (total sequences) of the two sets
    common_sequences = sequences1.intersection(sequences2)
    total_sequences = sequences1.union(sequences2)
    
    # Calculate the percentage similarity
    similarity_percentage = len(common_sequences) /(1+ len(total_sequences)) * 100
    
    # Determine if plagiarism is detected based on the similarity percentage
    plagiarism_detected = similarity_percentage > 0
    
    return plagiarism_detected, similarity_percentage

# Example usage
text1 = "This is a sample text for testing similarity."
text2 = "This is a text for testing similarity with different content."

plagiarism_detected, similarity_percentage = check_plagiarism(text1, text2)
if plagiarism_detected:
    print("Plagiarism detected!")
else:
    print("No plagiarism detected.")
print(f"Similarity Percentage: {similarity_percentage:.2f}%")
