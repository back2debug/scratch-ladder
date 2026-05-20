"""
Tests for lesson generator and renderer.
Run: pytest tests/ -v
"""

import json
import pytest
from pathlib import Path
import sys

_HERE = Path(__file__).resolve().parent
for candidate in (_HERE, _HERE.parent / "src", _HERE / "src"):
    if (candidate / "generate.py").exists() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))
        break

from generate import build_user_prompt, LEVELS
from render import slug, difficulty_emoji, render_index_html, render_lesson_html, e


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_lesson():
    return {
        "topic": "for loops",
        "level": "beginner",
        "game_world": "a dungeon crawler RPG (think Minecraft Dungeons)",
        "title": "Loop the Loop: Spawn Enemies with For Loops",
        "tagline": "Use for loops to fill your dungeon with monsters — just like a real game engine!",
        "generated_at": "2026-01-01T00:00:00",
        "scratch_bridge": "In Scratch you used the 'repeat' block to do something multiple times. In Python, the for loop is your repeat block — just written as code instead of a puzzle piece.",
        "concept": {
            "plain_english": "A for loop lets you repeat code a set number of times.",
            "why_it_matters": "Without loops you'd have to copy-paste code for every enemy, every coin, every tile.",
            "analogy": "A for loop is like telling your game to spawn 10 enemies one at a time — same action, repeated."
        },
        "code_example": {
            "title": "spawn_enemies.py",
            "code": "for i in range(5):\n    print(f'Enemy {i+1} spawned! 👾')",
            "explanation": "range(5) gives us numbers 0 through 4 — like 5 enemy spawn slots. Each loop, i gets the next number.",
            "sample_output": "Enemy 1 spawned! 👾\nEnemy 2 spawned! 👾\nEnemy 3 spawned! 👾\nEnemy 4 spawned! 👾\nEnemy 5 spawned! 👾"
        },
        "exercises": [
            {
                "number": 1,
                "difficulty": "easy",
                "game_context": "You are setting up the spawn counter before the dungeon level begins.",
                "title": "Enemy Spawn Counter",
                "instructions": "Print a countdown from 5 to 1 before the dungeon opens.",
                "expected_output": "5...\n4...\n3...\n2...\n1...\nDungeon unlocked! ⚔️",
                "starter_code": "for i in range(?, ?, ?):\n    print(f'{i}...')",
                "hint": "range(5, 0, -1) counts down from 5 to 1.",
                "scratch_equivalent": "In Scratch this is a 'repeat 5' block counting a variable down."
            },
            {
                "number": 2,
                "difficulty": "medium",
                "game_context": "You are building a loot drop system that collects coins in a row.",
                "title": "Coin Collector",
                "instructions": "Print a row of coins and tally them up.",
                "expected_output": "💰💰💰💰💰\nTotal coins: 5",
                "starter_code": "coins = 0\nfor i in range(5):\n    coins = coins + ?\nprint('💰' * 5)\nprint(f'Total coins: {coins}')",
                "hint": "Each loop adds 1 to the coins counter — just like collecting one coin at a time.",
                "scratch_equivalent": "In Scratch this is 'change coins by 1' inside a repeat block."
            }
        ],
        "quiz": [
            {
                "number": 1,
                "question": "What does range(3) produce?",
                "options": ["A) 1, 2, 3", "B) 0, 1, 2", "C) 0, 1, 2, 3", "D) 1, 2"],
                "answer": "B",
                "explanation": "range(3) produces 0, 1, 2 — starts at 0, stops before 3. Like spawn slots 0, 1, 2."
            }
        ],
        "challenge": {
            "title": "Dungeon Room Generator",
            "game_context": "Building the level generator for a text-based dungeon crawler.",
            "description": "Generate a 5x5 dungeon room using nested for loops. Fill it with walls (#) on the edges and floor (.) in the middle.",
            "example_output": "#####\n#...#\n#...#\n#...#\n#####"
        },
        "encouragement": "You just used the same loop pattern that every real game engine uses to spawn enemies, render tiles, and process game objects. You're building like a real dev now!"
    }


