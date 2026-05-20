# 🐍 Scratch Ladder

An AI-powered coding curriculum generator for kids climbing from Scratch up into Python — built with the Claude API. Give it a topic, get a complete game-themed lesson with explanations, exercises, a quiz, and a mini-project challenge.

**[→ View the live curriculum](https://back2debug.github.io/scratch-ladder)**

![Tests](https://github.com/back2debug/scratch-ladder/actions/workflows/build.yml/badge.svg)

---

## What it does

1. You run `make lesson TOPIC="for loops"` locally
2. Claude generates a complete structured lesson (concept, code example, 2 exercises, 3-question quiz, challenge)
3. The lesson is saved as JSON and rendered into a polished HTML page
4. Push to GitHub → Actions runs tests → deploys to GitHub Pages automatically

## Quick start

```bash
git clone https://github.com/back2debug/scratch-ladder
cd scratch-ladder
pip install -r requirements.txt

# Add your API key — copy the template, then edit .env and paste your key in.
cp .env.example .env
# (open .env in your editor and replace the placeholder with your real key)

# Generate your first lesson
make lesson TOPIC="variables"

# Open it locally
make open
```

## Usage

```bash
# Generate a lesson (renders automatically)
make lesson TOPIC="for loops"
make lesson TOPIC="functions" LEVEL="intermediate"

# Just re-render existing lessons (no API call)
make render

# See all generated lessons
make list
```

## Running tests

```bash
# Full suite (verbose)
make test

# With coverage report
make coverage

# Or run pytest directly
pytest tests/ -v
pytest tests/test_lesson.py::TestHtmlInjection -v   # one class
```

The suite covers the prompt builder, the JSON renderer, lesson schema validation,
and a set of security checks (HTML escaping, slug path-traversal hardening,
filename containment).

## Project structure

```
scratch-ladder/
├── src/
│   ├── generate.py      # Claude API call → structured lesson JSON
│   └── render.py        # JSON → HTML pages
├── lessons/             # Generated lesson JSON (committed to repo)
├── site/                # Generated HTML (deployed to GitHub Pages)
│   ├── index.html       # Curriculum overview
│   └── lessons/         # Individual lesson pages
├── tests/
│   └── test_lesson.py   # pytest suite
├── .github/workflows/
│   └── build.yml        # CI/CD → GitHub Pages
└── Makefile             # make lesson, make test, make render
```

## Lesson structure

Each generated lesson includes:
- **Concept explanation** — plain english, no jargon, with an analogy
- **Code example** — annotated, beginner-friendly
- **2 exercises** — easy / medium with hints
- **3-question quiz** — interactive, with explanations
- **Mini challenge** — a small creative project to apply the lesson

## Tech stack

| Layer | Tool |
|---|---|
| AI generation | [Anthropic Claude API](https://docs.anthropic.com) (`claude-sonnet-4-6`) |
| Structured output | Prompted JSON schema |
| HTML rendering | Python stdlib (f-strings + `html.escape`) |
| Testing | pytest + pytest-cov |
| CI/CD | GitHub Actions |
| Hosting | GitHub Pages |
| CLI | argparse + Makefile |

## GitHub Pages setup

1. Go to **Settings → Pages** in your repo
2. Set source to **GitHub Actions**
3. Push a commit — the workflow handles the rest

## Environment variables

Local runs load values from a `.env` file in the repo root (via `python-dotenv`).
Copy `.env.example` to `.env` and fill it in — `.env` is gitignored, so your key
never gets committed. In CI, set the same names as repo secrets.

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key ([get one here](https://console.anthropic.com)) |

---

Built as a portfolio project demonstrating agentic API usage, structured prompting, and CI/CD automation.
