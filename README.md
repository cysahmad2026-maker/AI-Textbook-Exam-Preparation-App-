
# 🎓 AI Matric & Intermediate Exam Preparation

An AI-powered exam preparation application for Pakistan Matric and Intermediate students.

Students can upload textbook chapters, generate practice questions, submit answers, and receive AI-based feedback using Google Gemini.

## 🚀 Features

- Upload textbook chapters in PDF, TXT, and DOCX formats.
- Generate MCQs, short questions, long questions, or mixed questions.
- Select Matric or Intermediate education system.
- Select class 9th, 10th, 11th, or 12th.
- Enter subject and chapter name.
- Select Easy, Medium, or Hard difficulty.
- Generate 5, 10, 15, or 20 questions.
- Practice questions in English, Urdu, or Roman Urdu.
- Submit answers for AI evaluation.
- Receive feedback and model answers.
- View marks and percentage.
- Download exam result report as JSON.
- Test Gemini API connection.
- Deploy through Streamlit Community Cloud.

## 🛠️ Technologies

- Python
- Streamlit
- Google Gemini API
- Google Gen AI Python SDK
- PyPDF
- Python-docx
- GitHub
- Streamlit Community Cloud

## 📁 Project Structure

```text
AI-Exam-Preparation/
│
├── app.py
├── requirements.txt
└── README.md
```

## 🔑 Gemini API Setup

### Step 1: Get your API key

1. Open Google AI Studio:
   https://aistudio.google.com/
2. Create or select a project.
3. Create a Gemini API key.
4. Copy your API key.

Never publish your API key in GitHub.

### Step 2: Configure Streamlit secrets locally

Create a folder named:

```text
.streamlit
```

Inside it, create:

```text
secrets.toml
```

Add:

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
GEMINI_MODEL = "gemini-3.8-flash"
```

Replace `YOUR_GEMINI_API_KEY` with your actual API key.

Do not upload this secrets file to GitHub.

### Step 3: Install requirements

Open your terminal inside the project directory.

Run:

```bash
pip install --upgrade -r requirements.txt
```

### Step 4: Start the application

Run:

```bash
streamlit run app.py
```

The application will open in your browser.

Usually the local URL is:

```text
http://localhost:8501
```

## ☁️ Deploy on Streamlit Community Cloud

### Step 1: Upload project to GitHub

Create a GitHub repository.

Upload these files:

- app.py
- requirements.txt
- README.md

Do not upload your API key.

### Step 2: Open Streamlit Cloud

Visit:

https://share.streamlit.io/

Sign in using GitHub.

### Step 3: Create application

Click:

**Create app**

Select:

- Repository: Your GitHub repository
- Branch: main
- Main file path: app.py

Click Deploy.

### Step 4: Add API key

Open your deployed application's settings.

Find the Secrets section.

Add:

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
GEMINI_MODEL = "gemini-3.8-flash"
```

Save the secrets.

Restart or redeploy the application if necessary.

## 🧪 Test Gemini API

Open your application.

In the sidebar, click:

**Test Gemini API**

A successful response should display:

```text
GEMINI CONNECTION SUCCESSFUL
```

If the connection fails:

1. Check that your API key is correct.
2. Check that Gemini API access is enabled.
3. Confirm that your selected model is available.
4. Check your API quota and billing requirements.
5. Check that google-genai is installed and updated.

## 📚 How to Use

1. Open the application.
2. Select your education system.
3. Select your class.
4. Enter your subject.
5. Enter your chapter name.
6. Upload your textbook chapter.
7. Choose question type.
8. Choose difficulty.
9. Choose number of questions.
10. Choose language.
11. Click Generate Exam Questions.
12. Answer the questions.
13. Click Submit Answers for Evaluation.
14. Review marks and feedback.
15. Download your result report if needed.

## ⚠️ Important Notes

- The application requires a valid Gemini API key.
- API usage may have limits or costs depending on your Google AI account.
- Scanned PDFs may not contain extractable text.
- The app currently reads text from PDF, DOCX, and TXT files.
- Very large chapters are shortened before being sent to Gemini.
- AI-generated questions and feedback may contain errors.
- Always verify important answers using your official textbook and teacher.
- The result is for practice and is not an official board examination result.

## 🔒 Security

Never commit API keys or secrets to GitHub.

Use Streamlit Secrets for deployment.

If an API key is accidentally published, revoke it and create a new one.

## 👨‍💻 Development

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
streamlit run app.py
```

## 📄 License

This project is intended for educational use.