# ── generate.py tests ────────────────────────────────────────────────────────

class TestPromptBuilder:
    def test_prompt_contains_topic(self):
        prompt = build_user_prompt("variables", "beginner", "dungeon crawler")
        assert "variables" in prompt

    def test_prompt_contains_level(self):
        prompt = build_user_prompt("functions", "beginner", "space shooter")
        assert "beginner" in prompt

    def test_prompt_contains_game_world(self):
        prompt = build_user_prompt("loops", "beginner", "Pokemon-style monster battler")
        assert "Pokemon" in prompt

    def test_prompt_requests_json(self):
        prompt = build_user_prompt("loops", "beginner", "dungeon crawler")
        assert "JSON" in prompt or "json" in prompt

    def test_all_levels_are_valid(self):
        for level in LEVELS:
            prompt = build_user_prompt("test topic", level, "dungeon crawler")
            assert level in prompt

    def test_prompt_specifies_exercises(self):
        prompt = build_user_prompt("strings", "beginner", "dungeon crawler")
        assert "exercises" in prompt.lower()

    def test_prompt_specifies_quiz(self):
        prompt = build_user_prompt("strings", "beginner", "dungeon crawler")
        assert "quiz" in prompt.lower()

    def test_prompt_mentions_scratch(self):
        prompt = build_user_prompt("variables", "beginner", "dungeon crawler")
        assert "Scratch" in prompt

    def test_prompt_mentions_ascii(self):
        prompt = build_user_prompt("variables", "beginner", "dungeon crawler")
        assert "ASCII" in prompt

    def test_prompt_does_not_mention_week(self):
        prompt = build_user_prompt("variables", "beginner", "dungeon crawler")
        assert "week" not in prompt.lower()


# ── render.py tests ──────────────────────────────────────────────────────────

class TestSlugFunction:
    def test_spaces_become_hyphens(self):
        assert slug("for loops") == "for-loops"

    def test_underscores_become_hyphens(self):
        assert slug("for_loops") == "for-loops"

    def test_lowercase(self):
        assert slug("Variables") == "variables"

    def test_multi_word(self):
        assert slug("if else statements") == "if-else-statements"


class TestDifficultyEmoji:
    def test_easy_is_green(self):
        assert difficulty_emoji("easy") == "🟢"

    def test_medium_is_yellow(self):
        assert difficulty_emoji("medium") == "🟡"

    def test_hard_is_red(self):
        assert difficulty_emoji("hard") == "🔴"

    def test_unknown_returns_default(self):
        result = difficulty_emoji("expert")
        assert result == "⚪"


class TestIndexRenderer:
    def test_empty_lessons_renders(self):
        html = render_index_html([])
        assert "No lessons yet" in html

    def test_lesson_count_shown(self, sample_lesson):
        html = render_index_html([sample_lesson])
        assert "<strong>1</strong> lesson" in html

    def test_plural_for_multiple(self, sample_lesson):
        html = render_index_html([sample_lesson, {**sample_lesson, "topic": "variables", "title": "Variables"}])
        assert "<strong>2</strong> lessons" in html

    def test_lesson_title_in_index(self, sample_lesson):
        html = render_index_html([sample_lesson])
        assert sample_lesson["title"] in html

    def test_no_week_label_in_index(self, sample_lesson):
        html = render_index_html([sample_lesson])
        assert "Week" not in html

    def test_no_week_label_in_lesson_page(self, sample_lesson):
        html = render_lesson_html(sample_lesson)
        assert "Week" not in html


