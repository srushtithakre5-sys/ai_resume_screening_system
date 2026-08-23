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
# PDF TEXT
    if uploaded_file.name.endswith(".pdf"):

        reader = PdfReader(uploaded_file)

        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        st.subheader("📄 Resume Text")
        st.write(text)

        # SKILLS
        skills = [
            "python",
            "java",
            "html",
            "css",
            "javascript",
            "sql",
            "mysql",
            "linux",
            "windows",
            "ccna",
            "networking",
            "flask",
            "excel"
        ]

        found_skills = []

        for skill in skills:
            if skill in text.lower():
                found_skills.append(skill)

        st.subheader("🛠️ Skills Detected")

        if found_skills:
            for skill in found_skills:
                st.write("✅", skill.title())
        else:
            st.warning("No skills detected.")

else:

    st.warning("Please upload your resume.")
