"""
llm_file_assistant.py - LLM-powered File Assistant

Integrates file system tools with an LLM (OpenAI) to enable
natural language queries for file operations on resumes.

Usage:
    python llm_file_assistant.py
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from fs_tools import read_file, list_files, write_file, search_in_file, TOOL_DEFINITIONS

# Load environment variables
load_dotenv()

# Initialize Groq client (OpenAI-compatible API)
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Map tool names to functions
TOOL_FUNCTIONS = {
    "read_file": read_file,
    "list_files": list_files,
    "write_file": write_file,
    "search_in_file": search_in_file,
}

SYSTEM_PROMPT = """You are a helpful file assistant specialized in managing and analyzing resume files.
You have access to the following tools:
- read_file: Read resume files (PDF, TXT, DOCX) and extract text content
- list_files: List files in a directory with optional extension filtering
- write_file: Write content to files (useful for creating summaries)
- search_in_file: Search for keywords in file content

When asked about resumes, use the tools to read, search, and analyze the files.
The resumes are typically stored in the 'resumes' folder relative to the current directory.
Always provide clear, structured responses based on the actual file contents."""


def execute_tool_call(tool_call):
    """Execute a single tool call and return the result."""
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    if function_name not in TOOL_FUNCTIONS:
        return json.dumps({"error": f"Unknown function: {function_name}"})

    func = TOOL_FUNCTIONS[function_name]
    result = func(**arguments)
    return json.dumps(result, default=str)


def chat(user_message: str, conversation_history: list) -> str:
    """
    Send a user message to the LLM with tool access and return the response.

    Args:
        user_message: The user's natural language query.
        conversation_history: List of previous messages in the conversation.

    Returns:
        The assistant's final text response.
    """
    conversation_history.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history,
        tools=TOOL_DEFINITIONS,
        tool_choice="auto",
    )

    message = response.choices[0].message

    # Handle tool calls iteratively until the LLM provides a final response
    while message.tool_calls:
        conversation_history.append(message)

        # Execute each tool call
        for tool_call in message.tool_calls:
            print(f"  [Tool Call] {tool_call.function.name}({tool_call.function.arguments})")
            result = execute_tool_call(tool_call)
            conversation_history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

        # Get next response from LLM
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
        )
        message = response.choices[0].message

    # Append final assistant message
    conversation_history.append({"role": "assistant", "content": message.content})
    return message.content


def main():
    """Interactive chat loop for the file assistant."""
    print("=" * 60)
    print("  LLM File Assistant - Resume Manager")
    print("=" * 60)
    print("\nI can help you manage and analyze resume files.")
    print("Example queries:")
    print('  - "Read all resumes in the resumes folder"')
    print('  - "Find resumes mentioning Python experience"')
    print('  - "Create a summary file for resume_john_doe.txt"')
    print('  - "List all PDF files in the resumes directory"')
    print('\nType "quit" or "exit" to end the session.\n')

    conversation_history = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit"):
            print("\nGoodbye!")
            break

        print("\nAssistant: ", end="")
        try:
            response = chat(user_input, conversation_history)
            print(response)
        except Exception as e:
            print(f"Error: {str(e)}")
            # Remove the failed user message from history
            if conversation_history and conversation_history[-1]["role"] == "user":
                conversation_history.pop()

        print()


if __name__ == "__main__":
    main()
