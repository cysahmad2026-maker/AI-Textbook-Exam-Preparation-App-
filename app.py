
import os
import json
import streamlit as st
from google import genai
from pypdf import PdfReader
from docx import Document


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Exam Preparation",
    page_icon="🎓",
    layout="wide"
)


# --------------------------------------------------
# APP DESIGN
# --------------------------------------------------

st.title("🎓 AI Matric & Intermediate Exam Preparation")

st.write(
    "Upload your textbook chapter, generate exam questions, "
    "practice your answers, and receive AI feedback."
)

st.caption(
    "Designed for Matric and Intermediate students. "
    "AI-generated questions and checking may contain mistakes."
)


# --------------------------------------------------
# API CONFIGURATION
# --------------------------------------------------

DEFAULT_MODEL = "gemini-3.8-flash"


def get_api_key():
    """Read Gemini API key from Streamlit secrets or environment."""

    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
        if key:
            return str(key).strip()
    except Exception:
        pass

    return os.getenv("GEMINI_API_KEY", "").strip()


def get_model_name():
    """Read model name from secrets or environment."""

    try:
        model = st.secrets.get("GEMINI_MODEL", DEFAULT_MODEL)
        if model:
            return str(model).strip()
    except Exception:
        pass

    return os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip()


def get_gemini_client():
    """Create Gemini client."""

    api_key = get_api_key()

    if not api_key:
        raise ValueError(
            "Gemini API key is missing. Add GEMINI_API_KEY "
            "to Streamlit secrets or environment variables."
        )

    return genai.Client(api_key=api_key)


def generate_ai_response(prompt):
    """Generate response using Gemini Interactions API."""

    client = get_gemini_client()
    model = get_model_name()

    try:
        response = client.interactions.create(
            model=model,
            input=prompt
        )

        answer = response.output_text

        if not answer:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return answer.strip()

    except Exception as error:
        raise RuntimeError(
            f"Gemini API error: {error}"
        ) from error


# --------------------------------------------------
# API CONNECTION TEST
# --------------------------------------------------

def test_gemini_connection():
    response = generate_ai_response(
        "Reply with exactly: GEMINI CONNECTION SUCCESSFUL"
    )

    return response


# --------------------------------------------------
# TEXTBOOK FILE EXTRACTION
# --------------------------------------------------

def extract_text_from_file(uploaded_file):
    """Extract text from PDF, DOCX, or TXT."""

    file_name = uploaded_file.name.lower()

    try:
        if file_name.endswith(".pdf"):
            pdf = PdfReader(uploaded_file)

            pages = []

            for page in pdf.pages:
                page_text = page.extract_text() or ""
                pages.append(page_text)

            text = "\n".join(pages)

        elif file_name.endswith(".docx"):
            document = Document(uploaded_file)

            paragraphs = [
                paragraph.text
                for paragraph in document.paragraphs
            ]

            text = "\n".join(paragraphs)

        elif file_name.endswith(".txt"):
            text = uploaded_file.getvalue().decode(
                "utf-8",
                errors="ignore"
            )

        else:
            raise ValueError(
                "Unsupported file format. Upload PDF, DOCX, or TXT."
            )

        text = text.strip()

        if not text:
            raise ValueError(
                "No readable text found. This may be a scanned PDF. "
                "Please upload a text-based PDF or TXT/DOCX file."
            )

        return text

    except Exception as error:
        raise RuntimeError(
            f"Could not read uploaded file: {error}"
        ) from error


# --------------------------------------------------
# PROMPT HELPER
# --------------------------------------------------

def build_language_instruction(language):
    """Instructions for answer language."""

    instructions = {
        "English": "Write the response in simple English.",
        "Urdu": "Write the response in Urdu script.",
        "Roman Urdu": (
            "Write the response in Roman Urdu using "
            "Urdu words written in English letters."
        )
    }

    return instructions.get(language, instructions["English"])


def build_chapter_context(chapter_text):
    """Keep prompt within reasonable size."""

    max_chars = 30000

    if len(chapter_text) > max_chars:
        chapter_text = chapter_text[:max_chars]

    return chapter_text


# --------------------------------------------------
# QUESTION GENERATION
# --------------------------------------------------

