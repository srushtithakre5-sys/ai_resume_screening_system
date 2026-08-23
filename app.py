from pypdf import PdfReader
from docx import Document
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import shutil
import os

# -----------------------------
# Model
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

app = FastAPI(title="AI Resume Screening System")


# -----------------------------
# PDF Extraction
# -----------------------------
def extract_pdf(path):
    reader = PdfReader(path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text.strip()


# -----------------------------
# DOCX Extraction
# -----------------------------
def extract_docx(path):
    document = Document(path)

    text = "\n".join(
        paragraph.text
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    )

    return text.strip()


# -----------------------------
# Resume Extraction
# -----------------------------
def extract_resume(path):
    extension = os.path.splitext(path)[1].lower()

    if extension == ".pdf":
        return extract_pdf(path)

    elif extension == ".docx":
        return extract_docx(path)

    else:
        raise ValueError("Only PDF and DOCX files are supported.")


# -----------------------------
# Skill Matching
# -----------------------------
def calculate_skill_match(resume_text, required_skills):
    resume_text = resume_text.lower()

    found = []
    missing = []

    for skill in required_skills:
        if skill.lower() in resume_text:
            found.append(skill)
        else:
            missing.append(skill)

    if len(required_skills) > 0:
        score = (len(found) / len(required_skills)) * 100
    else:
        score = 0

    return round(score, 2), found, missing


# -----------------------------
# Semantic Similarity
# -----------------------------
def semantic_similarity(resume_text, job_description):
    if not resume_text.strip() or not job_description.strip():
        return 0

    resume_vector = model.encode([resume_text])
    job_vector = model.encode([job_description])

    similarity = cosine_similarity(
        resume_vector,
        job_vector
    )[0][0]

    return round(float(similarity) * 100, 2)


# -----------------------------
# API Endpoint
# -----------------------------
@app.post("/screen")
async def screen_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):

    # Check file type
    if not resume.filename:
        raise HTTPException(
            status_code=400,
            detail="Resume file is required."
        )

    extension = os.path.splitext(resume.filename)[1].lower()

    if extension not in [".pdf", ".docx"]:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported."
        )

    # Check job description
    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty."
        )

    file_path = f"temp_resume{extension}"

    try:
        # Save uploaded resume
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)

        # Extract resume text
        resume_text = extract_resume(file_path)

        if not resume_text:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from the resume."
            )

        # Required skills
        job_skills = [
            "python",
            "machine learning",
            "sql",
            "tensorflow",
            "pandas"
        ]

        # Calculate skill score
        skill_score, found_skills, missing_skills = (
            calculate_skill_match(
                resume_text,
                job_skills
            )
        )

        # Calculate semantic similarity
        semantic_score = semantic_similarity(
            resume_text,
            job_description
        )

        # Final score
        final_score = round(
            (skill_score * 0.5) +
            (semantic_score * 0.5),
            2
        )

        # Result
        return {
            "candidate": resume.filename,
            "skill_score": skill_score,
            "found_skills": found_skills,
            "missing_skills": missing_skills,
            "semantic_score": semantic_score,
            "final_score": final_score
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing resume: {str(e)}"
        )

    finally:
        # Delete temporary file
        if os.path.exists(file_path):
            os.remove(file_path)


