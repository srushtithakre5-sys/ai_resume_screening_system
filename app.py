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
from flask import Flask, request, render_template_string
import PyPDF2

app = Flask(__name__)

skills = [
    "python", "java", "c++", "html", "css",
    "javascript", "sql", "linux", "windows",
    "networking", "ccna", "excel"
]

HTML = """
<h1>AI Resume Screening System</h1>

<form method="POST" enctype="multipart/form-data">
    <input type="file" name="resume" required><br><br>

    <textarea name="job" rows="6"
    placeholder="Enter job description" required></textarea><br><br>

    <button type="submit">Screen Resume</button>
</form>

{% if result %}
<h2>Result</h2>
<p>Match Score: {{ score }}%</p>
<p>Matched Skills: {{ matched }}</p>
<p>Missing Skills: {{ missing }}</p>
{% endif %}
"""

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        resume = request.files["resume"]
        job = request.form["job"].lower()

        reader = PyPDF2.PdfReader(resume)

        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        text = text.lower()

        required = [skill for skill in skills if skill in job]

        matched = [skill for skill in required if skill in text]

        missing = [skill for skill in required if skill not in text]

        score = 0

        if required:
            score = round(len(matched) / len(required) * 100)

        return render_template_string(
            HTML,
            result=True,
            score=score,
            matched=matched,
            missing=missing
        )

    return render_template_string(HTML)


if __name__ == "__main__":
    app.run(debug=True)
