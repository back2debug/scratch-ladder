"""
Lesson generator — calls Claude API and produces structured lesson JSON.
Usage: python src/generate.py --topic "for loops" --level beginner
       python src/generate.py --topic "variables" --game-world "dungeon crawler"
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv
    # Load .env from the repo root (parent of src/) so ANTHROPIC_API_KEY
    # is picked up automatically — no `export` needed.
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

import anthropic

LEVELS = ["absolute beginner", "beginner", "intermediate"]

GAME_WORLDS = [
    "a dungeon crawler RPG (think Minecraft Dungeons)",
    "a space shooter game (think Galaga or Asteroids)",
    "a Pokemon-style monster battler",
    "a platformer game (think Mario or Celeste)",
    "a survival crafting game (think Minecraft or Terraria)",
    "a tower defense game",
    "a retro arcade game (think Pac-Man or Space Invaders)",
    "a fantasy RPG (think Zelda or Stardew Valley)",
]

SYSTEM_PROMPT = """You are a game developer and coding mentor teaching a kid who loves games and is transitioning from Scratch to Python.

Your mission: make every single lesson feel like building a real game, not doing homework.

Rules you NEVER break:
- Every concept is explained using a game analogy first (variables = player stats, loops = game loops, functions = special moves, lists = inventory)
- Every exercise is a piece of a real game — the student should feel like a game dev, not a student
- Every exercise must produce satisfying ASCII art output when it runs — health bars, maps, battle results, scoreboards
- Always bridge from Scratch: mention what the equivalent Scratch block would be, then show how Python does the same thing
- Zero jargon. If you must use a technical word, immediately explain it in game terms.
- Be hype. Celebrate small wins. Make them feel like a real programmer.
- Always respond with valid JSON only — no markdown fences, no preamble, just the raw JSON object."""


def build_user_prompt(topic: str, level: str, game_world: str) -> str:
    return f"""Create a complete game-themed Python lesson for a {level} student transitioning from Scratch.
Topic: {topic}
Game world for this lesson: {game_world}

The student knows Scratch already. Bridge every concept to Scratch blocks they already know.
Every exercise must print ASCII art output — health bars, maps, stats screens, battle results.

Return a JSON object with exactly this structure:
{{
  "topic": "{topic}",
  "level": "{level}",
  "game_world": "{game_world}",
  "title": "A game-themed lesson title (e.g. 'Level Up: Variables are Your Player Stats')",
  "tagline": "One hype sentence mentioning the game world that makes a kid excited",
  "scratch_bridge": "In 2 sentences: what did they do in Scratch that is similar? What Scratch block does this replace?",
  "concept": {{
    "plain_english": "Explain in 3-4 sentences using game examples and zero jargon.",
    "why_it_matters": "One sentence: what game feature becomes possible once you know this?",
    "analogy": "A game-specific analogy (e.g. 'a variable is like a player stat')"
  }},
  "code_example": {{
    "title": "A game-themed filename (e.g. 'battle_setup.py')",
    "code": "A short Python example (8-15 lines) set in the game world. Must print ASCII output.",
    "explanation": "Walk through line by line. Reference Scratch equivalents. Be hype.",
    "sample_output": "Exactly what gets printed when the code runs including the ASCII art"
  }},
  "exercises": [
    {{
      "number": 1,
      "difficulty": "easy",
      "game_context": "One sentence: what part of the game are they building right now?",
      "title": "Game-themed exercise title",
      "instructions": "Step by step framed as game dev work. End with what the output should look like.",
      "expected_output": "The exact ASCII output they should see when it works",
      "starter_code": "# game-themed starter code with variables named after game concepts",
      "hint": "A hint framed as game dev advice",
      "scratch_equivalent": "One sentence: what Scratch blocks did something similar?"
    }},
    {{
      "number": 2,
      "difficulty": "medium",
      "game_context": "One sentence: what part of the game are they building?",
      "title": "Game-themed exercise title",
      "instructions": "Step by step framed as game dev work.",
      "expected_output": "The exact ASCII output they should see",
      "starter_code": "# starter code",
      "hint": "A hint framed as game dev advice",
      "scratch_equivalent": "One sentence: what Scratch blocks did something similar?"
    }}
  ],
  "quiz": [
    {{
      "number": 1,
      "question": "Game-scenario question (e.g. 'Your player has 50 HP. You store this as...')",
      "options": ["A) option", "B) option", "C) option", "D) option"],
      "answer": "A",
      "explanation": "Why this is right, explained in game terms"
    }},
    {{"number": 2, "question": "Game-scenario question", "options": ["A) option", "B) option", "C) option", "D) option"], "answer": "B", "explanation": "Game-terms explanation"}},
    {{"number": 3, "question": "Game-scenario question", "options": ["A) option", "B) option", "C) option", "D) option"], "answer": "C", "explanation": "Game-terms explanation"}}
  ],
  "challenge": {{
    "title": "A mini game project title that sounds like a real game feature",
    "game_context": "What game are they building a piece of?",
    "description": "Build a specific game feature using everything from this lesson. Must produce impressive ASCII output.",
    "example_output": "The full ASCII output when the challenge is complete — make it look awesome"
  }},
  "encouragement": "End hype — tell them what real game they could start building with this skill"
}}"""


def generate_lesson(topic: str, level: str, game_world: str) -> dict:
    client = anthropic.Anthropic()
    print(f"  Calling Claude API for: {topic} ({level})")
    print(f"  Game world: {game_world}")
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_prompt(topic, level, game_world)}]
    )
    raw = response.content[0].text.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    lesson = json.loads(raw)
    lesson["generated_at"] = datetime.now().isoformat()
    return lesson


def save_lesson(lesson: dict, output_dir: Path) -> Path:
    slug = lesson["topic"].lower().replace(" ", "-").replace("_", "-")
    path = output_dir / f"{slug}.json"
    path.write_text(json.dumps(lesson, indent=2))
    print(f"  Saved: {path}")
    return path


def pick_game_world(topic: str) -> str:
    # Stable per-topic so re-generating the same topic uses the same world.
    digest = int(hashlib.sha256(topic.encode()).hexdigest(), 16)
    return GAME_WORLDS[digest % len(GAME_WORLDS)]


def main():
    parser = argparse.ArgumentParser(description="Generate a game-themed Python lesson for a beginner")
    parser.add_argument("--topic", required=True, help='e.g. "for loops"')
    parser.add_argument("--level", default="beginner", choices=LEVELS)
    parser.add_argument("--game-world", default=None,
                        help='Override game world (e.g. "dungeon crawler"). Defaults to auto-pick by topic.')
    parser.add_argument("--out", default="lessons")
    args = parser.parse_args()

    game_world = args.game_world or pick_game_world(args.topic)
    out_dir = Path(args.out)
    out_dir.mkdir(exist_ok=True)

    print(f"\n Generating lesson: {args.topic}")
    try:
        lesson = generate_lesson(args.topic, args.level, game_world)
        path = save_lesson(lesson, out_dir)
        print(f"\n Done! Lesson saved to {path}")
        print(f"   Title: {lesson['title']}")
        print(f"   Exercises: {len(lesson['exercises'])}, Quiz: {len(lesson['quiz'])} questions")
    except json.JSONDecodeError as e:
        print(f" JSON parse error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f" Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
