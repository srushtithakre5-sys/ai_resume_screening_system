from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
import os
import re
from typing import List

app = FastAPI(title="AI Resume Screening System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

SKILLS = [
    "python", "java", "javascript", "typescript",
    "react", "angular", "vue",
    "node.js", "fastapi", "django", "flask",
    "sql", "mysql", "postgresql", "mongodb",
    "aws", "azure", "docker", "kubernetes",
    "machine learning", "deep learning",
    "artificial intelligence", "nlp",
    "tensorflow", "pytorch",
    "git", "github",
    "html", "css",
    "excel", "power bi",
]


def extract_pdf_text(file_path: str) -> str:
    try:
        reader = PdfReader(file_path)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to read PDF: {str(e)}"
        )


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text


def extract_skills(text: str) -> List[str]:
    text = normalize_text(text)

    found = []

    for skill in SKILLS:
        if skill.lower() in text:
            found.append(skill)

    return sorted(set(found))


def calculate_score(resume_text: str, job_description: str):
    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_description))

    if not job_skills:
        return {
            "score": 0,
            "matched_skills": [],
            "missing_skills": [],
        }

    matched = resume_skills.intersection(job_skills)
    missing = job_skills - resume_skills

    score = round((len(matched) / len(job_skills)) * 100, 2)

    return {
        "score": score,
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing),
    }


@app.get("/")
def home():
    return {
        "message": "AI Resume Screening API is running"
    }


@app.post("/screen")
async def screen_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF resumes are supported."
        )

    file_path = os.path.join(
        UPLOAD_DIR,
        resume.filename
    )

    try:
        content = await resume.read()

        with open(file_path, "wb") as f:
            f.write(content)

        resume_text = extract_pdf_text(file_path)

        if not resume_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from resume."
            )

        result = calculate_score(
            resume_text,
            job_description
        )

        return {
            "candidate": resume.filename,
            "score": result["score"],
            "matched_skills": result["matched_skills"],
            "missing_skills": result["missing_skills"],
            "resume_preview": resume_text[:1000]
        }

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
