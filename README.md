# Career Advisory Platform

A simple Streamlit project for career guidance, resume analysis, interview preparation, skill-gap analysis, learning plans, recruitment support, candidate screening, and business guidance.

## Features

- Candidate and Business modes
- ChatGPT-style AI assistant
- Simple Python agent functions with an orchestrator
- Gemini API integration
- PDF, DOCX, and TXT resume/job-description reading
- Resume analyzer
- Mock interview feedback
- Skill-gap chart with Plotly
- Learning plan and career roadmap downloads
- Candidate screening based only on job-related qualifications
- SQLite database for conversations, messages, resume analysis, and interview results
- Friendly fallback when the API key is missing

## Project Structure

```text
ardhanarishwar/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── agents.py
├── ai.py
├── database.py
├── resume_parser.py
├── utils.py
├── data/
│   └── demo_jobs.csv
└── tests/
    └── test_basic.py
```

## Installation

```bash
cd ardhanarishwar
pip install -r requirements.txt
```

## API Key Setup

Copy `.env.example` to `.env` and add your key:

```text
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.6-flash
```

If the key is missing, the app will show a clear message and use a small demo fallback response.

## Run

```bash
streamlit run app.py
```

For local development, if another Streamlit app is already using port 8501, run this app on port 8502:

```bash
streamlit run app.py --server.port 8502
```

## Tests

```bash
pytest
```

## Notes

This project intentionally avoids LangChain, Docker, Redis, PostgreSQL, and microservices. It is designed to be easy for a student to understand and demonstrate.
