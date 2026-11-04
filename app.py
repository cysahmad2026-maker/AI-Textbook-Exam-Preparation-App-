
import json
import os
import re
import io

import streamlit as st
from pypdf import PdfReader
from docx import Document
from google import genai
from google.genai import types


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Pakistan AI Exam Preparation",
    page_icon="📚",
    layout="wide"
)


# =========================================================
# CUSTOM UI
# =========================================================

st.markdown("""
<style>
    .main {
        background-color: #f8fafc;
    }

    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
    }

    .hero {
        background: linear-gradient(135deg, #0f766e, #115e59);
        padding: 28px;
        border-radius: 18px;
        color: white;
        margin-bottom: 25px;
    }

    .hero h1 {
        color: white;
        font-size: 32px;
    }

    .hero p {
        color: #d1fae5;
        font-size: 16px;
    }

    .question-card {
        background: white;
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        margin-bottom: 15px;
    }

    div[data-testid="stMetric"] {
        background: white;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }

    .footer {
        text-align: center;
        color: #64748b;
        padding: 25px;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# APPLICATION HEADER
# =========================================================

st.markdown("""
<div class="hero">
    <h1>📚 Pakistan AI Exam Preparation</h1>
    <p>
        Upload your textbook chapter, practice exam questions,
        check your answers, and improve your preparation.
    </p>
    <p>
        Matric 9th–10th | Intermediate 11th–12th
    </p>
</div>
""", unsafe_allow_html=True)


# =========================================================
# API CONFIGURATION
# =========================================================

def get_api_key():
    """
    Read Gemini API key from Streamlit secrets
    or environment variables.
    """

    try:
        secret_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        secret_key = ""

    return secret_key or os.getenv("GEMINI_API_KEY", "")


def get_gemini_client():
    api_key = get_api_key()

    if not api_key:
        return None

    return genai.Client(api_key=api_key)


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "chapter_text": "",
    "chapter_name": "",
    "questions": [],
    "answers": {},
    "results": {},
    "checked": False,
    "question_count": 10,
    "question_type": "Mixed",
    "language": "English",
    "class_level": "9th",
    "subject": "",
    "board": "Not specified",
    "chapter_title": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# TEXT EXTRACTION
# =========================================================

def extract_pdf(file_bytes):
    """
    Extract text from a text-based PDF.
    """

    reader = PdfReader(io.BytesIO(file_bytes))

    pages = []

    for page in reader.pages:
        page_text = page.extract_text() or ""

        if page_text.strip():
            pages.append(page_text)

    return "\n\n".join(pages)


def extract_txt(file_bytes):
    """
    Extract text from TXT files.
    """

    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return file_bytes.decode("utf-8", errors="replace")


def extract_docx(file_bytes):
    """
    Extract paragraphs and tables from DOCX.
    """

    document = Document(io.BytesIO(file_bytes))

    paragraphs = [
        paragraph.text
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    table_content = []

    for table in document.tables:
        for row in table.rows:
            cells = [
                cell.text.strip()
                for cell in row.cells
            ]

            table_content.append(" | ".join(cells))

    return "\n".join(paragraphs + table_content)


def extract_chapter(uploaded_file):
    """
    Detect file extension and extract chapter text.
    """

    file_bytes = uploaded_file.getvalue()

    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):
        return extract_pdf(file_bytes)

    elif filename.endswith(".txt"):
        return extract_txt(file_bytes)

    elif filename.endswith(".docx"):
        return extract_docx(file_bytes)

    else:
        raise ValueError(
            "Unsupported file. Upload PDF, TXT, or DOCX."
        )


# =========================================================
# GEMINI RESPONSE HELPERS
# =========================================================

def clean_json_response(response_text):
    """
    Remove Markdown code fences if Gemini returns them.
    """

    text = response_text.strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    return text.strip()


def generate_ai_response(prompt):
    """
    Send a prompt to Gemini and return its response.
    """

    client = get_gemini_client()

    if client is None:
        raise ValueError(
            "Gemini API key is missing. "
            "Add GEMINI_API_KEY to Streamlit secrets."
        )

    model = os.getenv(
        "GEMINI_MODEL",
        "gemini-2.5-flash"
    )

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=8192
        )
    )

    if not response.text:
        raise ValueError(
            "Gemini returned an empty response. Try again."
        )

    return response.text


# =========================================================
# QUESTION GENERATION
# =========================================================

def generate_questions(
    chapter_text,
    class_level,
    subject,
    board,
    chapter_title,
    question_count,
    question_type,
    language
):
    """
    Generate questions using ONLY the uploaded chapter.
    """

    prompt = f"""
You are an experienced Pakistani board examination teacher.

Your task is to prepare a practice test for a student
using the student's uploaded textbook chapter.

STUDENT INFORMATION:

Class: {class_level}
Subject: {subject}
Board: {board}
Chapter: {chapter_title}
Question count: {question_count}
Question type: {question_type}
Explanation language: {language}

IMPORTANT RULES:

1. Use the uploaded chapter as the primary and exclusive
   source for factual questions and their answers.

2. Do not invent textbook facts, page numbers, formulas,
   quotations, definitions, or chapter-specific information.

3. If the chapter does not contain enough information,
   generate fewer questions rather than inventing facts.

4. Questions should be appropriate for Pakistani Matric
   or Intermediate students.

5. Use simple, clear language suitable for the selected class.

6. Make questions educational and exam-oriented.

7. Do not reveal answers inside the question text.

8. For MCQs, provide exactly four options.

9. The correct answer must be supported by the chapter.

10. Do not generate questions about content absent
    from the uploaded chapter.

QUESTION TYPES:

If the selected type is MCQ:
Generate multiple-choice questions only.

If the selected type is Short Questions:
Generate short-answer questions.

If the selected type is Long Questions:
Generate descriptive questions.

If the selected type is Mixed:
Generate a useful combination of MCQs and short questions.
Include long questions only when requested separately.

LANGUAGE:

Question language: English.

Explanation language: {language}

Return ONLY valid JSON.

JSON FORMAT:

{{
    "questions": [
        {{
            "id": 1,
            "type": "MCQ",
            "question": "Question text",
            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ],
            "answer": "Exact correct option",
            "explanation": "Explanation in {language}",
            "chapter_evidence": "Relevant textbook evidence"
        }},
        {{
            "id": 2,
            "type": "Short Question",
            "question": "Question text",
            "options": [],
            "answer": "Expected answer",
            "explanation": "Explanation in {language}",
            "chapter_evidence": "Relevant textbook evidence"
        }}
    ]
}}

