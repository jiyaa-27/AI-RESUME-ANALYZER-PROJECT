from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from utils.synonyms import SYNONYM_GROUPS

def expand_text_with_synonyms(text: str) -> str:
    """
    Scans the preprocessed text for any terms belonging to known synonym groups,
    and appends a unique group-tag for each matching group. This expands the text's
    vocabulary so that related synonyms (e.g. AWS vs Cloud vs GCP) align in vector space.
    
    Args:
        text (str): Preprocessed text.
        
    Returns:
        str: Expanded preprocessed text.
    """
    if not text:
        return ""
        
    expanded_text = text
    # Scan through groups and append tag if any group member matches
    for i, group in enumerate(SYNONYM_GROUPS):
        tag = f"__syngroup_{i}__"
        for term in group:
            # Use regex to match the exact term/phrase with word boundaries
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, expanded_text):
                expanded_text += f" {tag}"
                break  # Only append one tag per group to avoid double counting
                
    return expanded_text

def calculate_job_fit_score(resume_clean: str, job_clean: str) -> float:
    """
    Calculates the Job Fit Score using TF-IDF vectorization and cosine similarity
    on synonym-expanded representations of the resume and job description.
    
    Args:
        resume_clean (str): Preprocessed resume text.
        job_clean (str): Preprocessed job description text.
        
    Returns:
        float: Similarity score formatted as a percentage (0.0 to 100.0).
    """
    if not resume_clean.strip() or not job_clean.strip():
        return 0.0
        
    # Perform document expansion using synonym tags
    expanded_resume = expand_text_with_synonyms(resume_clean)
    expanded_job = expand_text_with_synonyms(job_clean)
    
    # Vectorizer to use unigrams, bigrams & trigrams
    vectorizer = TfidfVectorizer(ngram_range=(1, 3))
    
    try:
        # Fit and transform the expanded corpus of two documents
        tfidf_matrix = vectorizer.fit_transform([expanded_resume, expanded_job])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        return round(float(similarity * 100), 1)
        
    except Exception as e:
        return 0.0
