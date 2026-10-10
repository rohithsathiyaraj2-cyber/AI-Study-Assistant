
import re
import random
import streamlit as st
from pypdf import PdfReader

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📚",
    layout="wide"
)

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

uploaded_file = st.file_uploader(
    "📄 Upload your study PDF",
    type=["pdf"],
    key="study_pdf"
)

text = ""

if uploaded_file:
    try:
        reader = PdfReader(uploaded_file)
        text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

        st.success(
            f"PDF loaded! Total pages: {len(reader.pages)}"
        )

        if not text.strip():
            st.warning(
                "No selectable text found. "
                "Scanned PDFs need OCR."
            )

    except Exception:
        st.error("Unable to read this PDF.")
        text = ""


def get_sentences(content):
    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", content)
        if len(sentence.split()) >= 5
    ]


def get_keywords(sentence):
    words = re.findall(r"\b[a-zA-Z]{3,}\b", sentence.lower())
    common = {
        "the", "and", "for", "are", "was", "were",
        "that", "this", "with", "from", "have", "has",
        "into", "their", "they", "which", "will", "can",
        "not", "but", "its", "also", "than", "then"
    }
    return set(words) - common


if tool == "Study Notes":
    st.subheader("📘 Study Notes")

    if text.strip():
        st.text_area(
            "Extracted PDF Text",
            text,
            height=300
        )

        if st.button("Generate Quick Summary"):
            sentences = get_sentences(text)
            summary = " ".join(sentences[:5])

            st.subheader("Quick Summary")

            if summary:
                st.write(summary)
            else:
                st.info("Not enough text to summarize.")

    else:
        st.info("Upload a PDF to read your study notes.")


elif tool == "Ask Questions":
    st.subheader("💬 Ask Questions")
    st.write("Ask something about your uploaded PDF.")

    question = st.text_input(
        "Enter your question",
        key="study_question"
    )

    if st.button("Find Answer"):
        if not text.strip():
            st.warning("Please upload a text-based PDF first.")

        elif not question.strip():
            st.warning("Please enter a question.")

        else:
            question_words = get_keywords(question)
            sentences = get_sentences(text)

            ranked = []

            for sentence in sentences:
                sentence_words = get_keywords(sentence)

                if question_words:
                    overlap = question_words & sentence_words
                    score = len(overlap) / len(question_words)

                    if overlap:
                        ranked.append((score, sentence))

            ranked.sort(key=lambda item: item[0], reverse=True)

            if ranked:
                st.subheader("📖 Relevant Answer")

                for score, sentence in ranked[:3]:
                    st.write("•", sentence)

                st.caption(
                    "Answers are matched from your PDF text. "
                    "Verify the context in your notes."
                )
            else:
                st.info(
                    "No close keyword match found. "
                    "Try using words from your PDF."
                )


elif tool == "Generate Quiz":
    st.subheader("🧠 Generate Quiz")
    st.write("Create a practice quiz from your PDF.")

    num_questions = st.slider(
        "Number of questions",
        min_value=3,
        max_value=10,
        value=5
    )

    if st.button("Generate Quiz"):
        if not text.strip():
            st.warning("Please upload a text-based PDF first.")

        else:
            sentences = get_sentences(text)
            candidates = []

            for sentence in sentences:
                words = re.findall(r"\b[A-Za-z]{5,}\b", sentence)
                unique_words = list(dict.fromkeys(words))

                if len(unique_words) >= 2:
                    candidates.append((sentence, unique_words))

            if len(candidates) < 3:
                st.warning(
                    "Not enough suitable text. "
                    "Try a longer PDF."
                )

            else:
                random.shuffle(candidates)
                vocabulary = list({
                    word.lower()
                    for _, words in candidates
                    for word in words
                })

                quiz = []

                for sentence, words in candidates:
                    answer = random.choice(words)

                    distractors = [
                        word for word in vocabulary
                        if word.lower() != answer.lower()
                    ]

                    if len(distractors) < 3:
                        continue

                    options = random.sample(distractors, 3)
                    options.append(answer)
                    random.shuffle(options)

                    pattern = re.compile(
                        r"\b" + re.escape(answer) + r"\b",
                        re.IGNORECASE
                    )

                    question_text = pattern.sub(
                        "________",
                        sentence,
                        count=1
                    )

                    quiz.append({
                        "question": question_text,
                        "options": options,
                        "answer": answer
                    })

                    if len(quiz) >= num_questions:
                        break

                if len(quiz) < 3:
                    st.warning(
                        "Could not create enough questions "
                        "from this PDF."
                    )
                else:
                    st.session_state["study_quiz"] = quiz
                    st.session_state.pop("study_quiz_result", None)

    quiz = st.session_state.get("study_quiz", [])

    if quiz:
        with st.form("quiz_form"):
            answers = []

            for i, item in enumerate(quiz):
                st.markdown(
                    f"**Q{i + 1}. {item['question']}**"
                )

                selected = st.radio(
                    "Choose your answer:",
                    item["options"],
                    index=None,
                    key=f"quiz_answer_{i}"
                )

                answers.append(selected)

            submitted = st.form_submit_button("Submit Quiz")

        if submitted:
            score = sum(
                selected == item["answer"]
                for selected, item in zip(answers, quiz)
            )

            st.session_state["study_quiz_result"] = (
                score, len(quiz), answers
            )

        result = st.session_state.get("study_quiz_result")

        if result:
            score, total, answers = result

            st.subheader("🏆 Your Result")
            st.metric("Score", f"{score} / {total}")

            for i, item in enumerate(quiz):
                st.write(f"**Q{i + 1}.** {item['question']}")
                st.write(f"Correct answer: {item['answer']}")

                if answers[i] == item["answer"]:
                    st.success("Correct!")
                else:
                    st.error("Incorrect or unanswered.")
