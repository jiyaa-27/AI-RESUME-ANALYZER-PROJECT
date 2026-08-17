from typing import Set, Optional

# Define cohesive taxonomy groups of synonyms, subfields, and related tech concepts.
# Note: Placeholders (cplusplus, csharp, dotnet, nodejs, reactjs, vuejs) are used here 
# because preprocessing converts the raw terms to these forms.
SYNONYM_GROUPS = [
    # Data Science & Machine Learning
    {
        "machine learning", "ml", "deep learning", "dl", "neural networks", 
        "artificial intelligence", "ai", "computer vision", "cv", "nlp", 
        "natural language processing", "supervised learning", "unsupervised learning", 
        "reinforcement learning", "data science", "data analysis", "statistics",
        "scikit-learn", "sklearn", "tensorflow", "pytorch", "keras"
    },
    # Cloud - AWS
    {
        "amazon web services", "aws", "s3", "ec2", "rds", "lambda", "cloud", 
        "cloud computing", "gcp", "azure"
    },
    # Databases & SQL
    {
        "sql", "database", "databases", "mysql", "postgresql", "oracle", 
        "sqlite", "sql server", "rdbms", "relational database"
    },
    # NoSQL
    {
        "nosql", "mongodb", "cassandra", "redis", "dynamodb", "document store"
    },
    # Python ecosystem
    {
        "python", "django", "flask", "fastapi", "numpy", "pandas", "scipy", 
        "scikit-learn", "sklearn", "pytorch", "tensorflow"
    },
    # Web Development - Frontend & JS
    {
        "javascript", "js", "typescript", "ts", "nodejs", "node", "reactjs", 
        "react", "angular", "vuejs", "vue", "nextjs", "expressjs", "frontend", 
        "web development", "web design"
    },
    # HTML/CSS Styling
    {
        "html", "css", "html5", "css3", "sass", "bootstrap", "tailwind", "styling"
    },
    # Version Control
    {
        "git", "github", "gitlab", "bitbucket", "version control"
    },
    # DevOps & Containerization
    {
        "docker", "kubernetes", "k8s", "containerization", "containers", 
        "devops", "ci/cd", "jenkins", "github actions"
    },
    # Data Structures & Core CS
    {
        "data structure", "data structures", "algorithm", "algorithms", "dsa", 
        "problem solving", "oop", "object oriented programming"
    },
    # Agile & Project Management
    {
        "agile", "scrum", "kanban", "jira", "project management"
    },
    # Java Ecosystem
    {
        "java", "spring", "spring boot", "springboot", "hibernate"
    },
    # C# & C++ Systems
    {
        "cplusplus", "csharp", "dotnet", "c", "backend", "software engineering"
    }
]

def find_synonyms(term: str) -> Set[str]:
    """
    Returns a set of synonyms and related subfields for a given term.
    
    Args:
        term (str): Preprocessed term.
        
    Returns:
        Set[str]: Set of related terms, excluding the term itself.
    """
    term_lower = term.lower().strip()
    synonyms = set()
    for group in SYNONYM_GROUPS:
        if term_lower in group:
            synonyms.update(group)
    synonyms.discard(term_lower)
    return synonyms

def check_synonym_match(job_term: str, resume_terms: Set[str]) -> Optional[str]:
    """
    Checks if any synonym or subfield of a job requirement is present in the candidate's resume keywords.
    
    Args:
        job_term (str): The keyword required by the job description.
        resume_terms (Set[str]): Keywords present in the resume.
        
    Returns:
        Optional[str]: The matching synonym found in the resume, or None if no match.
    """
    job_term_lower = job_term.lower().strip()
    
    # If the exact term is in the resume, it's an exact match, not a synonym match
    if job_term_lower in resume_terms:
        return None
        
    # Get all synonyms
    synonyms = find_synonyms(job_term_lower)
    
    # Check if any synonym exists in the resume terms
    for syn in synonyms:
        if syn in resume_terms:
            return syn
            
    return None
