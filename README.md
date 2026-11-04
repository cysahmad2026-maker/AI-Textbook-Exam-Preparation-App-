
# 🇵🇰 Pakistan AI Exam Preparation

An AI-powered exam preparation application designed for Pakistani Matric and Intermediate students.

Students can upload their own textbook chapters, generate practice questions, attempt exams, check their answers, and receive explanations in English, Urdu, or Roman Urdu.

Built using Python, Streamlit, and Google's Gemini API.

---

## 🎓 Target Students

- Matric Class 9
- Matric Class 10
- Intermediate Class 11
- Intermediate Class 12

Designed for students studying under Pakistani educational boards.

Supported board options:

- FBISE
- Punjab Board
- KPK Board
- Sindh Board
- Balochistan Board
- AJK Board
- Other educational boards

Board-specific alignment depends on the uploaded textbook and the information provided by the student.

---

## ✨ Features

### 1. Upload Your Own Textbook

Students can upload:

- PDF
- TXT
- DOCX

The application extracts the chapter text and uses it as the primary source for generating questions and checking answers.

### 2. AI Practice Questions

Generate practice questions from uploaded chapters.

Available question types:

- Multiple Choice Questions (MCQs)
- Short Questions
- Long Questions
- Mixed Practice

Students can select how many questions they want.

### 3. AI Answer Checking

Students submit their answers and receive:

- Estimated marks
- Correct or partially correct status
- Explanation of their answers
- Missing important points
- Mistakes to improve
- Model answers
- Relevant textbook evidence

The AI evaluates the meaning of answers instead of relying only on exact wording.

### 4. Multilingual Explanations

Students can select:

- English
- Urdu
- Roman Urdu

Questions are generated in English, while explanations and answer feedback follow the selected language.

### 5. Student Results

The application provides:

- Total score
- Percentage
- Correct answers
- Partially correct answers
- Incorrect answers
- Question-by-question review

---

## 🛠️ Technologies

| Technology | Purpose |
|-----------|---------|
| Python | Application development |
| Streamlit | Frontend and web interface |
| Google Gemini API | AI question generation and evaluation |
| PyPDF | PDF text extraction |
| Python-docx | Word document extraction |
| GitHub | Source code management |
| Streamlit Community Cloud | Application deployment |

---

## 📁 Project Structure

```text
pakistan-ai-exam-preparation/
│
├── app.py
├── requirements.txt
└── README.md
```

---

## 🚀 Installation

### Step 1: Clone the Repository

Open your terminal or Git Bash.

```bash
git clone https://github.com/YOUR_USERNAME/pakistan-ai-exam-preparation.git
```

Replace YOUR_USERNAME with your GitHub username.

### Step 2: Open the Project

```bash
cd pakistan-ai-exam-preparation
```

### Step 3: Create a Virtual Environment

```bash
python -m venv venv
```

Activate it.

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Configure Gemini API

Obtain a Gemini API key from Google AI Studio:

https://aistudio.google.com/

Create a file named:

```text
.streamlit/secrets.toml
```

Your project should now look like:

```text
pakistan-ai-exam-preparation/
│
├── .streamlit/
│   └── secrets.toml
│
├── app.py
├── requirements.txt
└── README.md
```

Add your API key:

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

Replace YOUR_GEMINI_API_KEY with your actual API key.

Do not upload secrets.toml to GitHub.

### Step 6: Run the Application

```bash
streamlit run app.py
```

The application will open in your browser.

Default local address:

http://localhost:8501

---

## 🌐 Deploy on Streamlit Community Cloud

### Step 1: Push Your Code to GitHub

Your GitHub repository must contain:

```text
app.py
requirements.txt
README.md
```

### Step 2: Open Streamlit Community Cloud

https://share.streamlit.io/

Sign in with GitHub.

### Step 3: Create an Application

Select:

- Repository: pakistan-ai-exam-preparation
- Branch: main
- Main file: app.py

Click Deploy.

### Step 4: Configure API Secrets

Open your deployed application settings.

Go to:

Settings → Secrets

Add:

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

Save the secrets.

Streamlit will restart the application.

### Step 5: Open Your Application

After deployment, Streamlit will provide a public application URL.

Share that URL with students.

---

## 📚 How Students Use the App

### Step 1

Open the application.

### Step 2

Select their class:

9th, 10th, 11th, or 12th.

### Step 3

Select their subject and educational board.

### Step 4

Enter their chapter name.

### Step 5

Upload their textbook chapter.

### Step 6

Extract the chapter text.

### Step 7

Select the question type, number of questions, and explanation language.

### Step 8

Generate practice questions.

### Step 9

Attempt the questions.

### Step 10

Submit answers and receive AI feedback.

### Step 11

Review marks, explanations, mistakes, and model answers.

---

## 🔐 API Security

Never expose your Gemini API key in:

- app.py
- GitHub repositories
- Public README files
- Screenshots
- Public configuration files

Use Streamlit secrets or environment variables.

If an API key is accidentally published, revoke it and generate a replacement.

---

## ⚠️ Important Limitations

1. AI-generated questions may contain errors.
2. Answer checking is an estimated evaluation, not official board marking.
3. Text-based PDFs work best.
4. Scanned PDFs require OCR.
5. Very large chapters may exceed model context limits.
6. Urdu and Roman Urdu explanations may require proofreading.
7. Board-specific paper patterns are not guaranteed unless explicitly implemented and supported by the relevant syllabus.
8. API usage may incur costs or be subject to provider limits.

Students should verify important answers against their textbooks and teacher guidance.

---

## 🔮 Future Improvements

- User accounts and student profiles
- Save practice test history
- Chapter-wise progress tracking
- Downloadable PDF question papers
- Past paper practice
- Board-specific exam patterns
- Urdu Nastaliq questions
- OCR for scanned textbook pages
- Subject-wise dashboard
- Timed examinations
- Automatic question difficulty levels
- Teacher dashboard
- Student leaderboard
- Firebase or Supabase database
- AI-generated revision notes
- Weak-topic identification
- Chapter summaries
- Flashcards
- Daily study plans

---

## 👨‍💻 Development

Contributions are welcome.

To contribute:

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Test the application.
5. Submit a pull request.

---

## 📄 License

This project is intended for educational purposes.

Add an appropriate open-source license before distributing the application.

---

## 🎯 Project Goal

Make textbook-based exam preparation easier and more accessible for Pakistani Matric and Intermediate students.

Learn from your own textbook.

Practice exam questions.

Understand your mistakes.

Prepare smarter.
```
