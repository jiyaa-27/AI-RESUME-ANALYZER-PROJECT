import streamlit as st
import os
from utils.pdf_extractor import extract_text_from_pdf
from utils.docx_extractor import extract_text_from_docx
from utils.preprocessing import preprocess_text, restore_tech_term
from utils.keyword_extraction import extract_keywords
from utils.similarity import calculate_job_fit_score
from utils.skill_matching import perform_skill_matching, generate_improvement_suggestions

# Set page configurations
st.set_page_config(
    page_title="AI Resume Analyzer & Job Fit Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium SaaS Look & Feel
st.markdown(
    """
    <style>
    /* Import modern Google font */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Header Gradient Jumbotron */
    .jumbotron {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #06b6d4 100%);
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(59, 130, 246, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .jumbotron h1 {
        font-weight: 800;
        font-size: 2.6rem !important;
        color: white !important;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .jumbotron p {
        font-weight: 300;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        opacity: 0.9;
        margin-bottom: 0;
    }
    .jumbotron-tech-pills {
        margin-top: 1rem;
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    .tech-pill {
        background: rgba(255, 255, 255, 0.15);
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Custom Section Headers */
    .section-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1e293b;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #3b82f6;
        padding-left: 10px;
    }
    
    /* Results Score Gauge styling */
    .score-card {
        background: white;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        padding: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        height: 100%;
    }
    .score-circle {
        position: relative;
        width: 170px;
        height: 170px;
        border-radius: 50%;
        background: conic-gradient(#3b82f6 var(--percent), #e2e8f0 0deg);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    }
    .score-circle::before {
        content: "";
        position: absolute;
        width: 135px;
        height: 135px;
        border-radius: 50%;
        background: white;
    }
    .score-number {
        position: absolute;
        font-size: 2.2rem;
        font-weight: 800;
        color: #1e3a8a;
    }
    .score-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1e293b;
        margin-top: 1.2rem;
        margin-bottom: 0.2rem;
    }
    
    /* Badges Containers */
    .badge-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
    .tag-badge {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid transparent;
        transition: all 0.2s ease;
    }
    .tag-matched {
        background-color: #ecfdf5;
        color: #047857;
        border-color: #a7f3d0;
    }
    .tag-matched:hover {
        background-color: #d1fae5;
    }
    .tag-missing {
        background-color: #fff1f2;
        color: #be123c;
        border-color: #fecdd3;
    }
    .tag-missing:hover {
        background-color: #ffe4e6;
    }
    .tag-general {
        background-color: #f1f5f9;
        color: #475569;
        border-color: #e2e8f0;
    }
    .tag-general:hover {
        background-color: #e2e8f0;
    }
    .tag-resume {
        background-color: #eff6ff;
        color: #1d4ed8;
        border-color: #bfdbfe;
    }
    .tag-job {
        background-color: #fffbeb;
        color: #b45309;
        border-color: #fde68a;
    }
    .tag-synonym {
        background-color: #f0fdfa;
        color: #0d9488;
        border-color: #99f6e4;
    }
    .tag-synonym:hover {
        background-color: #ccfbf1;
    }
    
    /* Suggestions Styling */
    .suggestion-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .suggestion-bullet {
        padding: 0.6rem 0.8rem;
        margin-bottom: 0.5rem;
        border-radius: 8px;
        font-size: 0.95rem;
        line-height: 1.4;
    }
    
    /* Sidebar adjustments */
    .sidebar-instructions {
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 1rem;
        line-height: 1.4;
    }
    
    /* Center text utility */
    .text-center {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header Section
st.markdown(
    """
    <div class="jumbotron">
        <h1>AI-Powered Resume Analyzer & Job Fit Assistant</h1>
        <p>Tailor your resume, discover keyword alignment, identify skill gaps, and calculate job match scores using classic NLP.</p>
        <div class="jumbotron-tech-pills">
            <span class="tech-pill">NLTK Preprocessing</span>
            <span class="tech-pill">TF-IDF Vectorization</span>
            <span class="tech-pill">Cosine Similarity</span>
            <span class="tech-pill">Set Operations</span>
            <span class="tech-pill">No LLM / Privacy-First</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Sample Data Library
SAMPLES = {
    "--- Select a Sample Job Description ---": "",
    "Python Web Developer (Django/Flask)": (
        "We are looking for a Python Web Developer to join our backend engineering team.\n"
        "Required Skills & Experience:\n"
        "- Strong programming skills in Python.\n"
        "- Experience building web applications and REST APIs using Django or Flask.\n"
        "- Excellent SQL queries optimization, PostgreSQL database schemas design.\n"
        "- Understanding of Git version control and code collaboration.\n"
        "- Familiarity with Docker containerization and AWS cloud environments.\n"
        "- Knowledge of Data Structures, Algorithms, and Software Engineering best practices."
    ),
    "Data Scientist / Machine Learning Engineer": (
        "Seeking a Data Scientist with solid experience in building machine learning models.\n"
        "Primary Qualifications:\n"
        "- Proficient in Python programming and related libraries: pandas, numpy, scikit-learn.\n"
        "- Hands-on experience with Machine Learning models (classification, regression, clustering).\n"
        "- Knowledge of Natural Language Processing (NLP) techniques, text mining, or tokenization.\n"
        "- Strong SQL databases queries skills for data extraction.\n"
        "- Experience deploying models to cloud services like AWS or GCP.\n"
        "- Solid background in statistics, data cleaning, and data visualization."
    ),
    "Frontend React Engineer": (
        "We are hiring a Frontend React Developer to build interactive and responsive user interfaces.\n"
        "Key Job Requirements:\n"
        "- Expert level HTML, CSS, JavaScript, and ES6+ standards.\n"
        "- Extensive experience with React.js, Redux state management, and React Router.\n"
        "- Modern CSS techniques, including responsive layouts, Flexbox, CSS Grid, and custom animations.\n"
        "- Consumption of RESTful API services and state synchronization.\n"
        "- Version control using Git.\n"
        "- Experience with modern build tools, Webpack, and testing libraries like Jest."
    )
}

# Sidebar - Inputs
st.sidebar.markdown("### 📤 Upload Documents")

uploaded_file = st.sidebar.file_uploader(
    "Upload Resume (PDF or DOCX)", 
    type=["pdf", "docx"], 
    help="Support PDF and DOCX files. Make sure the text is selectable."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Quick Try")
sample_job_select = st.sidebar.selectbox(
    "Choose a sample Job Description:",
    options=list(SAMPLES.keys())
)

# Display Sidebar Instructions
st.sidebar.markdown(
    """
    <div class="sidebar-instructions">
        <b>How it works:</b><br/>
        1. Upload your resume (PDF/DOCX).<br/>
        2. Enter the target Job Description.<br/>
        3. Click "Analyze Resume" to trigger the NLP pipeline.<br/>
        4. Exclude stopwords using NLTK, run TF-IDF, calculate Cosine Similarity, and map missing skills.
    </div>
    """,
    unsafe_allow_html=True
)

# Main Form Area
col_form, = st.columns(1)

with col_form:
    st.markdown('<div class="section-header">Target Job Description</div>', unsafe_allow_html=True)
    
    # Pre-populate description text area if a sample is selected
    default_jd_text = SAMPLES[sample_job_select] if sample_job_select in SAMPLES else ""
    
    job_description = st.text_area(
        "Paste the Job Description here:",
        value=default_jd_text,
        height=250,
        placeholder="We are looking for a..."
    )
    
    analyze_button = st.button("🔍 Analyze Resume", use_container_width=True, type="primary")

# Execute Analysis
if analyze_button:
    # 1. Error Handling and Validations
    if not uploaded_file:
        st.error("❌ Please upload a resume (PDF or DOCX file) to proceed.")
    elif not job_description.strip():
        st.error("❌ Please paste a job description to compare against your resume.")
    else:
        # Load and extract text based on extension
        file_name = uploaded_file.name.lower()
        resume_text = ""
        extraction_success = False
        
        with st.spinner("Extracting text from resume..."):
            try:
                if file_name.endswith('.pdf'):
                    resume_text = extract_text_from_pdf(uploaded_file)
                    extraction_success = True
                elif file_name.endswith('.docx'):
                    resume_text = extract_text_from_docx(uploaded_file)
                    extraction_success = True
                else:
                    st.error("❌ Unsupported file format. Please upload a PDF or DOCX document.")
            except ValueError as ve:
                st.error(f"❌ Extraction Error: {str(ve)}")
            except Exception as e:
                st.error(f"❌ Failed to read the uploaded file: {str(e)}")
                
        if extraction_success:
            # 2. Text Preprocessing
            with st.spinner("Preprocessing texts (cleaning, tokenizing, removing stopwords)..."):
                resume_clean = preprocess_text(resume_text)
                job_clean = preprocess_text(job_description)
                
            if not resume_clean.strip():
                st.error("❌ Insufficient text extracted from the resume. Please ensure it contains readable text (not images).")
            elif not job_clean.strip():
                st.error("❌ Preprocessing failed for the job description. Please provide a descriptive job post.")
            else:
                # 3. Calculate Job Fit Score (TF-IDF & Cosine Similarity)
                with st.spinner("Calculating similarity score..."):
                    fit_score = calculate_job_fit_score(resume_clean, job_clean)
                    
                # 4. Keyword Extraction (TF-IDF)
                with st.spinner("Extracting relevant keywords..."):
                    resume_keywords, job_keywords = extract_keywords(resume_clean, job_clean, top_n=25)
                    
                # 5. Skill Matching via Set Operations & Synonyms
                with st.spinner("Analyzing skill alignments..."):
                    matching_results = perform_skill_matching(resume_keywords, job_keywords)
                    matched_direct = matching_results["matched_direct"]
                    matched_via_synonyms = matching_results["matched_via_synonyms"]
                    missing_skills = matching_results["missing"]
                    
                # 6. Generate Rule-Based Suggestions
                suggestions = generate_improvement_suggestions(fit_score, matched_direct, matched_via_synonyms, missing_skills)
                
                # --- RENDER RESULTS DASHBOARD ---
                st.success("✅ Analysis completed successfully!")
                
                # Create beautiful tabs
                tab_dash, tab_keys, tab_texts = st.tabs([
                    "📊 Match Dashboard", 
                    "🔑 Keyword Details", 
                    "📄 Parsed Raw Data"
                ])
                
                with tab_dash:
                    # Layout inside dashboard tab
                    col_score, col_skills = st.columns([1, 2])
                    
                    with col_score:
                        # Draw custom Conic-gradient gauge indicator
                        st.markdown(
                            f"""
                            <div class="score-card">
                                <div class="score-circle" style="--percent: {fit_score}%;">
                                    <span class="score-number">{fit_score}%</span>
                                </div>
                                <div class="score-title">Job Fit Match Score</div>
                                <p style="color: #64748b; font-size: 0.9rem; margin-top: 0.2rem;">
                                    Calculated using TF-IDF & Cosine Similarity
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                    with col_skills:
                        # Matched Skills Section
                        st.markdown('<div style="font-weight: 700; color: #1e293b; margin-bottom: 0.3rem;">Matched Keywords / Skills</div>', unsafe_allow_html=True)
                        if matched_direct or matched_via_synonyms:
                            st.markdown('<div class="badge-container">', unsafe_allow_html=True)
                            
                            # Direct matches (Green)
                            direct_badges = "".join([
                                f'<span class="tag-badge tag-matched">{restore_tech_term(skill)}</span>' 
                                for skill in sorted(list(matched_direct))
                            ])
                            
                            # Synonym matches (Teal badge)
                            synonym_badges = "".join([
                                f'<span class="tag-badge tag-synonym">{restore_tech_term(job_k)} <span style="font-size:0.75rem; opacity:0.85; font-weight:400;">(via {restore_tech_term(res_k)})</span></span>'
                                for job_k, res_k in sorted(matched_via_synonyms.items())
                            ])
                            
                            st.markdown(direct_badges + synonym_badges + '</div>', unsafe_allow_html=True)
                        else:
                            st.info("No matching keywords detected. Check your resume's keyword alignment.")
                            
                        # Missing Skills Section
                        st.markdown('<div style="font-weight: 700; color: #1e293b; margin-top: 1rem; margin-bottom: 0.3rem;">Missing / Required Keywords</div>', unsafe_allow_html=True)
                        if missing_skills:
                            st.markdown('<div class="badge-container">', unsafe_allow_html=True)
                            missing_badges = "".join([
                                f'<span class="tag-badge tag-missing">{restore_tech_term(skill)}</span>' 
                                for skill in sorted(list(missing_skills))
                            ])
                            st.markdown(missing_badges + '</div>', unsafe_allow_html=True)
                        else:
                            st.success("🎉 Outstanding! No missing key skills detected relative to the job description keywords.")
                    
                    # Suggestions Section (Full Width below score and badges)
                    st.markdown('<div class="section-header">Resume Improvement Suggestions</div>', unsafe_allow_html=True)
                    if suggestions:
                        st.markdown('<div class="suggestion-box">', unsafe_allow_html=True)
                        for suggestion in suggestions:
                            # Apply alert color themes according to suggestions indicators
                            box_theme = "info"
                            if "Excellent" in suggestion or "Perfect" in suggestion or "Strong" in suggestion:
                                box_theme = "success"
                            elif "⚠️" in suggestion or "Low" in suggestion:
                                box_theme = "danger"
                            elif "📈" in suggestion or "🛠️" in suggestion or "💡" in suggestion:
                                box_theme = "warning"
                                
                            # Convert markdown inside suggestion to bold / format html manually or let streamlit do it
                            # We can render these as st.write or standard markdown with nice containers
                            theme_color = "#3b82f6" # default
                            if box_theme == "success":
                                theme_color = "#10b981"
                            elif box_theme == "danger":
                                theme_color = "#ef4444"
                            elif box_theme == "warning":
                                theme_color = "#f59e0b"
                                
                            st.markdown(
                                f"""
                                <div class="suggestion-bullet" style="border-left: 4px solid {theme_color}; background-color: white; margin-bottom: 0.6rem; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                                    {suggestion}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                with tab_keys:
                    col_res_keys, col_job_keys = st.columns(2)
                    
                    with col_res_keys:
                        st.markdown('<div style="font-weight: 700; color: #1d4ed8; margin-bottom: 0.5rem; font-size:1.1rem;">Top Resume Keywords</div>', unsafe_allow_html=True)
                        st.markdown("<p style='font-size:0.85rem; color:#64748b; margin-top:-0.4rem;'>Extracted from your resume via TF-IDF</p>", unsafe_allow_html=True)
                        if resume_keywords:
                            st.markdown('<div class="badge-container">', unsafe_allow_html=True)
                            resume_badges = "".join([
                                f'<span class="tag-badge tag-resume">{restore_tech_term(k)}</span>' 
                                for k in sorted(list(resume_keywords))
                            ])
                            st.markdown(resume_badges + '</div>', unsafe_allow_html=True)
                        else:
                            st.info("No keywords extracted.")
                            
                    with col_job_keys:
                        st.markdown('<div style="font-weight: 700; color: #b45309; margin-bottom: 0.5rem; font-size:1.1rem;">Top Job Description Keywords</div>', unsafe_allow_html=True)
                        st.markdown("<p style='font-size:0.85rem; color:#64748b; margin-top:-0.4rem;'>Extracted from job description via TF-IDF</p>", unsafe_allow_html=True)
                        if job_keywords:
                            st.markdown('<div class="badge-container">', unsafe_allow_html=True)
                            job_badges = "".join([
                                f'<span class="tag-badge tag-job">{restore_tech_term(k)}</span>' 
                                for k in sorted(list(job_keywords))
                            ])
                            st.markdown(job_badges + '</div>', unsafe_allow_html=True)
                        else:
                            st.info("No keywords extracted.")
                            
                with tab_texts:
                    col_raw_res, col_raw_job = st.columns(2)
                    
                    with col_raw_res:
                        st.subheader("Resume Extracted Text")
                        st.caption(f"Word count (original): {len(resume_text.split())} words")
                        st.text_area(
                            "Extracted raw text:", 
                            value=resume_text, 
                            height=350, 
                            key="raw_resume_display",
                            disabled=True
                        )
                        
                    with col_raw_job:
                        st.subheader("Job Description Original Text")
                        st.caption(f"Word count: {len(job_description.split())} words")
                        st.text_area(
                            "Job description raw text:", 
                            value=job_description, 
                            height=350, 
                            key="raw_job_display",
                            disabled=True
                        )