def generate_questions(
    chapter_text,
    board,
    class_name,
    subject,
    chapter_name,
    question_type,
    difficulty,
    number_of_questions,
    language
):
    """Generate questions using uploaded chapter."""

    chapter_text = build_chapter_context(chapter_text)
    language_instruction = build_language_instruction(language)

    prompt = f"""
You are an experienced Pakistan Matric and Intermediate
board examination teacher.

Create exam preparation questions strictly based on
the textbook chapter provided below.

STUDENT DETAILS:
Education system: {board}
Class: {class_name}
Subject: {subject}
Chapter: {chapter_name}
Question type: {question_type}
Difficulty: {difficulty}
Number of questions: {number_of_questions}

LANGUAGE:
{language_instruction}

RULES:
1. Use the uploaded chapter as the main source.
2. Do not invent facts that are not supported by the chapter.
3. Questions should be suitable for the student's class.
4. Use clear and simple wording.
5. For MCQs, provide exactly four options.
6. For MCQs, clearly identify the correct answer.
7. For short and long questions, provide a model answer.
8. Add a brief explanation for each answer.
9. Avoid duplicate questions.
10. If the chapter does not contain enough information,
   explain this rather than inventing content.
11. Return valid JSON only.
12. Do not include Markdown fences.

Return this JSON structure:

{{
  "questions": [
    {{
      "question": "Question text",
      "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "correct_answer": "Correct answer",
      "model_answer": "Full model answer",
      "explanation": "Explanation"
    }}
  ]
}}

For short and long questions, options can be an empty list.
For MCQs, correct_answer must match one of the options.

TEXTBOOK CHAPTER:
{chapter_text}
"""

    response = generate_ai_response(prompt)

    # Remove Markdown fences if model includes them.
    cleaned = response.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "", 1)
        cleaned = cleaned.replace("```", "")
        cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)

    except json.JSONDecodeError:
        raise ValueError(
            "Gemini returned invalid JSON. Please try generating "
            "questions again."
        )

    questions = data.get("questions", [])

    if not isinstance(questions, list) or not questions:
        raise ValueError(
            "Gemini did not return any questions."
        )

    return questions


# --------------------------------------------------
# ANSWER EVALUATION
# --------------------------------------------------

def evaluate_answers(
    chapter_text,
    questions,
    student_answers,
    language,
    board,
    class_name,
    subject
):
    """Evaluate student answers based on chapter."""

    chapter_text = build_chapter_context(chapter_text)
    language_instruction = build_language_instruction(language)

    student_data = []

    for index, question in enumerate(questions):
        student_data.append({
            "question_number": index + 1,
            "question": question.get("question", ""),
            "model_answer": question.get("model_answer", ""),
            "correct_answer": question.get("correct_answer", ""),
            "student_answer": student_answers.get(index, "")
        })

    prompt = f"""
You are a fair and supportive Pakistan board exam teacher.

Evaluate the student's answers using the uploaded textbook
chapter and the model answers.

STUDENT:
Board: {board}
Class: {class_name}
Subject: {subject}

LANGUAGE:
{language_instruction}

IMPORTANT RULES:
1. Evaluate each answer individually.
2. Use the textbook chapter as the primary source.
3. Accept correct answers written in different wording.
4. Do not require exact textbook wording unless necessary.
5. Give partial marks when an answer is partly correct.
6. Do not give full marks to blank or incorrect answers.
7. Explain mistakes in a supportive way.
8. Use simple language suitable for students.
9. Do not invent facts outside the chapter.
10. Score each answer from 0 to 5.
11. Return valid JSON only.
12. Do not include Markdown fences.

Return this JSON structure:

{{
  "results": [
    {{
      "question_number": 1,
      "student_answer": "Student answer",
      "score": 4,
      "max_score": 5,
      "status": "Correct / Partially Correct / Incorrect / Not Answered",
      "feedback": "Feedback",
      "correct_answer": "Correct answer"
    }}
  ],
  "total_score": 0,
  "max_total_score": 0,
  "overall_feedback": "Overall feedback"
}}

TEXTBOOK CHAPTER:
{chapter_text}

QUESTIONS AND STUDENT ANSWERS:
{json.dumps(student_data, ensure_ascii=False, indent=2)}
"""

    response = generate_ai_response(prompt)

    cleaned = response.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "", 1)
        cleaned = cleaned.replace("```", "")
        cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)

    except json.JSONDecodeError:
        raise ValueError(
            "Gemini returned invalid evaluation JSON. "
            "Please try checking answers again."
        )

    if "results" not in data:
        raise ValueError(
            "Gemini did not return evaluation results."
        )

    return data


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.header("⚙️ Settings")

    st.write("**Gemini API Connection**")

    if get_api_key():
        st.success("API key detected")
    else:
        st.warning("API key not found")

    if st.button("🔌 Test Gemini API", use_container_width=True):
        try:
            with st.spinner("Testing Gemini API..."):
                result = test_gemini_connection()

            st.success("Gemini API connected successfully!")
            st.write(result)

        except Exception as error:
            st.error(str(error))

    st.divider()

    st.caption(
        "Add your Gemini key to Streamlit Cloud Secrets. "
        "Never upload API keys to GitHub."
    )


