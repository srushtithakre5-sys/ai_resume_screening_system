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

st.title("AI Resume Screening System")

uploaded_file = st.file_uploader(
    "Upload Resume",
    type=["pdf", "docx"]
)

if uploaded_file is not None:

    text = ""

    if uploaded_file.name.endswith(".pdf"):
        reader = PdfReader(uploaded_file)

        for page in reader.pages:
            text += page.extract_text() or ""

    elif uploaded_file.name.endswith(".docx"):
        document = Document(uploaded_file)

        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"

    st.success("Resume uploaded successfully!")

    st.subheader("Resume Content")

    st.write(text)
    