For MCQs, answer must exactly match one of the options.

For short and long questions, provide a model answer
grounded in the chapter.

Keep the requested number of questions when possible.

UPLOADED TEXTBOOK CHAPTER:

<chapter>
{chapter_text}
</chapter>
"""

    response = generate_ai_response(prompt)

    cleaned_response = clean_json_response(response)

    data = json.loads(cleaned_response)

    questions = data.get("questions", [])

    if not isinstance(questions, list):
        raise ValueError(
            "AI response has an invalid question format."
        )

    valid_questions = []

    for question in questions:

        if not isinstance(question, dict):
            continue

        question_text = str(
            question.get("question", "")
        ).strip()

        answer = str(
            question.get("answer", "")
        ).strip()

        if not question_text or not answer:
            continue

        q_type = str(
            question.get("type", "Short Question")
        )

        options = question.get("options", [])

        if not isinstance(options, list):
            options = []

        options = [
            str(option)
            for option in options
        ]

        if q_type.lower() == "mcq":

            if len(options) != 4:
                continue

            if answer not in options:
                continue

        valid_questions.append({
            "id": len(valid_questions) + 1,
            "type": q_type,
            "question": question_text,
            "options": options,
            "answer": answer,
            "explanation": str(
                question.get("explanation", "")
            ),
            "chapter_evidence": str(
                question.get("chapter_evidence", "")
            )
        })

    if not valid_questions:
        raise ValueError(
            "No valid questions were generated. "
            "Try another chapter or question type."
        )

    return valid_questions


# =========================================================
# ANSWER EVALUATION
# =========================================================

def evaluate_answer(
    chapter_text,
    question,
    student_answer,
    language
):
    """
    Evaluate the student's answer against chapter content.

    Gemini should not mark an answer incorrect merely
    because the student used different wording.
    """

    prompt = f"""
You are a fair Pakistani board examination teacher.

Evaluate a student's answer using the uploaded
textbook chapter as the primary source.

QUESTION:

{question["question"]}

EXPECTED ANSWER:

{question["answer"]}

STUDENT ANSWER:

{student_answer}

TEXTBOOK CHAPTER:

<chapter>
{chapter_text}
</chapter>

LANGUAGE:

{language}

EVALUATION RULES:

1. Compare the student's meaning with the expected answer.

2. Accept correct answers written in different words.

3. Accept relevant correct information supported
   by the chapter.

4. Do not mark a correct answer wrong merely because
   its grammar, spelling, or wording differs.

5. Identify missing important points.