class TestLessonStructureValidation:
    """Validate that lesson JSON has all required fields."""

    REQUIRED_TOP_LEVEL = ["topic", "level", "game_world", "title", "scratch_bridge", "concept", "code_example", "exercises", "quiz", "challenge"]
    REQUIRED_CONCEPT = ["plain_english", "why_it_matters", "analogy"]
    REQUIRED_CODE = ["title", "code", "explanation", "sample_output"]
    REQUIRED_EXERCISE = ["number", "difficulty", "game_context", "title", "instructions", "expected_output", "hint", "scratch_equivalent"]
    REQUIRED_QUIZ = ["number", "question", "options", "answer", "explanation"]
    REQUIRED_CHALLENGE = ["title", "game_context", "description", "example_output"]

    def test_top_level_fields(self, sample_lesson):
        for field in self.REQUIRED_TOP_LEVEL:
            assert field in sample_lesson, f"Missing top-level field: {field}"

    def test_concept_fields(self, sample_lesson):
        for field in self.REQUIRED_CONCEPT:
            assert field in sample_lesson["concept"], f"Missing concept field: {field}"

    def test_code_example_fields(self, sample_lesson):
        for field in self.REQUIRED_CODE:
            assert field in sample_lesson["code_example"], f"Missing code_example field: {field}"

    def test_has_two_exercises(self, sample_lesson):
        assert len(sample_lesson["exercises"]) == 2

    def test_exercise_difficulties(self, sample_lesson):
        difficulties = [ex["difficulty"] for ex in sample_lesson["exercises"]]
        assert "easy" in difficulties
        assert "medium" in difficulties
        assert "hard" not in difficulties

    def test_exercise_fields(self, sample_lesson):
        for ex in sample_lesson["exercises"]:
            for field in self.REQUIRED_EXERCISE:
                assert field in ex, f"Exercise missing field: {field}"

    def test_quiz_fields(self, sample_lesson):
        for q in sample_lesson["quiz"]:
            for field in self.REQUIRED_QUIZ:
                assert field in q, f"Quiz question missing field: {field}"

    def test_quiz_options_count(self, sample_lesson):
        for q in sample_lesson["quiz"]:
            assert len(q["options"]) == 4, "Each quiz question should have 4 options"

    def test_quiz_answer_is_valid_letter(self, sample_lesson):
        for q in sample_lesson["quiz"]:
            assert q["answer"] in ["A", "B", "C", "D"]

    def test_challenge_fields(self, sample_lesson):
        for field in self.REQUIRED_CHALLENGE:
            assert field in sample_lesson["challenge"], f"Challenge missing field: {field}"


# ── Security tests ───────────────────────────────────────────────────────────

class TestSlugSafety:
    """Slug must not allow path traversal or filesystem-special characters."""

    def test_parent_dir_neutralized(self):
        assert "/" not in slug("../../etc/passwd")
        assert ".." not in slug("../../etc/passwd")

    def test_path_separator_stripped(self):
        out = slug("a/b\\c")
        assert "/" not in out and "\\" not in out

    def test_null_byte_stripped(self):
        assert "\x00" not in slug("foo\x00bar")

    def test_only_safe_chars(self):
        out = slug("Hello, World! @#$%")
        assert all(c.isalnum() or c == "-" for c in out)

    def test_empty_returns_fallback(self):
        assert slug("") == "lesson"
        assert slug("///") == "lesson"

    def test_unicode_stripped(self):
        # Non-ASCII letters are not in our safe charset — they're collapsed.
        out = slug("héllo")
        assert all(c.isalnum() or c == "-" for c in out)


class TestEscapeHelper:
    def test_escapes_angle_brackets(self):
        assert e("<script>") == "&lt;script&gt;"

    def test_escapes_quotes(self):
        # html.escape with quote=True escapes both " and '
        out = e('"hi"')
        assert '"' not in out
        assert "&quot;" in out

    def test_escapes_ampersand(self):
        assert e("a & b") == "a &amp; b"

    def test_none_becomes_empty(self):
        assert e(None) == ""

    def test_non_string_coerced(self):
        assert e(42) == "42"


