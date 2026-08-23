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
    import os
import shutil
import re

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse

from pypdf import PdfReader
from docx import Document

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


app = FastAPI(title="AI Resume Screening System")


# Load AI model
model = SentenceTransformer("all-MiniLM-L6-v2")


# Skills database
SKILLS = [
    "python",
    "java",
    "c",
    "c++",
    "html",
    "css",
    "javascript",
    "sql",
    "mysql",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "tensorflow",
    "pytorch",
    "pandas",
    "numpy",
    "scikit-learn",
    "fastapi",
    "flask",
    "django",
    "linux",
    "windows",
    "networking",
    "ccna",
    "git",
    "github",
    "excel",
    "power bi",
    "pcb",
    "microcontroller",
    "embedded systems",
    "testing",
    "troubleshooting"
]


# -----------------------------
# HTML
# -----------------------------

def page(content=""):

    return """
<!DOCTYPE html>
<html>
<head>
    <title>AI Resume Screening System</title>

    <meta name="viewport"
          content="width=device-width, initial-scale=1">

    <style>

        body {
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            margin: 0;
            padding: 20px;
        }

        .container {
            max-width: 900px;
            margin: auto;
        }

        .header {
            background: #2563eb;
            color: white;
            padding: 25px;
            text-align: center;
            border-radius: 10px;
        }

        .card {
            background: white;
            padding: 25px;
            margin-top: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        label {
            display: block;
            font-weight: bold;
            margin-top: 15px;
            margin-bottom: 8px;
        }

        input[type=file],
        textarea {
            width: 100%;
            padding: 12px;
            box-sizing: border-box;
            border: 1px solid #ccc;
            border-radius: 6px;
        }

        textarea {
            height: 180px;
            resize: vertical;
        }

        button {
            width: 100%;
            padding: 14px;
            margin-top: 20px;
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
        }

        .scores {
            display: flex;
            gap: 15px;
            margin-top: 20px;
        }

        .score {
            flex: 1;
            background: #f1f5f9;
            padding: 20px;
            text-align: center;
            border-radius: 8px;
        }

        .score strong {
            display: block;
            font-size: 25px;
            margin-top: 8px;
        }

        .skill {
            display: inline-block;
            padding: 7px 12px;
            margin: 5px;
            border-radius: 20px;
            background: #dcfce7;
        }

        .missing {
            background: #fee2e2;
        }

        .error {
            background: #fee2e2;
            color: #991b1b;
            padding: 15px;
            border-radius: 6px;
            margin-top: 20px;
        }

        .recommendation {
            text-align: center;
            padding: 20px;
            margin-top: 20px;
            background: #eef2ff;
            border-radius: 8px;
        }

        @media(max-width: 700px) {

            .scores {
                flex-direction: column;
            }

            body {
                padding: 10px;
            }
        }

    </style>
</head>

<body>

<div class="container">

    <div class="header">
        <h1>AI Resume Screening System</h1>
        <p>Resume Analysis and Job Matching</p>
    </div>

    <div class="card">

        <form action="/screen"
              method="post"
              enctype="multipart/form-data">

            <label>Upload Resume</label>

            <input
                type="file"
                name="resume"
                accept=".pdf,.docx"
                required
            >

            <label>Job Description</label>

            <textarea
                name="job_description"
                placeholder="Enter job description..."
                required
            ></textarea>

            <button type="submit">
                Screen Resume
            </button>

        </form>

    </div>

    """ + content + """

</div>

</body>
</html>
"""


# -----------------------------
# Home
# -----------------------------

@app.get("/", response_class=HTMLResponse)
def home():

    return page()


# -----------------------------
# Extract PDF
# -----------------------------

def extract_pdf(path):

    reader = PdfReader(path)

    text = ""

    for p in reader.pages:

        extracted = p.extract_text()

        if extracted:
            text += extracted + "\n"

    return text.strip()


# -----------------------------
# Extract DOCX
# -----------------------------

def extract_docx(path):

    document = Document(path)

    text = []

    for paragraph in document.paragraphs:

        if paragraph.text.strip():

            text.append(paragraph.text)

    return "\n".join(text).strip()


# -----------------------------
# Extract Resume
# -----------------------------

