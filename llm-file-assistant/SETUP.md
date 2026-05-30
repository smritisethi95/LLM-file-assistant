# Setup & Run Instructions

## Prerequisites
- Python 3.9+
- A Groq API key ([get one here](https://console.groq.com/keys))

---

## Windows

```powershell
cd llm-file-assistant
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edit .env and paste your Groq API key
python llm_file_assistant.py
```

## macOS

```bash
cd llm-file-assistant
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and paste your Groq API key
python llm_file_assistant.py
```

---

## .env File Format

```
GROQ_API_KEY=gsk_your_key_here
```

---

## Example Queries

```
"Read all resumes in the resumes folder"
"Find resumes mentioning Python experience"
"Create a summary file for resume_john_doe.txt"
"List all text files in the resumes directory"
```

Type `quit` or `exit` to end the session.