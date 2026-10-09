
import streamlit as st
from pypdf import PdfReader

st.set_page_config(page_title="AI Study Assistant", page_icon="📚")

st.title("📚 AI Study Assistant")
st.write("Your personal study companion!")

name = st.text_input("Enter your name")
if name:
    st.success(f"Welcome, {name}!")

st.sidebar.title("Study Tools")
tool = st.sidebar.radio(
    "Choose a tool",
    ["Study Notes", "Ask Questions", "Generate Quiz"]
)

if tool == "Study Notes":
    st.subheader("📄 Upload Your PDF Notes")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"]
    )

    if uploaded_file is not None:
        try:
            reader = PdfReader(uploaded_file)
            pages = [
                page.extract_text() or ""
                for page in reader.pages
            ]
            text = "\n".join(pages)

            st.success("PDF uploaded successfully!")
            st.write("Total pages:", len(reader.pages))

            if text.strip():
                st.text_area(
                    "Extracted Notes",
                    text,
                    height=300
                )

                if st.button("Generate Quick Summary"):
                    paragraphs = [
                        line.strip()
                        for line in text.splitlines()
                        if line.strip()
                    ]
                    summary = "\n".join(paragraphs[:5])
                    st.subheader("📘 Quick Summary")
                    st.write(summary)
            else:
                st.warning(
                    "No selectable text found. "
                    "This may be a scanned PDF."
                )

        except Exception as error:
            st.error("Unable to read this PDF.")
            st.caption(str(error))

elif tool == "Ask Questions":
    st.subheader("💬 Ask Questions")
    st.info("AI-powered answers will be added next!")

elif tool == "Generate Quiz":
    st.subheader("🧠 Generate Quiz")
    st.info("Automatic quiz generation will be added next!")