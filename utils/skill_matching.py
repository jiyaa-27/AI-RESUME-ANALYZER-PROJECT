from typing import Set, List, Dict, Tuple
from utils.synonyms import check_synonym_match, find_synonyms
from utils.preprocessing import restore_tech_term

def perform_skill_matching(resume_keywords: Set[str], job_keywords: Set[str]) -> Dict:
    """
    Performs set operations on keywords with synonym mapping support.
    
    1. Direct Matches (intersection): exact overlap between resume and job keywords.
    2. Synonym Matches: job keywords that were not directly matched, but have a 
       related synonym or subfield present in the resume keywords.
    3. Missing Skills: job keywords with no direct or synonym match.
    
    Args:
        resume_keywords (Set[str]): Set of resume keywords.
        job_keywords (Set[str]): Set of job description keywords.
        
    Returns:
        Dict: A dictionary containing:
            - 'matched_direct': Set of exact matching keywords.
            - 'matched_via_synonyms': Dict of {job_keyword: resume_keyword} for related matches.
            - 'missing': Set of keywords with no matches.
    """
    # Direct intersection
    matched_direct = resume_keywords.intersection(job_keywords)
    
    # Potential gaps
    potential_missing = job_keywords.difference(resume_keywords)
    
    matched_via_synonyms = {}
    missing_skills = set()
    
    # Check for synonym/subfield matches
    for job_term in potential_missing:
        matched_res_term = check_synonym_match(job_term, resume_keywords)
        if matched_res_term:
            matched_via_synonyms[job_term] = matched_res_term
        else:
            missing_skills.add(job_term)
            
    return {
        "matched_direct": matched_direct,
        "matched_via_synonyms": matched_via_synonyms,
        "missing": missing_skills
    }

def generate_improvement_suggestions(
    fit_score: float, 
    matched_direct: Set[str], 
    matched_via_synonyms: Dict[str, str], 
    missing: Set[str]
) -> List[str]:
    """
    Generates rule-based resume improvement recommendations dynamically based on exact
    matches, synonym matches, and gaps.
    
    Args:
        fit_score (float): Calculated job fit percentage score.
        matched_direct (Set[str]): Set of exact matching keywords.
        matched_via_synonyms (Dict[str, str]): Map of job keyword -> matched resume synonym.
        missing (Set[str]): Set of missing job keywords.
        
    Returns:
        List[str]: List of actionable suggestions.
    """
    suggestions = []
    
    # 1. Similarity Level Suggestion
    if fit_score >= 80:
        suggestions.append(
            "🌟 **Strong Alignment**: Your resume is highly optimized for this job description. "
            "Ensure that you can speak confidently to all the matched skills in interviews."
        )
    elif 50 <= fit_score < 80:
        suggestions.append(
            "📈 **Moderate Alignment**: Your resume matches the job description reasonably well, "
            "but there are significant gaps. Tailoring your terminology will boost your profile."
        )
    else:
        suggestions.append(
            "⚠️ **Low Keyword Alignment**: Your resume has low alignment with this job description. "
            "It is highly recommended to revise your resume to include the missing core requirements before applying."
        )
        
    # 2. Skill Density Analysis
    total_matches = len(matched_direct) + len(matched_via_synonyms)
    if len(missing) == 0 and total_matches > 0:
        suggestions.append(
            "🎯 **Excellent Skill Coverage**: You have addressed all key skills extracted from the job description!"
        )
    elif len(missing) > 0:
        suggestions.append(
            f"🛠️ **Skills Gap**: The analyzer detected **{len(missing)}** key required keyword(s)/skill(s) missing from your resume. "
            f"Evaluate if you have experience with these concepts, and if so, explicitly add them."
        )
        
    # 3. Synonym-specific Optimization Suggestion
    if matched_via_synonyms:
        suggestions.append(
            "🔄 **Keyword Phrasing Optimization**: We found related experience on your resume for some keywords, "
            "but not the exact terms the job description uses. For automated ATS screening, consider swapping "
            "or adding the exact terms: "
        )
        # Highlight top 3 synonym matches
        syn_tips = []
        for job_k, res_k in list(matched_via_synonyms.items())[:3]:
            syn_tips.append(f"Add exact term `{restore_tech_term(job_k)}` (currently mentions `{restore_tech_term(res_k)}`)")
        
        suggestions[-1] += " " + " | ".join(syn_tips)

    # 4. Actionable Tailoring Tips (highlighting top missing items)
    if missing:
        # Sort to keep suggestions deterministic
        sorted_missing = sorted(list(missing))
        highlighted_missing = [f"`{restore_tech_term(m)}`" for m in sorted_missing[:4]]
        
        suggestions.append(
            f"💡 **Action Item**: Try integrating high-priority missing terms like {', '.join(highlighted_missing)} "
            "directly into your resume (e.g. in your Skills section or Work Experience bullets)."
        )
        
    # 5. Structural Suggestion
    suggestions.append(
        "📋 **Formatting Advice**: Organize your technical competencies into a designated 'Skills' section "
        "using clean bullet points so parsers can scan them efficiently."
    )
    
    return suggestions
