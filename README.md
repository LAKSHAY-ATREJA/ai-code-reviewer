# AI Code Reviewer

A Streamlit web application that performs automated code review, security analysis, unit test generation, and plain-English explanation of Python code using a large language model hosted on Groq.

---

## What This Project Does

AI Code Reviewer accepts raw Python code as input and sends it to the Groq API (Llama 3 8B) to produce a structured analysis. The analysis is then parsed and displayed in a clean, colour-coded UI with downloadable artefacts.

There are three review modes available through the interface:

- **Review** — produces a quality score from 1 to 10, a written summary, a list of bugs with line numbers and suggested fixes, a list of security vulnerabilities with fixes, performance issues, style observations, code strengths, and a fully improved version of the submitted code.
- **Tests** — generates a complete pytest test file covering happy paths, edge cases, boundary values, and exception handling.
- **Explain** — produces a plain-English breakdown of what the code does, what each function is responsible for, potential issues to watch out for, and concrete improvement suggestions aimed at junior developers.

The sidebar stores a rolling history of recent review scores so you can track quality across multiple submissions in a session.

---

## Features

- Quality score (1-10) with colour-coded badge (green above 8, amber above 6, red below 6)
- Bug detection with line-number attribution and fix suggestions
- Security analysis covering SQL injection, hardcoded credentials, unsafe file handling, and similar patterns
- Performance review flagging inefficient loops, unclosed resources, and slow patterns
- Automatic generation of an improved version of the submitted code
- One-click download of the improved code or the generated test file
- Review history panel showing the last five reviews with score and issue counts
- Command-line demo script that runs a full review without the web UI
- Deployable for free on both Render and Streamlit Cloud

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web interface | Streamlit |
| LLM provider | Groq (Llama 3 8B — llama3-8b-8192) |
| LLM client | LangChain + langchain-groq |
| Env management | python-dotenv |

---

## Installation

Requirements: Python 3.9 or higher.

```bash
git clone https://github.com/LAKSHAY-ATREJA/ai-code-reviewer
cd ai-code-reviewer

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

---

## Environment Variables

The application needs one environment variable:

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Your Groq API key (starts with `gsk_`) |

Obtain a free key by creating an account at [console.groq.com](https://console.groq.com). Groq's free tier provides generous rate limits suitable for development and demonstration use.

Copy `.env.example` to `.env` and fill in your key:

```bash
cp .env.example .env
# edit .env and set GROQ_API_KEY=gsk_your_actual_key
```

The app loads `.env` automatically on startup. If the variable is not set, the sidebar prompts you to paste the key directly.

---

## Running Locally

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501` in your default browser.

To use the example code built into the app, click "Load Example Code" in the sidebar. The example contains a deliberately flawed Python file with a hardcoded password, an unclosed file handle, an inefficient deduplication loop, and an SQL injection vulnerability — a good baseline for seeing what the reviewer catches.

---

## Running the Command-Line Demo

`demo.py` runs a full review on a sample Python file and prints the results to the terminal without launching the web interface. This is useful for CI pipelines, quick checks, or verifying that your API key is working.

```bash
python3 demo.py
```

If `GROQ_API_KEY` is set in your environment or `.env`, it is picked up automatically. Otherwise the script prompts you to enter the key interactively.

The demo reviews a sample file that contains the following intentional problems:

- Hardcoded credentials (`password == "admin123"`, static token strings)
- Unclosed file handle in `read_config`
- Inefficient deduplication using `range(len(...))` and `list.append` instead of a set
- SQL injection via f-string query construction in `get_user_data`

After printing the review, the demo writes the improved version of the code to `improved_code.py` in the current directory.

---

## Example Output

Running the demo against the sample file produces output similar to the following (exact wording varies by model response):

```
======================================================================
  AI Code Reviewer — Command-Line Demo
======================================================================

Sample code being reviewed:
----------------------------------------------------------------------
def authenticate_user(username, password):
    if password == "admin123":
        return {"user": username, "role": "admin", "token": "abc123"}
    ...
----------------------------------------------------------------------

Sending code to Groq for review — please wait...

======================================================================
  OVERALL QUALITY SCORE: 3/10
======================================================================

BUGS DETECTED
----------------------------------------------------------------------
  * LINE 3: Function always returns a token regardless of whether
      authentication succeeded; there is no failure path. | FIX:
      Return None or raise an exception when credentials are invalid.

SECURITY ISSUES
----------------------------------------------------------------------
  * Hardcoded password "admin123" and static token strings expose
      credentials in source code. | FIX: Use environment variables
      and a proper token-generation library such as secrets or JWT.
  * SQL query built with f-string interpolation is vulnerable to SQL
      injection. | FIX: Use parameterised queries:
      cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

PERFORMANCE ISSUES
----------------------------------------------------------------------
  * LINE 44: Iterating with range(len(items)) and checking membership
      in a list on every iteration is O(n^2). | FIX: Use
      list(dict.fromkeys(items)) or return list(set(items)).

STRENGTHS
----------------------------------------------------------------------
  * Functions are short and single-purpose.
  * Docstrings are present on all functions.

IMPROVED CODE
----------------------------------------------------------------------
...
```

---

## Deployment

### Streamlit Cloud (recommended for quick sharing)

1. Fork this repository on GitHub.
2. Visit [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click "New app", select the forked repo, set the main file to `app.py`, and click Deploy.
4. In the app settings under "Secrets", add `GROQ_API_KEY = "gsk_..."`.

### Render (free tier)

The repository includes a `render.yaml` that configures a free-tier web service automatically.

1. Create a free account at [render.com](https://render.com).
2. Click "New" → "Blueprint" and connect the GitHub repository.
3. Render detects `render.yaml` and configures the service.
4. In the service environment settings, set `GROQ_API_KEY` to your key.
5. Click "Apply" — the service builds and deploys automatically.

The `Procfile` at the root of the repository is also present for platforms such as Heroku that use it directly:

```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

---

## Repository Structure

```
ai-code-reviewer/
├── app.py              Main Streamlit application
├── demo.py             Command-line demo script
├── requirements.txt    Python dependencies
├── .env.example        Template for environment variables
├── Procfile            Process declaration for Heroku-style platforms
├── render.yaml         Render deployment blueprint
└── README.md           This file
```

---

## About

Built by [Lakshay Atreja](https://linkedin.com/in/lakshay-atreja).
Source code on [GitHub](https://github.com/LAKSHAY-ATREJA/ai-code-reviewer).
