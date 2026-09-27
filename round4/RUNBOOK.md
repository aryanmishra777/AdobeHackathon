# Round 4 runbook — do these before the camera rolls

## Why a fresh directory matters

Record the trial run in an **empty folder**, not in the repo. `.audit/` in the
repo holds every development audit; a judge seeing those could reasonably wonder
whether the demo site was pre-baked. An empty folder makes it obvious that the
bundle and the report are created live, and it matches `TEST_STEPS` in the
manifest exactly.

```
mkdir ~/r4-demo && cd ~/r4-demo
```

## Pre-flight (run all four, expect all four)

**1 · The harness loads the submitted engine.** This is the integrity gate; if it
does not say MATCH, do not record.

```
python "<repo>/round4/verify_wiring.py"
```

Expect: `MATCH: the agent is running the submitted Round 3 marketplace.`
(63 files, fingerprint `5c4e779d…f279c5` on both lines.)

> Already done once this session: the skills in `~/.claude/skills/` were stale —
> 17 files behind the submission and missing `render_playwright.py` and
> `extras.py` entirely — and have been reinstalled from
> `dist/brand-ai-readiness-audit.zip`. Re-run the check anyway; it costs a second.

**2 · The renderer is available** (this is what makes READ-001 a measurement
rather than an inference, and the manifest promises it):

```
python "<repo>/brand-ai-readiness-audit/skills/site-evidence-collector/scripts/render_playwright.py" --check
```

Expect: `playwright-chromium 151.0.7922.34`

**3 · No stale output for the demo site.** In the fresh folder there is nothing
to clear, but confirm:

```
ls .audit 2>/dev/null || echo "clean"
```

**4 · The submission is untouched.** The engine must be frozen at the Round 3
state for the whole recording:

```
cd "<repo>" && git status --porcelain brand-ai-readiness-audit/
```

Expect: no output. If anything appears, `git checkout -- brand-ai-readiness-audit/`
before recording and re-run pre-flight 1.

## Recording settings

- Terminal font large enough to read at 1080p — the evidence text is the proof,
  and a judge who cannot read it cannot corroborate it.
- Maximise the terminal; avoid a narrow window that wraps the finding text into
  noise.
- Close anything with personal data (other tabs, notifications).

## What to expect during the run

Rehearsed on the submitted engine, scripts-only, 2026-09-27:

| site | pages | crawl time | renders | headline finding |
|---|---|---|---|---|
| **grammarly.com** | 25 | 87 s | 4/6 | PARSE-002 high — 10 of 18 JSON-LD blocks are empty |
| lenskart.com | 25 | 67 s | 6/6 | REACH-010 high — canonical host is literally `undefined` |
| zerodha.com | 25 | 32 s | 6/6 | 54 findings — too noisy to narrate |
| swiggy.com | 25 | 56 s | 6/6 | 5 findings — too thin |
| patagonia.com | 1 | 23 s | 1/1 | unusable, only one page reachable |

The **agent-driven** run adds the model-judged checks on top of these, so the
final list will not be identical to the scripts-only rehearsal — it is usually
slightly shorter, because the agent's review drops candidates that fail a
registry guard. The deterministic findings, including PARSE-002, will be there.
Budget roughly 2–4 minutes of wall clock; trim the idle stretches in the edit.

## The drill-in, verified

`PARSE-002 — Structured data is present but does not parse` on grammarly.com is
a **verified true positive**, not a parser artefact. Checked against the raw
HTML in the bundle, 11 sampled pages carry JSON-LD and 10 of them ship exactly
one empty block:

| page | blocks | empty | parses |
|---|---|---|---|
| `/premium` → `/pro` | 1 | **1** | 0 |
| `/paraphrasing-tool` | 1 | **1** | 0 |
| `/features` | 1 | **1** | 0 |
| `/trust` | 1 | **1** | 0 |
| `/plagiarism-checker` | 3 | 1 | 2 |
| `/citations` | 2 | 0 | 2 |

On **seven** pages the *only* structured-data block is empty — including
`/premium`, the page that sells the product. So the site ships
`<script type="application/ld+json"></script>` with nothing inside. A person
sees a perfect page; a crawler asking "what is this page, what does it cost"
gets an empty answer.

Provable on camera in one command — **`-L` is required**, `/premium` 301s to
`/pro` and plain `curl` returns 79 bytes of redirect:

```
curl -sL https://www.grammarly.com/premium | grep -o 'application/ld+json[^>]*></script>'
```

Verified output — the tag closes immediately, so the block is empty:

```
application/ld+json"></script>
```

Second drill-in if there is time: `PARSE-012` — `/paraphrasing-tool` carries 15
question-shaped headings with answers and declares no `FAQPage` entity.

## Things that would sink the submission

- Editing anything under `brand-ai-readiness-audit/` at any point. The engine is
  frozen; Round 4 is a demonstration round, not a rebuild.
- Splicing two takes of the trial run together. Trimming idle waiting is
  explicitly allowed; a cut that joins a URL from one run to findings from
  another is an integrity failure.
- A URL, harness or model in the video that does not match `REPLAY_Copper_Bottle.txt`.
- Quoting a number on camera that the submission does not support. Verified and
  safe to say: **91 checks**, **all 91 carry false-positive guards**, **26 fix
  files**, **6 mechanisms**, **64-site corpus**, **16-point GEO/SEO separation**.
  Do **not** say "18 proactive recommendations" — the real count is 24, and the
  submitted README does not make that claim (only the repo README does).