# --------------------------------------------------
# STUDENT DETAILS
# --------------------------------------------------

st.subheader("📚 Student Information")

col1, col2, col3 = st.columns(3)

with col1:
    board = st.selectbox(
        "Education System",
        [
            "Pakistan - Matric",
            "Pakistan - Intermediate"
        ]
    )

with col2:
    class_name = st.selectbox(
        "Class",
        [
            "9th",
            "10th",
            "11th",
            "12th"
        ]
    )

with col3:
    subject = st.text_input(
        "Subject",
        placeholder="e.g. Computer Science, Physics, Biology"
    )


chapter_name = st.text_input(
    "Chapter Name",
    placeholder="e.g. Introduction to Computer"
)


# --------------------------------------------------
# UPLOAD TEXTBOOK
# --------------------------------------------------

st.subheader("📄 Upload Textbook Chapter")

uploaded_file = st.file_uploader(
    "Upload a chapter file",
    type=["pdf", "docx", "txt"],
    help="Supported formats: PDF, DOCX, TXT"
)

chapter_text = ""

if uploaded_file:
    try:
        chapter_text = extract_text_from_file(uploaded_file)

        st.success("Chapter uploaded and text extracted successfully.")

        with st.expander("Preview extracted chapter text"):
            st.text_area(
                "Extracted Text",
                chapter_text[:5000],
                height=250,
                disabled=True
            )

        st.caption(
            f"Extracted characters: {len(chapter_text)}"
        )

    except Exception as error:
        st.error(str(error))


# --------------------------------------------------
# QUESTION SETTINGS
# --------------------------------------------------

st.subheader("📝 Practice Question Settings")

col1, col2, col3 = st.columns(3)

with col1:
    question_type = st.selectbox(
        "Question Type",
        [
            "MCQs",
            "Short Questions",
            "Long Questions",
            "Mixed Questions"
        ]
    )

with col2:
    difficulty = st.selectbox(
        "Difficulty",
        [
            "Easy",
            "Medium",
            "Hard"
        ]
    )

with col3:
    number_of_questions = st.selectbox(
        "Number of Questions",
        [5, 10, 15, 20]
    )


