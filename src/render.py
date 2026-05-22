"""
Renderer — converts lesson JSON files into HTML pages for GitHub Pages.
Usage: python src/render.py
Reads from lessons/*.json, writes to site/lessons/*.html and site/index.html
"""

import html
import json
import re
from pathlib import Path
from datetime import datetime

LESSONS_DIR = Path("lessons")
SITE_DIR = Path("site")
SITE_LESSONS_DIR = SITE_DIR / "lessons"

_SAFE_SLUG = re.compile(r"[^a-z0-9-]+")


def e(s) -> str:
    # Escape & < > " ' for safe interpolation into HTML text and attributes.
    if s is None:
        return ""
    return html.escape(str(s), quote=True)


def slug(topic: str) -> str:
    s = str(topic).lower().replace(" ", "-").replace("_", "-")
    s = _SAFE_SLUG.sub("-", s).strip("-")
    return s or "lesson"


def difficulty_emoji(d: str) -> str:
    return {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(d, "⚪")


def render_lesson_html(lesson: dict) -> str:
    exercises_html = ""
    for ex in lesson.get("exercises", []):
        starter = ex.get("starter_code", "").strip()
        starter_block = f'<pre class="starter-code"><code>{e(starter)}</code></pre>' if starter else ""
        expected = ex.get("expected_output", "").strip()
        expected_block = f'<div class="expected-output-box"><div class="expected-label">🎯 Your output should look like this:</div><pre class="expected-output"><code>{e(expected)}</code></pre></div>' if expected else ""
        scratch_eq = ex.get("scratch_equivalent", "")
        scratch_block = f'<div class="scratch-tag">🐱 In Scratch: {e(scratch_eq)}</div>' if scratch_eq else ""
        game_ctx = ex.get("game_context", "")
        game_ctx_block = f'<p class="game-context">🎮 {e(game_ctx)}</p>' if game_ctx else ""
        difficulty = ex.get("difficulty", "")
        exercises_html += f"""
        <div class="exercise-card" data-number="{e(ex.get('number', ''))}">
          <div class="exercise-header">
            <span class="diff-badge diff-{e(difficulty)}">{difficulty_emoji(difficulty)} {e(difficulty.title() if isinstance(difficulty, str) else difficulty)}</span>
            <h3>Exercise {e(ex.get('number', ''))}: {e(ex.get('title', ''))}</h3>
          </div>
          {game_ctx_block}
          {scratch_block}
          <p class="exercise-instructions">{e(ex.get('instructions', ''))}</p>
          {starter_block}
          {expected_block}
          <details class="hint-box">
            <summary>💡 Need a hint?</summary>
            <p>{e(ex.get('hint', ''))}</p>
          </details>
        </div>"""

    quiz_html = ""
    for q in lesson.get("quiz", []):
        answer = q.get("answer", "")
        options_html = "".join(
            f'<button class="quiz-option" data-answer="{e(answer)}" data-letter="{e(opt[0] if opt else "")}">{e(opt)}</button>'
            for opt in q.get("options", [])
        )
        quiz_html += f"""
        <div class="quiz-question" data-q="{e(q.get('number', ''))}">
          <p class="question-text"><strong>Q{e(q.get('number', ''))}.</strong> {e(q.get('question', ''))}</p>
          <div class="quiz-options">{options_html}</div>
          <div class="quiz-feedback hidden" data-explanation="{e(q.get('explanation', ''))}"></div>
        </div>"""

    code = lesson.get("code_example", {})
    concept = lesson.get("concept", {})
    challenge = lesson.get("challenge", {})

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{e(lesson.get('title', ''))}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #3a3d50;
      --surface: #474a5f;
      --surface2: #555870;
      --accent: #b8acff;
      --accent2: #ffd9a3;
      --green: #a3f0c0;
      --red: #ffb3b3;
      --yellow: #ffd9a3;
      --text: #ffffff;
      --muted: #c8ccdd;
      --border: rgba(184,172,255,0.3);
      --radius: 12px;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Nunito', sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.7;
      min-height: 100vh;
    }}
    .hero {{
      background: linear-gradient(135deg, #474a5f 0%, #443e6a 100%);
      border-bottom: 1px solid var(--border);
      padding: 3rem 2rem 2.5rem;
      text-align: center;
      position: relative;
      overflow: hidden;
    }}
    .hero::before {{
      content: '';
      position: absolute;
      top: -60px; left: 50%;
      transform: translateX(-50%);
      width: 400px; height: 400px;
      background: radial-gradient(circle, rgba(184,172,255,0.25) 0%, transparent 70%);
      pointer-events: none;
    }}
    .hero h1 {{
      font-size: clamp(1.8rem, 4vw, 2.8rem);
      font-weight: 800;
      color: #fff;
      margin-bottom: 0.75rem;
    }}
    .hero .tagline {{
      font-size: 1.05rem;
      color: var(--muted);
      max-width: 520px;
      margin: 0 auto 1.5rem;
    }}
    .meta-pills {{
      display: flex;
      gap: 10px;
      justify-content: center;
      flex-wrap: wrap;
    }}
    .pill {{
      background: var(--surface2);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 4px 12px;
      font-size: 0.8rem;
      color: var(--muted);
    }}
    .container {{
      max-width: 780px;
      margin: 0 auto;
      padding: 2rem 1.5rem 4rem;
    }}
    .section {{
      margin-bottom: 2.5rem;
    }}
    .section-title {{
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--accent);
      margin-bottom: 1rem;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .section-title::after {{
      content: '';
      flex: 1;
      height: 1px;
      background: var(--border);
    }}
    .concept-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1.5rem;
    }}
    .analogy-box {{
      background: rgba(124,106,247,0.08);
      border-left: 3px solid var(--accent);
      border-radius: 0 8px 8px 0;
      padding: 0.75rem 1rem;
      margin-top: 1rem;
      font-style: italic;
      color: var(--muted);
    }}
    .analogy-box strong {{ color: var(--accent); font-style: normal; }}
    .scratch-bridge {{ margin-top: 1rem; background: rgba(93,222,142,0.06); border: 1px dashed rgba(93,222,142,0.3); border-radius: 8px; padding: 0.75rem 1rem; font-size: 0.88rem; color: var(--muted); }}
    .scratch-bridge-label {{ color: #5dde8e; font-weight: 700; font-size: 0.8rem; display: block; margin-bottom: 4px; }}
    .sample-output-box {{ margin-top: 0.75rem; }}
    .code-card {{
      background: #2e3142;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: hidden;
    }}
    .code-header {{
      background: var(--surface2);
      padding: 0.6rem 1rem;
      display: flex;
      align-items: center;
      gap: 8px;
      border-bottom: 1px solid var(--border);
    }}
    .code-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
    .code-dot.r {{ background: #f76a6a; }}
    .code-dot.y {{ background: #f7c66a; }}
    .code-dot.g {{ background: #5dde8e; }}
    .code-label {{ font-family: 'Space Mono', monospace; font-size: 0.7rem; color: var(--muted); margin-left: auto; }}
    pre {{
      padding: 1.25rem 1.5rem;
      overflow-x: auto;
      font-family: 'Space Mono', monospace;
      font-size: 0.82rem;
      line-height: 1.7;
      color: #c8d0f0;
    }}
    .code-explanation {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1.25rem 1.5rem;
      margin-top: 0.75rem;
      color: var(--muted);
      font-size: 0.92rem;
    }}
    .exercise-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1.25rem 1.5rem;
      margin-bottom: 1rem;
    }}
    .exercise-header {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 0.75rem;
      flex-wrap: wrap;
    }}
    .exercise-header h3 {{ font-size: 0.95rem; font-weight: 700; }}
    .diff-badge {{
      font-size: 0.7rem;
      font-weight: 700;
      padding: 2px 10px;
      border-radius: 12px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .diff-easy {{ background: rgba(93,222,142,0.15); color: var(--green); }}
    .diff-medium {{ background: rgba(247,198,106,0.15); color: var(--yellow); }}
    .diff-hard {{ background: rgba(247,106,106,0.15); color: var(--red); }}
    .exercise-instructions {{ color: var(--muted); font-size: 0.9rem; margin-bottom: 0.75rem; }}
    .game-context {{ font-size: 0.82rem; color: var(--accent2); margin-bottom: 0.5rem; font-weight: 600; }}
    .scratch-tag {{ font-size: 0.78rem; color: #5dde8e; background: rgba(93,222,142,0.08); border: 1px dashed rgba(93,222,142,0.25); border-radius: 6px; padding: 4px 10px; margin-bottom: 0.75rem; }}
    .expected-output-box {{ margin: 0.75rem 0; }}
    .expected-label {{ font-size: 0.75rem; color: var(--accent); font-weight: 700; margin-bottom: 4px; }}
    .expected-output {{ background: #2e3d35; border: 1px solid rgba(163,240,192,0.35); border-radius: 8px; padding: 0.75rem 1rem; font-family: 'Space Mono', monospace; font-size: 0.78rem; color: #a3f0c0; margin: 0; }}
    .starter-code {{
      background: #2e3142;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 0.75rem 1rem;
      margin-bottom: 0.75rem;
      font-family: 'Space Mono', monospace;
      font-size: 0.78rem;
      color: #c8d0f0;
    }}
    details.hint-box {{
      border: 1px dashed rgba(124,106,247,0.3);
      border-radius: 8px;
      padding: 0.6rem 1rem;
    }}
    details.hint-box summary {{
      cursor: pointer;
      font-size: 0.85rem;
      color: var(--accent);
      font-weight: 600;
      list-style: none;
    }}
    details.hint-box p {{
      margin-top: 0.5rem;
      font-size: 0.85rem;
      color: var(--muted);
    }}
    .quiz-question {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1.25rem 1.5rem;
      margin-bottom: 1rem;
    }}
    .question-text {{ margin-bottom: 0.75rem; font-size: 0.92rem; }}
    .quiz-options {{ display: flex; flex-direction: column; gap: 8px; }}
    .quiz-option {{
      background: var(--surface2);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 0.6rem 1rem;
      text-align: left;
      color: var(--text);
      font-family: 'Nunito', sans-serif;
      font-size: 0.88rem;
      cursor: pointer;
      transition: border-color 0.15s, background 0.15s;
    }}
    .quiz-option:hover {{ border-color: var(--accent); background: rgba(124,106,247,0.08); }}
    .quiz-option.correct {{ border-color: var(--green); background: rgba(93,222,142,0.1); color: var(--green); }}
    .quiz-option.wrong {{ border-color: var(--red); background: rgba(247,106,106,0.1); color: var(--red); }}
    .quiz-option:disabled {{ cursor: default; }}
    .quiz-feedback {{
      margin-top: 0.75rem;
      font-size: 0.85rem;
      color: var(--muted);
      padding: 0.5rem 0.75rem;
      background: rgba(124,106,247,0.06);
      border-radius: 6px;
      border-left: 2px solid var(--accent);
    }}
    .hidden {{ display: none; }}
    .quiz-score {{
      text-align: center;
      padding: 1.5rem;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      margin-top: 1rem;
      display: none;
    }}
    .quiz-score .score-number {{
      font-size: 3rem;
      font-weight: 800;
      color: var(--accent);
      font-family: 'Space Mono', monospace;
    }}
    .challenge-card {{
      background: linear-gradient(135deg, rgba(124,106,247,0.1), rgba(247,198,106,0.05));
      border: 1px solid rgba(124,106,247,0.3);
      border-radius: var(--radius);
      padding: 1.5rem;
    }}
    .challenge-card h3 {{ font-size: 1.1rem; font-weight: 800; margin-bottom: 0.5rem; color: var(--accent2); }}
    .challenge-card .challenge-desc {{ color: var(--muted); font-size: 0.92rem; margin-bottom: 0.75rem; }}
    .expected-output {{
      background: #2e3142;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 0.75rem 1rem;
      font-family: 'Space Mono', monospace;
      font-size: 0.78rem;
      color: var(--green);
    }}
    .encouragement {{
      text-align: center;
      padding: 2rem;
      color: var(--muted);
      font-size: 0.95rem;
      font-style: italic;
    }}
    .back-link {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      color: var(--muted);
      text-decoration: none;
      font-size: 0.85rem;
      margin-bottom: 1.5rem;
      transition: color 0.15s;
    }}
    .back-link:hover {{ color: var(--accent); }}
    @media (max-width: 600px) {{
      .hero {{ padding: 2rem 1rem 1.5rem; }}
    }}
  </style>
</head>
<body>
  <div class="hero">
    <h1>{e(lesson.get('title', ''))}</h1>
    <p class="tagline">{e(lesson.get('tagline', ''))}</p>
    <div class="meta-pills">
      <span class="pill">📚 {e(str(lesson.get('level', 'beginner')).title())}</span>
      <span class="pill">🐍 Python</span>
    </div>
  </div>

  <div class="container">
    <a href="../index.html" class="back-link">← Back to curriculum</a>

    <div class="section">
      <div class="section-title">The concept</div>
      <div class="concept-card">
        <p>{e(concept.get('plain_english', ''))}</p>
        <p style="margin-top:0.75rem; color: var(--muted); font-size:0.9rem;">{e(concept.get('why_it_matters', ''))}</p>
        <div class="analogy-box"><strong>Think of it like this:</strong> {e(concept.get('analogy', ''))}</div>
      </div>
      {f'<div class="scratch-bridge"><span class="scratch-bridge-label">🐱 Coming from Scratch?</span> {e(lesson["scratch_bridge"])}</div>' if lesson.get("scratch_bridge") else ""}
    </div>

    <div class="section">
      <div class="section-title">See it in action</div>
      <div class="code-card">
        <div class="code-header">
          <span class="code-dot r"></span>
          <span class="code-dot y"></span>
          <span class="code-dot g"></span>
          <span class="code-label">{e(code.get('title', 'example.py'))}</span>
        </div>
        <pre><code>{e(code.get('code', ''))}</code></pre>
      </div>
      <div class="code-explanation">{e(code.get('explanation', ''))}</div>
      {f'<div class="sample-output-box"><div class="expected-label">▶ Output when you run this:</div><pre class="expected-output"><code>{e(code["sample_output"])}</code></pre></div>' if code.get("sample_output") else ""}
    </div>

    <div class="section">
      <div class="section-title">Your turn — exercises</div>
      {exercises_html}
    </div>

    <div class="section">
      <div class="section-title">Quiz time</div>
      <div id="quiz-container">
        {quiz_html}
      </div>
      <div class="quiz-score" id="quiz-score">
        <div class="score-number" id="score-display">0/{len(lesson.get("quiz", []))}</div>
        <p style="color: var(--muted); margin-top: 0.5rem;" id="score-message"></p>
      </div>
    </div>

    <div class="section">
      <div class="section-title">Challenge</div>
      <div class="challenge-card">
        <h3>🚀 {e(challenge.get('title', 'Mini Project'))}</h3>
        {f'<p class="game-context">🎮 {e(challenge["game_context"])}</p>' if challenge.get("game_context") else ""}
        <p class="challenge-desc">{e(challenge.get('description', ''))}</p>
        <div class="expected-label">🎯 When complete, it should look like this:</div>
        <pre class="expected-output"><code>{e(challenge.get('example_output', ''))}</code></pre>
      </div>
    </div>

    <p class="encouragement">✨ {e(lesson.get('encouragement', 'Great work today!'))}</p>
  </div>

  <script>
    let answered = 0;
    let correct = 0;
    const total = document.querySelectorAll('.quiz-question').length;

    document.querySelectorAll('.quiz-option').forEach(btn => {{
      btn.addEventListener('click', function() {{
        const question = this.closest('.quiz-question');
        if (question.dataset.answered) return;
        question.dataset.answered = true;
        answered++;

        const isCorrect = this.dataset.letter === this.dataset.answer;
        if (isCorrect) correct++;

        question.querySelectorAll('.quiz-option').forEach(b => {{
          b.disabled = true;
          if (b.dataset.letter === b.dataset.answer) b.classList.add('correct');
          else if (b === this && !isCorrect) b.classList.add('wrong');
        }});

        const feedback = question.querySelector('.quiz-feedback');
        feedback.textContent = (isCorrect ? '✓ ' : '✗ ') + feedback.dataset.explanation;
        feedback.classList.remove('hidden');

        if (answered === total) {{
          const scoreEl = document.getElementById('quiz-score');
          scoreEl.style.display = 'block';
          document.getElementById('score-display').textContent = correct + '/' + total;
          const msgs = ['Keep going, you got this! 💪', 'Getting there! 🌱', 'Nice work! 🎉', 'Really solid! 🔥', 'Perfect score! You crushed it! 🏆'];
          document.getElementById('score-message').textContent = msgs[Math.min(correct, msgs.length - 1)];
        }}
      }});
    }});
  </script>
</body>
</html>"""


def render_index_html(lessons: list) -> str:
    lesson_cards = ""
    for lesson in sorted(lessons, key=lambda l: l["topic"].lower()):
        s = slug(lesson["topic"])
        lesson_cards += f"""
      <a href="lessons/{e(s)}.html" class="lesson-card">
        <div class="lesson-title">{e(lesson.get('title', ''))}</div>
        <div class="lesson-meta">{e(str(lesson.get('level', 'beginner')).title())}</div>
      </a>"""

    count = len(lessons)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Python for Beginners 🐍</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #3a3d50; --surface: #474a5f; --surface2: #555870;
      --accent: #b8acff; --accent2: #ffd9a3;
      --text: #ffffff; --muted: #c8ccdd;
      --border: rgba(184,172,255,0.3); --radius: 12px;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Nunito', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }}
    .hero {{
      text-align: center; padding: 4rem 2rem 3rem;
      background: linear-gradient(135deg, #474a5f 0%, #443e6a 100%);
      border-bottom: 1px solid var(--border);
    }}
    .hero h1 {{ font-size: clamp(2rem, 5vw, 3.5rem); font-weight: 800; margin-bottom: 0.75rem; }}
    .hero h1 span {{ color: var(--accent); }}
    .hero p {{ color: var(--muted); font-size: 1.05rem; max-width: 480px; margin: 0 auto 1.5rem; }}
    .stat-row {{ display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; }}
    .stat {{ background: var(--surface2); border: 1px solid var(--border); border-radius: 20px; padding: 4px 14px; font-size: 0.82rem; color: var(--muted); }}
    .stat strong {{ color: var(--accent); }}
    .grid {{ max-width: 860px; margin: 3rem auto; padding: 0 1.5rem; display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 14px; }}
    .lesson-card {{
      background: var(--surface); border: 1px solid var(--border);
      border-radius: var(--radius); padding: 1.25rem 1.5rem;
      text-decoration: none; color: var(--text);
      transition: border-color 0.15s, transform 0.15s;
      display: block;
    }}
    .lesson-card:hover {{ border-color: var(--accent); transform: translateY(-2px); }}
    .lesson-title {{ font-size: 0.95rem; font-weight: 700; margin-bottom: 0.4rem; }}
    .lesson-meta {{ font-size: 0.78rem; color: var(--muted); }}
    .empty {{ text-align: center; padding: 4rem 2rem; color: var(--muted); }}
    .empty code {{ font-family: 'Space Mono', monospace; font-size: 0.85rem; background: var(--surface2); padding: 2px 8px; border-radius: 4px; }}
  </style>
</head>
<body>
  <div class="hero">
    <h1>Learn <span>Python</span> 🐍</h1>
    <p>Your personal coding curriculum — one lesson at a time.</p>
    <div class="stat-row">
      <div class="stat"><strong>{count}</strong> lesson{"s" if count != 1 else ""} ready</div>
      <div class="stat">Built with 🤖 Claude</div>
    </div>
  </div>
  <div class="grid">
    {lesson_cards if lesson_cards else '<div class="empty"><p>No lessons yet!</p><p style="margin-top:0.5rem">Run <code>make lesson TOPIC="variables"</code> to generate your first lesson.</p></div>'}
  </div>
</body>
</html>"""


def render_all():
    SITE_LESSONS_DIR.mkdir(parents=True, exist_ok=True)

    json_files = list(LESSONS_DIR.glob("*.json"))
    if not json_files:
        print("  No lesson JSON files found in lessons/. Generate one first.")
        return

    lessons = []
    for jf in json_files:
        lesson = json.loads(jf.read_text())
        lessons.append(lesson)

        s = slug(lesson["topic"])
        html_path = SITE_LESSONS_DIR / f"{s}.html"
        html_path.write_text(render_lesson_html(lesson))
        print(f"  Rendered: {html_path}")

    index_path = SITE_DIR / "index.html"
    index_path.write_text(render_index_html(lessons))
    print(f"  Rendered: {index_path}")
    print(f"\n  Done — {len(lessons)} lesson(s) rendered to {SITE_DIR}/")


if __name__ == "__main__":
    render_all()