class TestHtmlInjection:
    """Lesson content must not be able to inject HTML/JS into the rendered page."""

    def _mk_lesson(self, payload: str) -> dict:
        return {
            "topic": "loops", "level": "beginner",
            "title": payload, "tagline": payload,
            "scratch_bridge": payload,
            "concept": {"plain_english": payload, "why_it_matters": payload, "analogy": payload},
            "code_example": {"title": "x.py", "code": payload, "explanation": payload, "sample_output": payload},
            "exercises": [{
                "number": 1, "difficulty": "easy", "game_context": payload,
                "title": payload, "instructions": payload,
                "expected_output": payload, "starter_code": payload,
                "hint": payload, "scratch_equivalent": payload,
            }],
            "quiz": [{
                "number": 1, "question": payload,
                "options": [f"A) {payload}", "B) b", "C) c", "D) d"],
                "answer": "A", "explanation": payload,
            }],
            "challenge": {"title": payload, "game_context": payload,
                          "description": payload, "example_output": payload},
            "encouragement": payload,
        }

    def test_script_tag_not_executable(self):
        payload = "<script>alert('xss')</script>"
        html_out = render_lesson_html(self._mk_lesson(payload))
        # The raw payload must not appear unescaped anywhere in the document.
        assert payload not in html_out
        assert "&lt;script&gt;" in html_out

    def test_attribute_break_in_quiz_explanation(self):
        # A " in explanation must not escape its containing attribute.
        payload = '" onerror="alert(1)'
        html_out = render_lesson_html(self._mk_lesson(payload))
        assert 'onerror="alert(1)' not in html_out
        assert "&quot;" in html_out

    def test_attribute_break_in_quiz_option(self):
        payload = '"><img src=x onerror=alert(1)>'
        html_out = render_lesson_html(self._mk_lesson(payload))
        assert "<img src=x" not in html_out

    def test_image_onerror_in_concept(self):
        payload = '<img src=x onerror=alert(1)>'
        html_out = render_lesson_html(self._mk_lesson(payload))
        assert payload not in html_out

    def test_ampersand_preserved_as_entity(self):
        payload = "Tom & Jerry"
        html_out = render_lesson_html(self._mk_lesson(payload))
        assert "Tom &amp; Jerry" in html_out

    def test_index_escapes_title(self):
        payload = "<script>alert(1)</script>"
        idx = render_index_html([{
            "topic": "x", "title": payload,
            "level": "beginner",
        }])
        assert payload not in idx
        assert "&lt;script&gt;" in idx


class TestGenerateJsonParsing:
    """generate.py strips markdown fences before json.loads — verify the regex."""

    def test_fence_stripping(self):
        import re as _re
        raw = '```json\n{"a": 1}\n```'
        cleaned = _re.sub(r"^```json\s*", "", raw)
        cleaned = _re.sub(r"\s*```$", "", cleaned)
        assert json.loads(cleaned) == {"a": 1}

    def test_unfenced_json_unchanged(self):
        import re as _re
        raw = '{"a": 1}'
        cleaned = _re.sub(r"^```json\s*", "", raw)
        cleaned = _re.sub(r"\s*```$", "", cleaned)
        assert json.loads(cleaned) == {"a": 1}


class TestRenderFilenameSafety:
    """The path constructed for a lesson HTML file must stay inside site/lessons/."""

    def test_malicious_topic_does_not_escape_dir(self, tmp_path, sample_lesson, monkeypatch):
        import render as render_mod
        evil = dict(sample_lesson)
        evil["topic"] = "../../etc/passwd"

        site = tmp_path / "site"
        lessons = tmp_path / "lessons"
        site_lessons = site / "lessons"
        lessons.mkdir()
        monkeypatch.setattr(render_mod, "SITE_DIR", site)
        monkeypatch.setattr(render_mod, "SITE_LESSONS_DIR", site_lessons)
        monkeypatch.setattr(render_mod, "LESSONS_DIR", lessons)

        (lessons / "evil.json").write_text(json.dumps(evil))

        render_mod.render_all()

        # Every output file must live inside site_lessons.
        for path in site_lessons.rglob("*.html"):
            assert str(path.resolve()).startswith(str(site_lessons.resolve()))
        # And nothing was written outside site/.
        assert not (tmp_path / "etc").exists()
