import streamlit as st
import random

st.title("AI Resume Screening System")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

if uploaded_file is not None:
    score = random.randint(50, 100)

    st.success(f"Uploaded: {uploaded_file.name}")
    st.write("Resume Score: 85%")
    st.write(f"Resume Score: {score}%")

    if score >= 85:
        st.success("✅ Good Resume")
    elif score >= 70:
        st.warning("🟡 Average Resume")
    else:
        st.error("❌ Poor Resume")
else:
     st.warning("Please upload your resume.")
import streamlit as st
from pypdf import PdfReader
from docx import Document
import re
# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="AI Resume Screening System",
    page_icon="📄",
    layout="wide"
)
st.title("🤖 AI Resume Screening System")
st.write("Upload your resume and get a detailed resume analysis.")
# -----------------------------
# EXTRACT TEXT FROM PDF
# -----------------------------
def extract_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text
# -----------------------------
# EXTRACT TEXT FROM DOCX
# -----------------------------
def extract_docx(uploaded_file):
    document = Document(uploaded_file)
    return "\n".join(paragraph.text for paragraph in document.paragraphs)
# -----------------------------
# EXTRACT RESUME TEXT
# -----------------------------
def extract_resume(uploaded_file):
    if uploaded_file.name.lower().endswith(".pdf"):
        return extract_pdf(uploaded_file)
    if uploaded_file.name.lower().endswith(".docx"):
        return extract_docx(uploaded_file)
    return ""
# -----------------------------
# CONTACT CHECKS
# -----------------------------
def check_email(text):
    return bool(re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text))
def check_phone(text):
    return bool(re.search(r"(\+91[\s-]?)?[6-9]\d{9}", text))
def check_linkedin(text):
    return "linkedin.com" in text.lower()
def check_github(text):
    return "github.com" in text.lower()
# -----------------------------
# SECTION CHECK
# -----------------------------
def check_section(text, keywords):
    text = text.lower()
    return any(keyword in text for keyword in keywords)
# -----------------------------
# SKILLS DATABASE
# -----------------------------
SKILLS = [
    "python","java","c++","c","sql","mysql","postgresql","mongodb",
    "machine learning","deep learning","data science","data analysis",
    "artificial intelligence","numpy","pandas","tensorflow","pytorch",
    "scikit-learn","fastapi","flask","django","html","css","javascript",
    "react","node.js","docker","aws","azure","git","github","power bi",
    "tableau","excel"
]
def find_skills(text):
    text = text.lower()
    return [skill for skill in SKILLS if skill in text]
# -----------------------------
# JOB DESCRIPTION MATCH
# -----------------------------
def analyse_job_match(resume_text, job_description):
    resume_skills = find_skills(resume_text)
    job_skills = find_skills(job_description)
    matched = [s for s in job_skills if s in resume_skills]
    missing = [s for s in job_skills if s not in resume_skills]
    score = round(len(matched) / len(job_skills) * 100, 2) if job_skills else 0
    return score, matched, missing
# -----------------------------
# RESUME ANALYSIS
# -----------------------------
def analyse_resume(text):
    text_lower = text.lower()
    score, results, suggestions = 0, {}, []
    # Contact details
    results["Email"] = check_email(text); score += 5 if results["Email"] else suggestions.append("Add a professional email address.")
    results["Phone"] = check_phone(text); score += 5 if results["Phone"] else suggestions.append("Add a valid phone number.")
    results["LinkedIn"] = check_linkedin(text); score += 5 if results["LinkedIn"] else suggestions.append("Add your LinkedIn profile URL.")
    results["GitHub"] = check_github(text); score += 5 if results["GitHub"] else suggestions.append("Add your GitHub profile if you have technical projects.")
    # Sections
    results["Professional Summary"] = check_section(text_lower, ["summary","professional summary","profile","objective"])
    score += 10 if results["Professional Summary"] else suggestions.append("Add a professional summary or career objective.")
    results["Education"] = check_section(text_lower, ["education","university","college","bachelor","master"])
    score += 10 if results["Education"] else suggestions.append("Add your education details.")
    results["Experience"] = check_section(text_lower, ["experience","work experience","internship","employment"])
    score += 15 if results["Experience"] else suggestions.append("Add internship or work experience.")
    results["Projects"] = check_section(text_lower, ["project","projects","academic project"])
    score += 15 if results["Projects"] else suggestions.append("Add relevant projects with technologies and outcomes.")
     # Skill
    detected_skills = find_skills(text)
    results["Skills"] = detected_skills
    if len(detected_skills) >= 8: score += 15
    elif len(detected_skills) >= 4: score += 10
    elif len(detected_skills) > 0: score += 5
    else: suggestions.append("Add a dedicated technical skills section.")
    # Certifications
    results["Certifications"] = check_section(text_lower, ["certification","certifications","certificate"])
    score += 5 if results["Certifications"] else suggestions.append("Add relevant certifications if available.")
    # Word count
    word_count = len(text.split())
    results["Word Count"] = word_count
    if 300 <= word_count <= 1200: score += 10
    elif word_count < 300: suggestions.append("Your resume may be too short. Add more relevant details.")
    else: suggestions.append("Your resume may be too long. Keep it concise.")
    # Action words
    action_words = ["developed","created","designed","implemented","improved","managed","built","analysed","analyzed","led"]
    action_count = sum(1 for w in action_words if w in text_lower)
    results["Action Words"] = action_count
    if action_count >= 3:
    score += 5
else:
    suggestions.append("Use stronger action words such as Developed, Built, Implemented, Managed, etc.")
return min(score, 100), results, suggestions
def get_status(score):
    if score >= 80: return "EXCELLENT"
    elif score >= 65: return "GOOD"
    elif return"NEEDS IMPROVEMENT"