6. Identify incorrect statements.

7. For MCQs, determine whether the selected answer
   matches the correct option.

8. Do not invent textbook evidence.

9. If the chapter does not contain enough information
   to evaluate a claim, explain this limitation.

10. Give constructive feedback suitable for a student.

11. Award a score between 0 and 100.

12. For a blank answer, give zero.

13. Provide the explanation in {language}.

14. Be fair and avoid overly strict wording comparisons.

Return ONLY valid JSON:

{{
    "score": 0,
    "status": "Correct",
    "feedback": "Student-friendly feedback",
    "correct_points": [
        "Point correctly mentioned"
    ],
    "missing_points": [
        "Important point missing"
    ],
    "mistakes": [
        "Incorrect point"
    ],
    "model_answer": "Correct answer based on chapter",
    "chapter_evidence": "Relevant textbook evidence"
}}

The score must be an integer from 0 to 100.

Status must be one of:

Correct
Partially Correct
Incorrect

Make sure the score and status agree.

Do not give full marks if important parts are missing.
"""

    response = generate_ai_response(prompt)

    cleaned_response = clean_json_response(response)

    result = json.loads(cleaned_response)

    score = result.get("score", 0)

    try:
        score = int(score)
    except (ValueError, TypeError):
        score = 0

    score = max(0, min(100, score))

    status = result.get("status", "Incorrect")

    if status not in [
        "Correct",
        "Partially Correct",
        "Incorrect"
    ]:
        status = "Incorrect"

    return {
        "score": score,
        "status": status,
        "feedback": str(
            result.get("feedback", "")
        ),
        "correct_points": result.get(
            "correct_points", []
        ),
        "missing_points": result.get(
            "missing_points", []
        ),
        "mistakes": result.get(
            "mistakes", []
        ),
        "model_answer": str(
            result.get("model_answer", "")
        ),
        "chapter_evidence": str(
            result.get("chapter_evidence", "")
        )
    }


# =========================================================
# SIDEBAR SETTINGS
# =========================================================

st.sidebar.title("⚙️ Exam Settings")

class_level = st.sidebar.selectbox(
    "Select Class",
    [
        "9th",
        "10th",
        "11th",
        "12th"
    ]
)

subject = st.sidebar.text_input(
    "Subject",
    placeholder="Physics, Biology, Chemistry..."
)

board = st.sidebar.selectbox(
    "Educational Board",
    [
        "Not specified",
        "FBISE",
        "Punjab Board",
        "KPK Board",
        "Sindh Board",
        "Balochistan Board",
        "AJK Board",
        "Other"
    ]
)

chapter_title = st.sidebar.text_input(
    "Chapter Name",
    placeholder="Chapter 1: Introduction"
)

question_count = st.sidebar.slider(
    "Number of Questions",
    min_value=1,
    max_value=20,
    value=10
)

question_type = st.sidebar.selectbox(
    "Question Type",
    [
        "Mixed",
        "MCQ",
        "Short Questions",
        "Long Questions"
    ]
)

language = st.sidebar.selectbox(
    "Explanation Language",
    [
        "English",
        "Urdu",
        "Roman Urdu"
    ]
)

st.sidebar.caption(
    "Questions and explanations will be based "
    "on your uploaded textbook chapter."
)


# =========================================================
# MAIN TABS
# =========================================================

tab1, tab2, tab3 = st.tabs([
    "📖 Upload Chapter",
    "📝 Practice Test",
    "📊 Results"
])


# =========================================================
# TAB 1: UPLOAD CHAPTER
# =========================================================

with tab1:

    st.subheader("Upload Your Textbook Chapter")

    st.write(
        "Upload a chapter from your Matric or "
        "Intermediate textbook."
    )

    uploaded_file = st.file_uploader(
        "Choose your textbook file",
        type=[
            "pdf",
            "txt",
            "docx"
        ]
    )

    if uploaded_file:

        if st.button(
            "📚 Extract Chapter",
            use_container_width=True
        ):

            try:

                with st.spinner(
                    "Reading your textbook chapter..."
                ):

                    chapter_text = extract_chapter(
                        uploaded_file
                    )

                if not chapter_text.strip():

                    st.error(
                        "No readable text found. "
                        "Your PDF may be scanned."
                    )

                else:

                    st.session_state.chapter_text = (
                        chapter_text
                    )

                    st.session_state.chapter_name = (
                        uploaded_file.name
                    )

                    st.session_state.questions = []

                    st.session_state.answers = {}

                    st.session_state.results = {}

                    st.session_state.checked = False

                    st.success(
                        "Chapter uploaded and extracted successfully!"
                    )

            except Exception as error:

                st.error(
                    f"Chapter extraction failed: {error}"
                )

    if st.session_state.chapter_text:

        st.divider()

        st.success(
            f"Uploaded: {st.session_state.chapter_name}"
        )

        st.metric(
            "Extracted Characters",
            len(st.session_state.chapter_text)
        )

        with st.expander(
            "Preview Textbook Chapter"
        ):

            st.text(
                st.session_state.chapter_text[:12000]
            )

        st.info(
            "If the chapter is very long, the app may "
            "need to process a smaller section at a time."
        )

        if st.button(
            "🧠 Generate Practice Questions",
            use_container_width=True
        ):

            if not subject.strip():

                st.warning(
                    "Please enter your subject "
                    "in the sidebar."
                )

            elif not chapter_title.strip():

                st.warning(
                    "Please enter the chapter name."
                )

            else:

                try:

                    with st.spinner(
                        "AI is preparing your exam questions..."
                    ):

                        questions = generate_questions(
                            chapter_text=(
                                st.session_state.chapter_text
                            ),
                            class_level=class_level,
                            subject=subject,
                            board=board,
                            chapter_title=chapter_title,
                            question_count=question_count,
                            question_type=question_type,
                            language=language
                        )

                    st.session_state.questions = questions

                    st.session_state.answers = {}

                    st.session_state.results = {}

                    st.session_state.checked = False

                    st.success(
                        f"{len(questions)} questions generated!"
                    )

                    st.info(
                        "Open the Practice Test tab "
                        "to start answering."
                    )

                except Exception as error:

                    st.error(
                        f"Question generation failed: {error}"
                    )

                    st.caption(
                        "Check your Gemini API key, model name, "
                        "internet connection, and uploaded chapter."
                    )


# =========================================================
# TAB 2: PRACTICE TEST
# =========================================================

with tab2:

    st.subheader("📝 Your Practice Test")

    if not st.session_state.questions:

        st.info(
            "First upload your chapter and generate questions."
        )

    else:

        st.write(
            f"Chapter: {st.session_state.chapter_name}"
        )

        st.write(
            f"Total questions: "
            f"{len(st.session_state.questions)}"
        )

        st.divider()

        with st.form("practice_test_form"):

            current_answers = {}

            for index, question in enumerate(
                st.session_state.questions
            ):

                st.markdown(
                    f"### Question {index + 1}"
                )

                st.write(
                    question["question"]
                )

                if question["type"].lower() == "mcq":

                    answer = st.radio(
                        "Select your answer",
                        question["options"],
                        key=f"answer_{index}",
                        index=None
                    )

                else:

                    answer = st.text_area(
                        "Write your answer",
                        key=f"answer_{index}",
                        height=130,
                        placeholder=(
                            "Write your answer here..."
                        )
                    )

                current_answers[index] = answer

                st.divider()

            submitted = st.form_submit_button(
                "✅ Submit & Check Answers",
                use_container_width=True
            )

        if submitted:

            st.session_state.answers = (
                current_answers
            )

            st.session_state.results = {}

            st.session_state.checked = False

            if not any(
                str(answer or "").strip()
                for answer in current_answers.values()
            ):

                st.warning(
                    "Please answer at least one question."
                )

            else:

                progress = st.progress(0)

                status_text = st.empty()

                total = len(
                    st.session_state.questions
                )

                failed = False

                for index, question in enumerate(
                    st.session_state.questions
                ):

                    student_answer = (
                        current_answers.get(index, "")
                    )

                    if not str(
                        student_answer or ""
                    ).strip():

                        st.session_state.results[index] = {
                            "score": 0,
                            "status": "Incorrect",
                            "feedback": (
                                "No answer was provided."
                            ),
                            "correct_points": [],
                            "missing_points": [],
                            "mistakes": [],
                            "model_answer": (
                                question["answer"]
                            ),
                            "chapter_evidence": (
                                question["chapter_evidence"]
                            )
                        }

                    else:

                        try:

                            status_text.write(
                                f"Checking question "
                                f"{index + 1} of {total}..."
                            )

                            result = evaluate_answer(
                                chapter_text=(
                                    st.session_state.chapter_text
                                ),
                                question=question,
                                student_answer=str(
                                    student_answer
                                ),
                                language=language
                            )

                            st.session_state.results[
                                index
                            ] = result

                        except Exception as error:

                            failed = True

                            st.error(
                                f"Could not check question "
                                f"{index + 1}: {error}"
                            )

                            break

                    progress.progress(
                        (index + 1) / total
                    )

                status_text.empty()

                if not failed:

                    st.session_state.checked = True

                    st.success(
                        "Your answers have been checked!"
                    )

                    st.info(
                        "Open the Results tab to review "
                        "your score and explanations."
                    )

                else:

                    st.warning(
                        "Some answers could not be checked. "
                        "Submit again to retry."
                    )


# =========================================================
# TAB 3: RESULTS
# =========================================================

with tab3:

    st.subheader("📊 Your Exam Results")

    if not st.session_state.checked:

        st.info(
            "Submit your practice test first "
            "to see your results."
        )

    else:

        questions = st.session_state.questions

        results = st.session_state.results

        total_questions = len(questions)

        total_score = sum(
            results.get(index, {}).get(
                "score", 0
            )
            for index in range(total_questions)
        )

        maximum_score = total_questions * 100

        percentage = (
            total_score / maximum_score * 100
            if maximum_score
            else 0
        )

        correct_count = sum(
            1
            for index in range(total_questions)
            if results.get(index, {}).get(
                "status"
            ) == "Correct"
        )

        partial_count = sum(
            1
            for index in range(total_questions)
            if results.get(index, {}).get(
                "status"
            ) == "Partially Correct"
        )

        incorrect_count = sum(
            1
            for index in range(total_questions)
            if results.get(index, {}).get(
                "status"
            ) == "Incorrect"
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Score",
            f"{total_score}/{maximum_score}"
        )

        col2.metric(
            "Percentage",
            f"{percentage:.1f}%"
        )

        col3.metric(
            "Correct",
            correct_count
        )

        col4.metric(
            "Incorrect",
            incorrect_count
        )

        st.progress(
            int(percentage)
        )

        st.write(
            f"Partially correct: {partial_count}"
        )

        if percentage >= 80:

            st.success(
                "Excellent! Keep practicing to maintain "
                "your preparation."
            )

        elif percentage >= 50:

            st.info(
                "Good effort! Review the explanations "
                "and practice again."
            )

        else:

            st.warning(
                "Keep learning. Review the textbook "
                "chapter and retry the practice test."
            )

        st.divider()

        st.subheader(
            "Question-by-Question Review"
        )

        for index, question in enumerate(questions):

            result = results.get(index, {})

            student_answer = (
                st.session_state.answers.get(
                    index, ""
                )
            )

            with st.expander(
                f"Question {index + 1}: "
                f"{result.get('status', 'Not checked')}"
            ):

                st.markdown(
                    f"**Question:** "
                    f"{question['question']}"
                )

                st.write(
                    "**Your Answer:**"
                )

                st.write(
                    student_answer or "Not answered"
                )

                st.write(
                    f"**Score:** "
                    f"{result.get('score', 0)}/100"
                )

                st.write(
                    "**Feedback:**"
                )

                st.write(
                    result.get(
                        "feedback",
                        "No feedback available."
                    )
                )

                correct_points = result.get(
                    "correct_points", []
                )

                if correct_points:

                    st.write(
                        "**Correct Points:**"
                    )

                    for point in correct_points:

                        st.write(f"• {point}")

                missing_points = result.get(
                    "missing_points", []
                )

                if missing_points:

                    st.write(
                        "**Missing Points:**"
                    )

                    for point in missing_points:

                        st.write(f"• {point}")

                mistakes = result.get(
                    "mistakes", []
                )

                if mistakes:

                    st.write(
                        "**Mistakes to Improve:**"
                    )

                    for mistake in mistakes:

                        st.write(f"• {mistake}")

                st.write(
                    "**Model Answer:**"
                )

                st.write(
                    result.get(
                        "model_answer",
                        question["answer"]
                    )
                )

                evidence = result.get(
                    "chapter_evidence",
                    question["chapter_evidence"]
                )

                if evidence:

                    st.write(
                        "**Textbook Reference / Evidence:**"
                    )

                    st.write(evidence)

                explanation = question.get(
                    "explanation", ""
                )

                if explanation:

                    st.write(
                        "**Chapter Explanation:**"
                    )

                    st.write(explanation)

        st.divider()

        if st.button(
            "🔄 Start a New Practice Test",
            use_container_width=True
        ):

            st.session_state.questions = []

            st.session_state.answers = {}

            st.session_state.results = {}

            st.session_state.checked = False

            st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<div class="footer">
    <p>Pakistan AI Exam Preparation</p>
    <p>Learn from your own textbook • Practice • Improve</p>
</div>
""", unsafe_allow_html=True)
