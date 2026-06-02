"""
demo.py — Command-line demo for the AI Code Reviewer.

Run:
    python demo.py

The script reads GROQ_API_KEY from the environment (or prompts for one),
then runs a full code review on a sample Python file that intentionally
contains bugs, security issues, and performance problems.  The review
output is printed to the terminal so you can see exactly what the
application produces without launching the Streamlit UI.
"""

import os
import sys
import textwrap

# Load .env when running locally so GROQ_API_KEY is available automatically.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from langchain_groq import ChatGroq
except ImportError:
    print("ERROR: langchain-groq is not installed.  Run: pip install -r requirements.txt")
    sys.exit(1)


SAMPLE_CODE = '''
def authenticate_user(username, password):
    """Check user credentials against a hardcoded password."""
    if password == "admin123":
        return {"user": username, "role": "admin", "token": "abc123"}
    else:
        return {"user": username, "role": "standard", "token": "xyz789"}


def read_config(filename):
    """Read a configuration file and return its contents."""
    f = open(filename, "r")
    data = f.read()
    return data


def process_items(items):
    """Return a deduplicated version of the input list."""
    results = []
    for i in range(len(items)):
        item = items[i]
        if item not in results:
            results.append(item)
    return results


def get_user_data(user_id):
    """Fetch user records from the database by ID."""
    import sqlite3
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return cursor.fetchall()
'''

REVIEW_PROMPT = """You are a senior software engineer. Review this Python code thoroughly.

```python
{code}
```

Respond EXACTLY in this format:

OVERALL_SCORE: [1-10]

SUMMARY:
[2-3 sentence assessment]

BUGS:
- LINE [N]: [bug description] | FIX: [fix]
[or write "None found"]

SECURITY:
- [security issue] | FIX: [fix]
[or write "None found"]

PERFORMANCE:
- LINE [N]: [performance issue] | FIX: [improvement]
[or write "None found"]

STYLE:
- [style issue] | FIX: [suggestion]
[or write "Follows best practices"]

STRENGTHS:
- [strength 1]
- [strength 2]

IMPROVED_CODE:
```python
[complete improved version with all fixes applied]
```"""


def get_api_key() -> str:
    """Return the Groq API key from the environment or prompt the user."""
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if not key:
        key = input("Enter your Groq API key (gsk_...): ").strip()
    if not key:
        print("ERROR: No API key provided.  Set GROQ_API_KEY or enter it when prompted.")
        sys.exit(1)
    return key


def parse_score(text: str) -> int:
    """Extract the overall score from the LLM response."""
    import re
    for line in text.split("\n"):
        if "OVERALL_SCORE:" in line:
            match = re.search(r"\d+", line.split("OVERALL_SCORE:")[-1])
            if match:
                return max(1, min(10, int(match.group())))
    return 7


def parse_section(text: str, section: str) -> list:
    """Extract bullet items for a given section header."""
    items = []
    in_section = False
    headers = {
        "BUGS:", "SECURITY:", "PERFORMANCE:", "STYLE:",
        "STRENGTHS:", "IMPROVED_CODE:", "SUMMARY:", "OVERALL_SCORE:",
    }
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped == section:
            in_section = True
            continue
        if in_section:
            if stripped in headers:
                break
            if stripped.startswith("-"):
                items.append(stripped[1:].strip())
    return [
        i for i in items
        if i
        and "none found" not in i.lower()
        and "follows best" not in i.lower()
    ]


def parse_improved_code(text: str) -> str:
    """Extract the improved code block from the LLM response."""
    if "IMPROVED_CODE:" not in text:
        return ""
    part = text.split("IMPROVED_CODE:")[-1]
    if "```python" not in part:
        return ""
    inner = part.split("```python")[-1]
    if "```" not in inner:
        return ""
    return inner.split("```")[0].strip()


def print_separator(char: str = "-", width: int = 70) -> None:
    print(char * width)


def run_demo() -> None:
    print_separator("=")
    print("  AI Code Reviewer — Command-Line Demo")
    print_separator("=")
    print()

    api_key = get_api_key()

    print("Initialising Groq LLM (llama3-8b-8192)...")
    llm = ChatGroq(
        model="llama3-8b-8192",
        temperature=0,
        groq_api_key=api_key,
        max_tokens=2000,
    )

    print()
    print("Sample code being reviewed:")
    print_separator()
    print(SAMPLE_CODE.strip())
    print_separator()
    print()

    print("Sending code to Groq for review — please wait...")
    try:
        response = llm.invoke(REVIEW_PROMPT.format(code=SAMPLE_CODE))
        raw = response.content
    except Exception as exc:
        print(f"ERROR: LLM call failed — {exc}")
        sys.exit(1)

    score = parse_score(raw)
    bugs = parse_section(raw, "BUGS:")
    security = parse_section(raw, "SECURITY:")
    perf = parse_section(raw, "PERFORMANCE:")
    style = parse_section(raw, "STYLE:")
    strengths = parse_section(raw, "STRENGTHS:")
    improved = parse_improved_code(raw)

    print()
    print_separator("=")
    print(f"  OVERALL QUALITY SCORE: {score}/10")
    print_separator("=")
    print()

    def print_items(title: str, items: list, prefix: str = "  *") -> None:
        print(f"{title}")
        print_separator()
        if items:
            for item in items:
                wrapped = textwrap.fill(item, width=68, subsequent_indent="      ")
                print(f"{prefix} {wrapped}")
        else:
            print("  None found.")
        print()

    print_items("BUGS DETECTED", bugs)
    print_items("SECURITY ISSUES", security)
    print_items("PERFORMANCE ISSUES", perf)
    print_items("STYLE ISSUES", style)
    print_items("STRENGTHS", strengths)

    if improved:
        print("IMPROVED CODE")
        print_separator()
        print(improved)
        print()

        out_path = "improved_code.py"
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(improved)
        print(f"Improved code saved to: {out_path}")
    else:
        print("Improved code block was not returned by the model.")

    print()
    print_separator("=")
    print("  Demo complete.  Run `streamlit run app.py` for the full UI.")
    print_separator("=")


if __name__ == "__main__":
    run_demo()
