# LLM File Assistant - Resume Manager

A Python application demonstrating LLM function calling (tool use) for file system operations on resume documents.

## Overview

This project implements:
- **Part A**: Core file system tools (`fs_tools.py`) for reading, listing, writing, and searching files
- **Part B**: LLM integration (`llm_file_assistant.py`) that uses OpenAI's function calling to invoke tools based on natural language queries

## Project Structure

```
llm-file-assistant/
├── fs_tools.py              # Core file system tools module
├── llm_file_assistant.py    # LLM integration with interactive chat
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
├── README.md                # This file
└── resumes/                 # Sample resume files
    ├── resume_john_doe.txt
    ├── resume_jane_smith.txt
    ├── resume_michael_johnson.txt
    ├── resume_sarah_williams.txt
    ├── resume_david_chen.txt
    ├── resume_emily_martinez.txt
    ├── resume_alex_kumar.txt
    └── resume_rachel_thompson.txt
```

## Setup

### Prerequisites
- Python 3.9+
- An OpenAI API key

### Installation

1. Clone/download the project:
   ```bash
   cd llm-file-assistant
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

## Usage

### Running the Interactive Assistant

```bash
python llm_file_assistant.py
```

This launches an interactive chat where you can ask natural language questions about the resume files.

### Example Queries

| Query | What it does |
|-------|-------------|
| "Read all resumes in the resumes folder" | Lists and reads all resume files |
| "Find resumes mentioning Python experience" | Searches each resume for "Python" |
| "Create a summary file for resume_john_doe.txt" | Reads the resume and writes a summary |
| "List all text files in the resumes directory" | Lists files filtered by .txt extension |
| "Who has Kubernetes experience?" | Searches resumes for Kubernetes mentions |
| "Compare the skills of Jane Smith and David Chen" | Reads both resumes and compares |

### Using Tools Directly (Without LLM)

```python
from fs_tools import read_file, list_files, write_file, search_in_file

# Read a resume
result = read_file("resumes/resume_john_doe.txt")
print(result["content"])

# List all .txt files
files = list_files("resumes", extension=".txt")
print(files)

# Search for a keyword
matches = search_in_file("resumes/resume_john_doe.txt", "Python")
print(matches)

# Write a summary
write_file("output/summary.txt", "John Doe - Senior Software Engineer")
```

## Tools Reference

### `read_file(filepath: str) → dict`
Reads resume files (PDF, TXT, DOCX) and extracts text content.

**Returns:**
```json
{
  "success": true,
  "content": "extracted text...",
  "metadata": {"name": "file.txt", "size_bytes": 1234, "extension": ".txt", "modified": "2024-01-01T00:00:00"},
  "error": null
}
```

### `list_files(directory: str, extension: str = None) → dict`
Lists files in a directory with optional extension filtering.

**Returns:**
```json
{
  "success": true,
  "files": [{"name": "file.txt", "path": "/full/path", "size_bytes": 1234, "modified": "...", "extension": ".txt"}],
  "error": null
}
```

### `write_file(filepath: str, content: str) → dict`
Writes content to a file, creating directories if needed.

**Returns:**
```json
{
  "success": true,
  "filepath": "/full/path/to/file.txt",
  "size_bytes": 1234,
  "error": null
}
```

### `search_in_file(filepath: str, keyword: str) → dict`
Searches for keywords (case-insensitive) with surrounding context.

**Returns:**
```json
{
  "success": true,
  "matches": [{"line_number": 5, "line": "matched line", "context": "surrounding text"}],
  "total_matches": 1,
  "error": null
}
```

## How Tool Calling Works

1. User sends a natural language query
2. The LLM analyzes the query and decides which tool(s) to call
3. The application executes the tool function with the LLM-provided arguments
4. Results are sent back to the LLM
5. The LLM may call additional tools or provide a final response
6. The final response is displayed to the user

```
User Query → LLM → Tool Call Decision → Execute Tool → Results → LLM → Response
```

## Dependencies

| Package | Purpose |
|---------|---------|
| `openai` | OpenAI API client for LLM integration |
| `python-dotenv` | Load environment variables from .env file |
| `PyPDF2` | PDF file reading support |
| `python-docx` | DOCX file reading support |

## Error Handling

All tools return structured responses with:
- `success`: Boolean indicating operation status
- `error`: Descriptive error message (null on success)

Common errors handled:
- File not found
- Permission denied
- Unsupported file format
- Missing dependencies (PyPDF2, python-docx)