language = st.selectbox(
    "Question and Feedback Language",
    [
        "English",
        "Urdu",
        "Roman Urdu"
    ]
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "questions" not in st.session_state:
    st.session_state.questions = []

if "chapter_text" not in st.session_state:
    st.session_state.chapter_text = ""

if "student_answers" not in st.session_state:
    st.session_state.student_answers = {}

if "evaluation" not in st.session_state:
    st.session_state.evaluation = None


# --------------------------------------------------
# GENERATE QUESTIONS
# --------------------------------------------------

st.divider()

if st.button(
    "🚀 Generate Exam Questions",
    type="primary",
    use_container_width=True
):

    if not get_api_key():
        st.error(
            "Gemini API key is missing. Add it to Streamlit secrets."
        )

    elif not uploaded_file:
        st.error("Please upload your textbook chapter first.")

    elif not subject.strip():
        st.error("Please enter your subject.")

    elif not chapter_name.strip():
        st.error("Please enter the chapter name.")

    elif not chapter_text.strip():
        st.error("No chapter text was extracted.")

    else:
        try:
            with st.spinner("Generating questions from your chapter..."):

                questions = generate_questions(
                    chapter_text=chapter_text,
                    board=board,
                    class_name=class_name,
                    subject=subject,
                    chapter_name=chapter_name,
                    question_type=question_type,
                    difficulty=difficulty,
                    number_of_questions=number_of_questions,
                    language=language
                )

            st.session_state.questions = questions
            st.session_state.chapter_text = chapter_text
            st.session_state.student_answers = {}
            st.session_state.evaluation = None

            st.success(
                f"Successfully generated {len(questions)} questions!"
            )

        except Exception as error:
            st.error(f"Question generation failed: {error}")


# --------------------------------------------------
# DISPLAY QUESTIONS
# --------------------------------------------------

questions = st.session_state.questions

if questions:

    st.divider()
    st.header("✍️ Your Practice Exam")

    st.write(
        "Answer the questions below. "
        "When you finish, click Submit Answers."
    )

    with st.form("exam_answer_form"):

        current_answers = {}

        for index, question in enumerate(questions):

            question_text = question.get(
                "question",
                f"Question {index + 1}"
            )

            st.markdown(
                f"### Question {index + 1}"
            )

            st.write(question_text)

            options = question.get("options", [])

            if options and question_type == "MCQs":

                answer = st.radio(
                    "Choose your answer",
                    options,
                    key=f"answer_{index}",
                    index=None
                )

            else:

                answer = st.text_area(
                    "Your Answer",
                    key=f"answer_{index}",
                    height=120,
                    placeholder="Write your answer here..."
                )

            current_answers[index] = answer or ""

            st.divider()

        submitted = st.form_submit_button(
            "📊 Submit Answers for Evaluation",
            type="primary",
            use_container_width=True
        )

    if submitted:

        if not get_api_key():
            st.error("Gemini API key is missing.")

        else:

            try:
                with st.spinner("Checking your answers..."):

                    evaluation = evaluate_answers(
                        chapter_text=st.session_state.chapter_text,
                        questions=questions,
                        student_answers=current_answers,
                        language=language,
                        board=board,
                        class_name=class_name,
                        subject=subject
                    )

                st.session_state.student_answers = current_answers
                st.session_state.evaluation = evaluation

                st.success("Your answers have been evaluated!")

            except Exception as error:
                st.error(f"Answer evaluation failed: {error}")


# --------------------------------------------------
# SHOW EVALUATION
# --------------------------------------------------

evaluation = st.session_state.evaluation

if evaluation:

    st.divider()
    st.header("📊 Exam Result")

    total_score = evaluation.get("total_score", 0)
    max_score = evaluation.get("max_total_score", 0)

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Your Score",
            f"{total_score} / {max_score}"
        )

    with col2:
        if max_score:
            percentage = (total_score / max_score) * 100
        else:
            percentage = 0

        st.metric(
            "Percentage",
            f"{percentage:.1f}%"
        )

    st.progress(
        min(max(percentage / 100, 0.0), 1.0)
    )

    st.subheader("Overall Feedback")

    st.write(
        evaluation.get(
            "overall_feedback",
            "Keep practicing!"
        )
    )

    st.subheader("Question-by-Question Feedback")

    results = evaluation.get("results", [])

    for result in results:

        question_number = result.get(
            "question_number",
            "?"
        )

        score = result.get("score", 0)
        max_score = result.get("max_score", 5)

        status = result.get(
            "status",
            "Evaluated"
        )

        with st.expander(
            f"Question {question_number} — {status} — {score}/{max_score}",
            expanded=False
        ):

            st.markdown("**Your Answer**")

            st.write(
                result.get(
                    "student_answer",
                    "No answer"
                )
            )

            st.markdown("**Feedback**")

            st.write(
                result.get(
                    "feedback",
                    "No feedback available."
                )
            )

            st.markdown("**Correct Answer**")

            st.write(
                result.get(
                    "correct_answer",
                    "Not available."
                )
            )

    report = {
        "score": total_score,
        "maximum_score": max_score,
        "percentage": round(percentage, 2),
        "overall_feedback": evaluation.get(
            "overall_feedback", ""
        ),
        "results": results
    }

    st.download_button(
        "⬇️ Download Result Report",
        data=json.dumps(
            report,
            ensure_ascii=False,
            indent=2
        ),
        file_name="exam_result.json",
        mime="application/json"
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "AI Exam Preparation | Matric & Intermediate | "
    "Powered by Google Gemini"
)

st.caption(
    "Always verify important answers with your official textbook "
    "and teacher. AI feedback is not an official board result."
)
