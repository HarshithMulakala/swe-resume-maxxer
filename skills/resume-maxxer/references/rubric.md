# hiring-agent rubric and mechanics, distilled

Everything below comes from reading the actual prompts and code (`roles/software_engineering_intern/`, `evaluator.py`, `github.py`, `transform.py`, `pymupdf_rag.py`) and from hundreds of real scoring runs. Ground truth, not guesses.

## Score math

- Categories: open_source max 35, self_projects max 30, production max 25, technical_skills max 10
- Plus bonus (max +20), minus deductions. Printed as X/100 but can reach 120.
- The evaluator LLM never sees your raw resume. It sees structured JSON from six extraction prompts (basics, work, education, skills, projects, awards) plus GitHub data. Anything the extractors drop is invisible.

## Open Source (35)

- 25-35: contributions to popular OSS (1000+ stars), significant contributions to well-known projects, GSoC
- 15-24: contributions to smaller external projects, meaningful activity on other people's repos
- 5-10: only personal repos. HARD RULE: all personal repos means 10 max
- Hacktoberfest as your only OSS signal: capped low PLUS a mandatory 3-5 point deduction
- The pipeline cannot see your merged PRs to other people's repos at all (it only lists repos you own). External contributions must be stated in resume text with links.
- Realistic honest ceiling without real external PRs: about 8-10 on strict graders. Tell the user the fix is real PRs or GSoC (+5 bonus and the top band).

## Self Projects (30)

- 20-30 needs: complexity, multiple technologies, real-world impact, user adoption
- Complex-project list the model pattern-matches FOR: full-stack with multiple features, auth + databases, ML/AI, real-time (chat/streaming), mobile with native features, microservices, advanced algorithms, real user adoption
- Simple-project blocklist (kills the score): todo, calculator, basic CRUD (mandatory 0), weather app, notes app, recipe app, portfolio site, tutorial projects, classroom assignments, basic sentiment analysis with NLTK/sklearn, ecommerce clones, social media clones
- Generic names like "Calculator" or "Todo App": -1 each
- Links: no link on a project is -3 to -5 EACH. GitHub link but no live demo is -2 to -3 EACH. Working live demo is +10-20%.
- Fewer strong projects beat many weak ones. Deductions are per project.

## Production (25)

- Two-line rubric: reads work + volunteer sections, extra points for founder/co-founder/early-stage roles. Saturates easily: almost anyone with one real internship or founder role gets 24-25. Do not burn effort here.
- The volunteer section is structurally always empty (extractor bug), so community/OSS org roles must live under Work Experience.
- Work is the richest surviving section (summary + all bullets). Densest content goes here. Action + tech + real metric per bullet.

## Technical Skills (10)

- One-line rubric. Categorized skill lines with real keywords get 9-10 basically always. No headroom, just don't break it.

## Bonus (max +20)

- +5 GSoC (spell out "Google Summer of Code")
- +3-5 founder/co-founder in a JOB TITLE
- +2-3 early-stage engineer (first 10-20 employees, say it explicitly)
- +2 portfolio website URL in the header
- +1 LinkedIn
- +1-3 blog (the blog pipeline is dead code, so this only fires if the model infers it from a header link; cheap to include if real)
- No bonus exists for hackathons, certifications, competitive programming, or publications.

## Deductions

- Per-project link deductions (see above), simple-project deductions, all-personal-repos deduction (-3 to -5), Hacktoberfest-only deduction
- Fairness block: school name, GPA, location, demographics must not affect the score. Zero value optimizing those.

## Extraction traps (cost real points silently)

1. `Name | Tech, Tech` project titles: the transform splits on `|`, moves the tech into a field that is NEVER shown to the evaluator. Tech stack must appear in bullet prose.
2. Only name + description + url survive per project. Bullets get condensed into description by the extractor, so front-load what matters.
3. Icon-only links are dropped entirely. Every link needs visible anchor text. Best: the URL itself as visible text, hyperlinked.
4. The GitHub link must extract with network label "GitHub" and a real username URL or enrichment never runs and open_source collapses. Put `github.com/<username>` as visible header text.
5. A `username.github.io` link is labeled Portfolio, not GitHub. You need both if you want both.
6. Certifications, publications, languages sections are invisible (extractor only keeps 6 sections). Restate anything important as awards, skills keywords, or work bullets.
7. Multi-column layouts scramble reading order. Single column only. Max 3 font sizes, no monospace (becomes code blocks), standard bullets.
8. Hyphenated terms that wrap across lines get their hyphen deleted ("real-time" becomes "real time" split across lines). Keep them on one line.
9. Overlaid text-box edits on a PDF leak BOTH old and new text into extraction. Regenerate PDFs cleanly, never patch them.
10. White/hidden text IS extracted by the scorer but do not use it. It is the known exploit, it is detectable, and it is dishonest.

## GitHub enrichment mechanics

- Fetches up to 100 of the user's most recently updated repos. Forks with under 5 forks of their own are discarded (so your fork of a big project is invisible).
- Repos where the user has 0 attributed commits are dropped in code; under 4 commits are excluded by the selection prompt. 15+ commits get prioritized.
- An LLM picks 7 repos, pre-sorted by stars. The evaluator sees ONLY: username, name, bio, followers, repo count, and per repo name/description/URL/stars/forks/language.
- So: real descriptions on the top repos matter a lot, junk repos should be private, the bio field is shown, and contributor counts/commit counts are NOT shown to the evaluator even though the selection uses them.
- After any GitHub change, delete `cache/gh_*` and `cache/githubcache_*` or the scorer keeps using the old snapshot.

## Measurement discipline

- The scorer caches extraction by PDF FILENAME. New content = new filename, always.
- Single runs are noise. 4+ runs per version, compare medians per category.
- Small local models (gemma) swing up to 33 points on identical input. Frontier Gemini models swing 5-15. Iterate on Gemini if at all possible.
- Never run two batches on one API key at once. Rate limits kill runs silently mid-extraction.
- Read the Evidence lines across runs. A phrase appearing in most runs is real signal. A one-off is a coin flip.
- providers.json controls allowed models. New Gemini models can be added under the gemini provider with temperature 0.1, top_p 0.9.
