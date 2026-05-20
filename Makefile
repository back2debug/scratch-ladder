.PHONY: lesson render test install clean

# Pick python3 / pip3 explicitly — on many systems `python` still points at Python 2,
# which chokes on the non-ASCII characters in our source files.
PYTHON ?= python3
PIP ?= pip3

# Generate a lesson: make lesson TOPIC="for loops" LEVEL=beginner
lesson:
	@$(PYTHON) src/generate.py --topic "$(TOPIC)" --level $(or $(LEVEL),beginner)
	@$(MAKE) render

# Re-render all lessons to site/
render:
	@$(PYTHON) src/render.py

# Run tests
test:
	@$(PYTHON) -m pytest tests/ -v --tb=short

# Run tests with coverage
coverage:
	@$(PYTHON) -m pytest tests/ -v --cov=src --cov-report=term-missing

# Install dependencies
install:
	@$(PIP) install -r requirements.txt

# Open the local site in browser (macOS / Linux)
open:
	@open site/index.html 2>/dev/null || xdg-open site/index.html 2>/dev/null || echo "Open site/index.html in your browser"

# Remove generated site files
clean:
	@rm -rf site/lessons/*.html site/index.html
	@echo "Cleaned site output"

# Show available lessons
list:
	@ls lessons/*.json 2>/dev/null | sed 's/lessons\///' | sed 's/\.json//' || echo "No lessons generated yet"
