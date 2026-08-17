from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from typing import Tuple, Set

def extract_keywords(resume_clean: str, job_clean: str, top_n: int = 25) -> Tuple[Set[str], Set[str]]:
    """
    Extracts important keywords/phrases from the preprocessed resume and job description using TF-IDF.
    Uses n-grams of range (1, 2) to capture single-word and double-word technical terms 
    (e.g., 'python', 'machine learning', 'software engineering').
    
    Args:
        resume_clean (str): Preprocessed resume text.
        job_clean (str): Preprocessed job description text.
        top_n (int): Max number of keywords to extract per document.
        
    Returns:
        Tuple[Set[str], Set[str]]: Sets of extracted keywords for (resume, job_description).
    """
    # Check if either document is empty to avoid vectorizer errors
    if not resume_clean.strip() or not job_clean.strip():
        return set(), set()
        
    # Fit and transform TF-IDF on both preprocessed texts
    # We use ngram_range=(1,3) to capture unigrams, bigrams, and trigrams
    vectorizer = TfidfVectorizer(ngram_range=(1, 3))
    
    try:
        tfidf_matrix = vectorizer.fit_transform([resume_clean, job_clean])
        feature_names = np.array(vectorizer.get_feature_names_out())
        
        # 1. Extract Resume Keywords (index 0)
        resume_row = tfidf_matrix[0].toarray()[0]
        resume_sorted_idx = np.argsort(resume_row)[::-1]
        resume_keywords = [
            feature_names[i] 
            for i in resume_sorted_idx 
            if resume_row[i] > 0
        ][:top_n]
        
        # 2. Extract Job Description Keywords (index 1)
        job_row = tfidf_matrix[1].toarray()[0]
        job_sorted_idx = np.argsort(job_row)[::-1]
        job_keywords = [
            feature_names[i] 
            for i in job_sorted_idx 
            if job_row[i] > 0
        ][:top_n]
        
        return set(resume_keywords), set(job_keywords)
        
    except Exception as e:
        # Fallback to simple split token sets if vectorizer fails
        resume_words = set(resume_clean.split())
        job_words = set(job_clean.split())
        return resume_words, job_words
