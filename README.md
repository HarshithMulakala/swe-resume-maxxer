# swe-resume-maxxer

**For SWE, SWE intern, new grad, and AI/ML resumes.**

HackerRank open sourced the actual LLM pipeline they built to rank 50,000+ software intern applications ([hiring-agent](https://github.com/interviewstreet/hiring-agent)). So I made a coding agent skill that scores your resume against that exact rubric, figures out exactly where you're losing points, and rewrites your resume until the score tops out. No fake stuff, just presenting what you actually did in a way the scorer can actually read.

If you're applying to software engineering internships or early-career SWE/AI roles, this is literally the rubric class of tool screening you. The scoring dimensions are all engineering signals: GitHub, open source, shipped projects, production experience, technical skills. It is not built for design, PM, finance, or any non-engineering resume.

## My results (real runs, not vibes)

| | before | after |
|---|---|---|
| Gemini 2.5 Flash (median of 10+ runs) | 63/100 | **96/100** (one run literally hit 100, zero deductions every run) |
| Gemini 3.6 Flash (way stricter grader) | 64/100 | 70-74/100 |

Same me, same experience. The 33 point jump is all stuff the scorer was blind to or penalizing for dumb reasons.

## What it actually does

No API keys, no cloning, nothing to configure. The scorer's actual rubric prompts and its exact PDF extraction module are vendored right into the skill (it's all MIT), so your coding agent applies the real rubric itself:

1. Extracts your resume with the scorer's own extraction code, so you see exactly what it sees
2. Scores it against the real rubric prompts in three passes (generous, strict, adversarial) plus a deterministic audit checklist, and takes the median
3. Shows you what the scorer literally sees after PDF extraction. Spoiler: way less than you think. If you write project titles like `MyApp | React, Node.js` the tech list gets silently deleted before the scoring model ever sees it. Icon-only links just vanish. Certifications are invisible.
4. Audits your GitHub the way the scorer does. It pulls your repos, throws away forks and anything with under 4 of your commits, then shows the model your top 7 as just name + description + stars. Empty description = it shows "Description: None". Junk repos leak into those 7 slots.
5. Rewrites your resume content against the actual rubric and regenerates a clean single-column PDF (or matches your existing format)
6. Rescores, repeats until it stops moving
7. Optional ground truth mode: if you do have a Gemini key (free) or Ollama, it clones the real repo and runs the actual pipeline for calibrated numbers. That's how I got the scores in the table.

## The rubric in one breath

Open source is 35 points, self projects 30, production 25, technical skills 10, bonus up to +20, deductions down to -20. Founder in a job title is +3 to 5. Portfolio link in your header is +2. Every project without a link is -3 to -5. And the top open source band basically requires merged PRs into 1000+ star repos, you cannot write your way into it. The full playbook I pulled out of the prompts and code is in [`skills/resume-maxxer/references/rubric.md`](skills/resume-maxxer/references/rubric.md).

## Install

One line, works across Claude Code, Codex, Cursor, and basically every coding agent (it drops the skill in `.agents/skills` and symlinks Claude Code automatically):

```bash
npx skills add HarshithMulakala/swe-resume-maxxer
```

Claude Code plugin route if you prefer:

```
/plugin marketplace add HarshithMulakala/swe-resume-maxxer
/plugin install resume-maxxer@swe-resume-maxxer
```

Or just copy it manually: `skills/resume-maxxer/` goes into `~/.claude/skills/` (Claude Code) or `.agents/skills/` (Codex, Cursor, most others).

Then tell your agent something like "use resume-maxxer on my_resume.pdf" and it takes it from there. It's plain markdown plus three small python scripts, nothing agent specific.

## You need

- Python 3.10+ and Chrome (for rendering the PDF)
- `pip install pymupdf==1.26.3 pymupdf4llm==0.0.27 jinja2` (the skill tells your agent to do this)
- Optional: `gh` CLI logged in, for the GitHub audit
- Optional: a free Gemini API key or Ollama, only if you want ground truth mode

## The honest part

This optimizes how your real experience is presented. Link hygiene, extraction-safe formatting, wording the rubric rewards, GitHub metadata the scorer reads. It will not invent metrics, fake experience, or do the hidden white text exploit (yes that works, yes it's detectable, no I'm not helping you end your interview in 30 seconds). The one gap it can't fix with words is real open source contributions, and the skill just tells you straight how to fix that in real life.

## License

MIT. The scorer itself is MIT from HackerRank.