def extract_resume(path):

    extension = os.path.splitext(path)[1].lower()

    if extension == ".pdf":
        return extract_pdf(path)

    if extension == ".docx":
        return extract_docx(path)

    raise ValueError(
        "Only PDF and DOCX files are supported."
    )


# -----------------------------
# Find Skills
# -----------------------------

def find_skills(text):

    text = text.lower()

    found = []

    for skill in SKILLS:

        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text):

            found.append(skill)

    return found


# -----------------------------
# Skill Matching
# -----------------------------

def skill_match(resume_text, job_text):

    resume_lower = resume_text.lower()

    job_skills = find_skills(job_text)

    found = []
    missing = []

    for skill in job_skills:

        pattern = (
            r"(?<!\w)"
            + re.escape(skill)
            + r"(?!\w)"
        )

        if re.search(pattern, resume_lower):

            found.append(skill)

        else:

            missing.append(skill)

    if len(job_skills) == 0:

        score = 0

    else:

        score = (
            len(found)
            / len(job_skills)
        ) * 100

    return round(score, 2), found, missing


# -----------------------------
# Semantic Matching
# -----------------------------

def semantic_match(resume_text, job_text):

    resume_vector = model.encode(
        [resume_text]
    )

    job_vector = model.encode(
        [job_text]
    )

    similarity = cosine_similarity(
        resume_vector,
        job_vector
    )[0][0]

    similarity = float(similarity)

    if similarity < 0:
        similarity = 0

    return round(similarity * 100, 2)


# -----------------------------
# Screen Resume
# -----------------------------

@app.post("/screen", response_class=HTMLResponse)
async def screen(

    resume: UploadFile = File(...),

    job_description: str = Form(...)
):

    temp_file = None

    try:

        if not resume.filename:

            raise ValueError(
                "Please upload a resume."
            )

        extension = os.path.splitext(
            resume.filename
        )[1].lower()

        if extension not in [".pdf", ".docx"]:

            raise ValueError(
                "Please upload PDF or DOCX only."
            )

        if not job_description.strip():

            raise ValueError(
                "Job description is required."
            )

        temp_file = "temp_resume" + extension

        with open(temp_file, "wb") as file:

            shutil.copyfileobj(
                resume.file,
                file
            )

        resume_text = extract_resume(
            temp_file
        )

        if not resume_text:

            raise ValueError(
                "Could not read text from resume."
            )

        skill_score, found, missing = skill_match(
            resume_text,
            job_description
        )

        semantic_score = semantic_match(
            resume_text,
            job_description
        )

        final_score = round(
            (skill_score * 0.5)
            +
            (semantic_score * 0.5),
            2
        )

        if final_score >= 70:

            recommendation = "SHORTLISTED"

        elif final_score >= 50:

            recommendation = "MAY BE CONSIDERED"

        else:

            recommendation = "NOT SHORTLISTED"

        found_html = ""

        for skill in found:

            found_html += (
                '<span class="skill">'
                + skill +
                '</span>'
            )

        missing_html = ""

        for skill in missing:

            missing_html += (
                '<span class="skill missing">'
                + skill +
                '</span>'
            )

        if not found_html:

            found_html = "No matching skills found."

        if not missing_html:

            missing_html = "No missing skills."

        result = f"""

        <div class="card">

            <h2>Screening Result</h2>

            <p>
                <b>Candidate:</b>
                {resume.filename}
            </p>

            <div class="scores">

                <div class="score">
                    Skill Match
                    <strong>{skill_score}%</strong>
                </div>

                <div class="score">
                    Semantic Match
                    <strong>{semantic_score}%</strong>
                </div>

                <div class="score">
                    Overall Score
                    <strong>{final_score}%</strong>
                </div>

            </div>

            <div class="recommendation">

                <h3>Recommendation</h3>

                <h2>{recommendation}</h2>

            </div>

            <h3>Matched Skills</h3>

            <div>
                {found_html}
            </div>

            <h3>Missing Skills</h3>

            <div>
                {missing_html}
            </div>

        </div>

        """

        return page(result)

    except Exception as error:

        return page(
            f"""
            <div class="error">
                <b>Error:</b> {str(error)}
            </div>
            """
        )

    finally:

        if temp_file and os.path.exists(temp_file):

            try:
                os.remove(temp_file)

            except Exception:
                pass
