---
name: resume-maxxer
description: Score a software-engineering resume PDF against HackerRank's open-source hiring-agent rubric (software engineering intern role) and iteratively maximize it with honest content only. Built for SWE, SWE intern, new grad, and AI/ML engineering resumes. No API keys needed, the agent applies the real rubric itself. Use when the user wants to score, test, or optimize a SWE or AI resume, or mentions hiring-agent, ATS scoring, or resume ranking.
---

# resume-maxxer

You are going to score a real software-engineering resume the way HackerRank's open-source `hiring-agent` scorer does, then iterate the resume until the score tops out. The vendored rubric is the `software_engineering_intern` role, which is what HackerRank ships and what this skill is tuned for; it fits SWE, SWE intern, new grad, and AI/ML engineering resumes. If the user's resume is for a non-engineering role, tell them this rubric will not evaluate it meaningfully. You apply the scorer's ACTUAL rubric prompts yourself, so no API keys or local models are required. Honest content only: never fabricate experience or metrics, never use hidden text. If the user's real background caps a category, say so and tell them the real-world action that raises it.

## Setup (keyless, no cloning, once per workspace)

```
pip install pymupdf==1.26.3 pymupdf4llm==0.0.27 jinja2
```

(If bare `pip`/`python` resolve to the wrong interpreter, use the platform's launcher, e.g. `py -3.12 -m pip ...` on Windows.) All `scripts/...` and `references/...` paths below are relative to THIS skill's installed directory (e.g. `.agents/skills/resume-maxxer/` or `~/.claude/skills/resume-maxxer/`), so prefix them or cd there; your content JSONs and PDFs live in the user's workspace.

Everything else is already in this skill: the scorer's ACTUAL rubric prompts are vendored verbatim at `references/criteria.jinja` and `references/system_message.jinja`, and the scorer's exact PDF extraction module is vendored at `scripts/pymupdf_rag.py` (all MIT from the hiring-agent repo). Read both rubric files completely before scoring anything. They ARE the ground truth; `references/rubric.md` is the distilled cheat sheet with the extraction traps and deterministic audit. Keep the pinned versions: newer pymupdf breaks the extraction module.

## Step 1: See what the scorer sees

```
python scripts/extract_view.py resume.pdf
```

READ the output.

Look for: mangled name, hyperlinks attached to the wrong text, duplicate/garbage text from PDF edits, multi-column scrambling, missing links (icon-only links vanish entirely). Every extraction trap is listed in `references/rubric.md`. If the GitHub URL is not cleanly visible in this output, open_source (35 points) is forfeit before scoring even starts.

## Step 2: Fetch GitHub the way the scorer does

Keyless via `gh api` (usually authenticated in coding agents) or plain unauthenticated HTTPS (60 req/hr is enough):

- `GET /users/<username>/repos?per_page=100&sort=updated&type=all`
- Per candidate repo: `GET /repos/<u>/<r>/contributors` for contributor count and the user's commit count

Then simulate the scorer's selection exactly: discard forks (unless the fork itself has 5+ forks), discard repos with 0 commits by the user, exclude under 4 commits, pick the top 7 by stars favoring high commit counts. What the evaluator ultimately sees per repo is ONLY: name, description, URL, stars, forks, language, plus profile bio/followers/repo count. Note every selected repo with an empty description; each one renders as "Description: None".

## Step 3: Score it yourself (3 passes)

Apply `references/criteria.jinja` + `references/system_message.jinja` to (a) the extracted resume text and (b) the simulated GitHub payload. Produce the same output shape as the scorer: per-category score with evidence, bonus breakdown, deduction list. Do THREE independent passes with different postures: once generously, once strictly, once adversarially (hunt for every deduction the prompts mandate). Take the median PER CATEGORY, then recompute the total from those category medians; report that plus the min-max spread of the pass totals. Also run the deterministic audit in `references/rubric.md` (link checks, blocklist names, cap conditions, bonus triggers); deterministic findings override vibes.

## Step 4: Rewrite, render, iterate

1. Build a content JSON replicating the user's existing format and voice (`templates/content.example.json` shows the schema for `templates/template.html.j2`, a clean single-column ATS-safe serif layout; keep the user's own format if they have one).
2. Apply the playbook in `references/rubric.md`. Hard rules:
   - Every project has a working link. Live demos beat repo links.
   - Tech stack in bullet PROSE. The `Name | Tech, Tech` title convention gets silently deleted by the scorer's transform.
   - Visible-text GitHub URL in the header (`github.com/<user>`). Never icon-only links.
   - Portfolio URL in header (+2), LinkedIn (+1), "Founder"/"Co-Founder" in job titles where true (+3-5).
   - Nothing that pattern-matches the simple-project blocklist (todo, calculator, CRUD, weather, portfolio-site, ...).
   - No invented numbers. Reuse the user's real metrics; qualitative phrasing where none exist.
3. Render: `python scripts/make_resume.py content/vN.json versions/vN.pdf` (add `--template path/to/your.html.j2` when replicating the user's own format instead of the default template). Must be 1 page. The script prints page count, embedded links, and the scorer's-eye extraction. Verify all three.
4. Re-score (step 3) and repeat until the audit is clean and your three-pass median plateaus.
5. Confirm every date, title, and claim you were not explicitly given with the user. Never guess facts onto a resume.
6. GitHub fixes need explicit user approval (they touch a public profile): real descriptions on the top repos, privatize junk repos, surface work hidden in forks or org accounts.

## Optional: ground-truth mode (real scorer, needs a backend)

If the user has a Gemini API key (free at aistudio.google.com/api-keys) or Ollama installed, run the real pipeline for calibrated numbers: `git clone https://github.com/interviewstreet/hiring-agent`, create `hiring-agent/.env` with `DEFAULT_MODEL` + key, `pip install -r hiring-agent/requirements.txt` into a venv (Python 3.10+), then `python scripts/run_batch.py <pdf> 4 <tag>`. Rules that matter: the scorer caches by PDF FILENAME so every content change gets a new filename; never run two batches on one key concurrently; compare per-category MEDIANS across 4+ runs, never single runs; small local models swing up to 33 points so prefer Gemini. Delete `hiring-agent/cache/gh_*` and `githubcache_*` after any GitHub profile change.

## What honest optimization cannot do

Open source (35 pts) caps near 8-10 without real merged PRs to established external projects. The rubric's top band requires 1000+ star projects or GSoC, and the pipeline cannot even see upstream PRs (it only lists repos the user owns). Tell the user this straight, with the concrete path: 3-5 real merged PRs, or Google Summer of Code (+5 bonus and the 25-35 band).
