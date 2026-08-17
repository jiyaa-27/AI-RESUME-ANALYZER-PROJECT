import re
import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Thread-safe loading/downloading of NLTK resources
def download_nltk_resources():
    resources = ['punkt', 'stopwords']
    for resource in resources:
        try:
            # Check if resource is already downloaded
            if resource == 'punkt':
                nltk.data.find('tokenizers/punkt')
            elif resource == 'stopwords':
                nltk.data.find('corpora/stopwords')
        except LookupError:
            try:
                nltk.download(resource, quiet=True)
            except Exception as e:
                print(f"Warning: Failed to download NLTK resource '{resource}': {e}")

# Run NLTK downloader
download_nltk_resources()

# Dictionary to map special tech terms to safe alphanumeric representations
TECH_MAP_PRESERVE = {
    # C++
    r'\b[cC]\+\+(?=\s|[.,;!?()\{\}\[\]\-\/]|$)' : 'cplusplus',
    # C#
    r'\b[cC]#(?=\s|[.,;!?()\{\}\[\]\-\/]|$)' : 'csharp',
    # .NET
    r'(?<!\S)\.[nN][eE][tT]\b' : 'dotnet',
    # Node.js
    r'\b[nN][oO][dD][eE]\.[jJ][sS]\b' : 'nodejs',
    # React.js
    r'\b[rR][eE][aA][cC][tT]\.[jJ][sS]\b' : 'reactjs',
    # Vue.js
    r'\b[vV][uU][eE]\.[jJ][sS]\b' : 'vuejs',
}

# Reverse mapping for displaying skills nicely on the dashboard
TECH_MAP_RESTORE = {
    'cplusplus': 'C++',
    'csharp': 'C#',
    'dotnet': '.NET',
    'nodejs': 'Node.js',
    'reactjs': 'React.js',
    'vuejs': 'Vue.js'
}

def preserve_tech_terms(text: str) -> str:
    """Replaces tricky programming symbols with alphanumeric placeholders before tokenization."""
    if not text:
        return ""
    for pattern, placeholder in TECH_MAP_PRESERVE.items():
        text = re.sub(pattern, placeholder, text)
    return text

def restore_tech_term(term: str) -> str:
    """Restores the placeholder back to its readable format (e.g. cplusplus -> C++)."""
    term_lower = term.lower().strip()
    if term_lower in TECH_MAP_RESTORE:
        return TECH_MAP_RESTORE[term_lower]
    # Capitalize first letter of each word for standard words
    return " ".join([word.capitalize() for word in term_lower.split()])

def preprocess_text(text: str) -> str:
    """
    Cleans and preprocesses the input text:
    1. Replaces special language signatures (C++, C#, .NET, etc.) with safe placeholders.
    2. Converts all text to lowercase.
    3. Tokenizes the text using NLTK word_tokenize.
    4. Removes punctuation, stopwords, and single-letter characters.
    5. Joins the preprocessed tokens back into a space-separated string.
    """
    if not text:
        return ""
    
    # 1. Preserve special tech terms
    processed_text = preserve_tech_terms(text)
    
    # 2. Downcase
    processed_text = processed_text.lower()
    
    # 3. Tokenize
    try:
        tokens = word_tokenize(processed_text)
    except Exception:
        # Fallback regex word tokenization if NLTK fails
        tokens = re.findall(r'\b\w+\b', processed_text)
        
    # 4. Filter stop words
    try:
        stop_words = set(stopwords.words('english'))
    except Exception:
        # Stand-in fallback list if NLTK files aren't loading
        stop_words = {
            "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", 
            "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", 
            "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", 
            "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", 
            "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", 
            "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", 
            "with", "about", "against", "between", "into", "through", "during", "before", "after", 
            "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", 
            "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", 
            "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", 
            "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", 
            "should", "now"
        }
        
    cleaned_tokens = []
    for token in tokens:
        # Strip leading/trailing punctuation (like parentheses, commas, dots)
        cleaned_token = token.strip(string.punctuation)
        
        # Avoid empty tokens and stopwords
        if cleaned_token and cleaned_token not in stop_words:
            # Remove single-letter tokens except for known languages like 'c', 'r'
            if len(cleaned_token) == 1 and cleaned_token not in ('c', 'r'):
                continue
            cleaned_tokens.append(cleaned_token)
            
    return " ".join(cleaned_tokens)
