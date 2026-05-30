"""
fs_tools.py - Core File System Tools Module

Provides structured tool interfaces for file I/O operations:
- read_file: Read resume files (PDF, TXT, DOCX)
- list_files: List and filter files in a directory
- write_file: Write content to files
- search_in_file: Search for keywords in file content
"""

import os
import datetime
from pathlib import Path


def read_file(filepath: str) -> dict:
    """
    Read resume files (PDF, TXT, DOCX) and extract text content.

    Args:
        filepath: Path to the file to read.

    Returns:
        dict with keys:
            - success (bool): Whether the operation succeeded
            - content (str): Extracted text content
            - metadata (dict): File metadata (name, size, extension, modified)
            - error (str|None): Error message if failed
    """
    try:
        filepath = os.path.abspath(filepath)

        if not os.path.exists(filepath):
            return {
                "success": False,
                "content": None,
                "metadata": None,
                "error": f"File not found: {filepath}"
            }

        if not os.path.isfile(filepath):
            return {
                "success": False,
                "content": None,
                "metadata": None,
                "error": f"Path is not a file: {filepath}"
            }

        ext = os.path.splitext(filepath)[1].lower()
        stat = os.stat(filepath)
        metadata = {
            "name": os.path.basename(filepath),
            "size_bytes": stat.st_size,
            "extension": ext,
            "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
        }

        content = ""

        if ext == ".txt":
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

        elif ext == ".pdf":
            try:
                import PyPDF2
                with open(filepath, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    pages = []
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            pages.append(text)
                    content = "\n".join(pages)
            except ImportError:
                return {
                    "success": False,
                    "content": None,
                    "metadata": metadata,
                    "error": "PyPDF2 is required to read PDF files. Install with: pip install PyPDF2"
                }

        elif ext == ".docx":
            try:
                import docx
                doc = docx.Document(filepath)
                paragraphs = [para.text for para in doc.paragraphs]
                content = "\n".join(paragraphs)
            except ImportError:
                return {
                    "success": False,
                    "content": None,
                    "metadata": metadata,
                    "error": "python-docx is required to read DOCX files. Install with: pip install python-docx"
                }

        else:
            # Attempt to read as plain text
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                return {
                    "success": False,
                    "content": None,
                    "metadata": metadata,
                    "error": f"Unsupported file format: {ext}"
                }

        return {
            "success": True,
            "content": content,
            "metadata": metadata,
            "error": None
        }

    except PermissionError:
        return {
            "success": False,
            "content": None,
            "metadata": None,
            "error": f"Permission denied: {filepath}"
        }
    except Exception as e:
        return {
            "success": False,
            "content": None,
            "metadata": None,
            "error": f"Unexpected error: {str(e)}"
        }


def list_files(directory: str, extension: str = None) -> list:
    """
    List all files in a directory with optional extension filter.

    Args:
        directory: Path to the directory to list.
        extension: Optional file extension filter (e.g., '.pdf', '.txt').

    Returns:
        list of dicts, each containing:
            - name (str): File name
            - path (str): Full file path
            - size_bytes (int): File size in bytes
            - modified (str): Last modified timestamp (ISO format)
            - extension (str): File extension
        Returns a dict with error key if the operation fails.
    """
    try:
        directory = os.path.abspath(directory)

        if not os.path.exists(directory):
            return {"success": False, "files": [], "error": f"Directory not found: {directory}"}

        if not os.path.isdir(directory):
            return {"success": False, "files": [], "error": f"Path is not a directory: {directory}"}

        # Normalize extension
        if extension and not extension.startswith("."):
            extension = f".{extension}"

        files = []
        for entry in os.listdir(directory):
            full_path = os.path.join(directory, entry)
            if not os.path.isfile(full_path):
                continue

            file_ext = os.path.splitext(entry)[1].lower()

            # Apply extension filter
            if extension and file_ext != extension.lower():
                continue

            stat = os.stat(full_path)
            files.append({
                "name": entry,
                "path": full_path,
                "size_bytes": stat.st_size,
                "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "extension": file_ext
            })

        return {"success": True, "files": files, "error": None}

    except PermissionError:
        return {"success": False, "files": [], "error": f"Permission denied: {directory}"}
    except Exception as e:
        return {"success": False, "files": [], "error": f"Unexpected error: {str(e)}"}


def write_file(filepath: str, content: str) -> dict:
    """
    Write content to a file, creating directories if needed.

    Args:
        filepath: Path to the file to write.
        content: String content to write.

    Returns:
        dict with keys:
            - success (bool): Whether the operation succeeded
            - filepath (str): Absolute path of the written file
            - size_bytes (int): Size of the written file
            - error (str|None): Error message if failed
    """
    try:
        filepath = os.path.abspath(filepath)

        # Create parent directories if they don't exist
        parent_dir = os.path.dirname(filepath)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        stat = os.stat(filepath)
        return {
            "success": True,
            "filepath": filepath,
            "size_bytes": stat.st_size,
            "error": None
        }

    except PermissionError:
        return {
            "success": False,
            "filepath": filepath,
            "size_bytes": 0,
            "error": f"Permission denied: {filepath}"
        }
    except Exception as e:
        return {
            "success": False,
            "filepath": filepath,
            "size_bytes": 0,
            "error": f"Unexpected error: {str(e)}"
        }


def search_in_file(filepath: str, keyword: str) -> dict:
    """
    Search for keywords in file content (case-insensitive).

    Args:
        filepath: Path to the file to search.
        keyword: Keyword to search for.

    Returns:
        dict with keys:
            - success (bool): Whether the operation succeeded
            - matches (list): List of matches with line number and context
            - total_matches (int): Total number of matches found
            - error (str|None): Error message if failed
    """
    try:
        # First read the file content
        result = read_file(filepath)
        if not result["success"]:
            return {
                "success": False,
                "matches": [],
                "total_matches": 0,
                "error": result["error"]
            }

        content = result["content"]
        lines = content.split("\n")
        keyword_lower = keyword.lower()
        matches = []

        for i, line in enumerate(lines, start=1):
            if keyword_lower in line.lower():
                # Get surrounding context (1 line before and after)
                context_start = max(0, i - 2)
                context_end = min(len(lines), i + 1)
                context_lines = lines[context_start:context_end]

                matches.append({
                    "line_number": i,
                    "line": line.strip(),
                    "context": "\n".join(context_lines)
                })

        return {
            "success": True,
            "matches": matches,
            "total_matches": len(matches),
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "matches": [],
            "total_matches": 0,
            "error": f"Unexpected error: {str(e)}"
        }


# Tool definitions for LLM function calling
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a resume file (PDF, TXT, or DOCX) and extract its text content along with metadata.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "The path to the file to read"
                    }
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List all files in a directory, optionally filtered by file extension. Returns file metadata including name, size, and modification date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "The path to the directory to list"
                    },
                    "extension": {
                        "type": "string",
                        "description": "Optional file extension filter (e.g., '.pdf', '.txt', '.docx')"
                    }
                },
                "required": ["directory"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write text content to a file. Creates parent directories if they don't exist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "The path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "The text content to write to the file"
                    }
                },
                "required": ["filepath", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_in_file",
            "description": "Search for a keyword in a file's content. Performs case-insensitive search and returns matching lines with surrounding context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "The path to the file to search"
                    },
                    "keyword": {
                        "type": "string",
                        "description": "The keyword to search for (case-insensitive)"
                    }
                },
                "required": ["filepath", "keyword"]
            }
        }
    }
]
