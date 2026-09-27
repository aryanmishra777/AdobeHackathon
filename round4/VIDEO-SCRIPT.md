# Round 4 video script — 5:00 hard cap

**Budget:** Part 1 methodology ≤ 3:00 · Part 2 live trial run ≤ 2:00.

Part 1 is **272 words**, which fills the 3:00 cap at **91 words per minute** —
deliberate, and well under conversational speed of 130–150, so a judge absorbs
each point instead of catching half of it. Part 2 is 110 words, leaving **47
seconds** of its two minutes to actually watch the agent work.

That budget is the design constraint: the voice carries only the through-line
and **the diagram carries the detail**. Do not read the diagram aloud — point at
it and say the sentence that makes it mean something.

Measure before recording (it reports the pace the script requires, so you can
check yourself against a stopwatch):

```
python round4/check_timing.py
```

One image for the whole of Part 1: **`round4/methodology.svg`**. Its five regions
are the five beats, in reading order — three triage columns, the severity chain,
the two red clamps, the fix lane, and the GPTBot / ChatGPT-User contrast at the
foot. Cut to a real file three times only; that is enough to prove the anchoring
the rubric asks for.

---

## Part 1 — Thought process (≤ 3:00)

### Beat 1 · How we found the signals (0:00 – 1:05)

> An assistant fails to cite you at one of six points — get in, read, parse,
> quote, trust, stay. Six stages, one skill each.
>
> We didn't guess the signals. Forty-five studies, and one test for each: is
> there a controlled measurement, and is its absence a defect?
>
> If yes, it ships as a check. If the effect is real but depends on the page, it
> ships as a recommendation — never as a defect. If there is no effect, or a
> negative one, it is not shipped, and we record why.
>
> Ninety-one checks. Every one of them guarded.

**On screen:** the three triage columns. Rest on the red column while you say
"not shipped" — then cut to `checks.yaml` with a `false_positive_guards:` block
visible on the last line.

### Beat 2 · How we assign severity (1:05 – 2:04)

> Severity is computed, never chosen. The check's own rule, then scope,
> confidence, six false-positive gates, supersession.
>
> Two things can stop it moving: a locked registry guard, and the rule that a
> model-judged finding is never critical unless a deterministic one agrees.
>
> Here is the distinction that matters most. A 403 to GPTBot is a training
> crawler — a licensing decision, and we report it as information. A 403 to
> ChatGPT-User is a retrieval agent, fetching this page because a user just
> asked about you.
>
> Same status code. Opposite meaning.

**On screen:** the severity chain, then the two red clamps, then the contrast
strip at the foot — point, don't narrate it. Cut to `merge_findings.py` on
"computed, never chosen".

### Beat 3 · How we derive the fix (2:04 – 3:00)

> Every finding carries its fix: steps, effort, an owner, and a rationale.
>
> A fix has to act on the stage that actually failed. A page whose content is
> missing from the HTML also has no structured data and nothing quotable. That
> is one defect, not three.
>
> Then they rank by impact over effort, grouping the ones that share a single
> change.
>
> **[cut if long]** And we state our own boundary. Five of seven causal factors
> sit outside any site crawl, and every report says so.

**On screen:** the fix lane and `priority_plan`. Cut to `ls references/fixes/` —
26 files.

---

## Part 2 — Live trial run (≤ 2:00)

Site: **https://www.grammarly.com/** — never used in development (not in the
64-site corpus, the 15-site unseen sweep, or the 8 hand-audited sites). Run the
pre-flight in `round4/RUNBOOK.md` first.

Narration here is deliberately thin: the run is the evidence, not the voiceover.

### 0:00 – 0:15 · Harness, model, wiring

> Claude Code, Claude Opus 5. One fingerprint over the skills the agent loads
> and over the submitted zip. They match.

```
python round4/verify_wiring.py
```

### 0:15 – 0:28 · Enter the URL

```
audit https://www.grammarly.com/
```

> A site the audit has never seen. No flags — the agent picks the entrypoint
> itself.

### 0:28 – 1:10 · Let the agent work *(trim idle time here)*

> One polite crawl. Six skills read that single bundle. Nothing re-fetches.

### 1:10 – 1:48 · Drill into one finding

Target: **PARSE-002**, high, site-wide, 10 of 25 pages. Verified true before
recording — see RUNBOOK.

> Ten of eighteen structured-data blocks don't parse. Here it is live.

```
curl -sL https://www.grammarly.com/premium | grep -o 'application/ld+json[^>]*></script>'
```

> The tag closes immediately. Empty — including on the page that sells the
> product. A person sees a perfect page. A crawler gets nothing.
>
> The fix names the mechanism, and the cost: they are paying for structured data
> and receiving none of the benefit.

### 1:48 – 2:00 · Sorted by impact

> And the fixes rank by impact over effort.

**On screen:** the "Fix these first" section of `report.md`.

---

## Audit against the Round 4 brief

| Requirement (§3) | Where |
|---|---|
| Part 1 ≤ 3 min, Part 2 ≤ 2 min | budgeted above, measured by `check_timing.py` |
| How you discovered the findings | Beat 1 |
| How you assigned severities | Beat 2 |
| How you derived the suggested actions | Beat 3 |
| Anchor every claim to your code | 3 file cuts; every path on the diagram is inside the package |
| Enter the URL on camera | Part 2, 0:15 |
| Let the agent work in the CLI | Part 2, 0:28 |
| Drill into findings with real evidence | Part 2, 1:10 — invalid JSON-LD, named in the brief |
| Show fixes sorted/prioritised by impact | Part 2, 1:48 |
| State harness and model on camera | Part 2, 0:00 |
| One line on wiring | Part 2, 0:00 — `verify_wiring.py` |

## Integrity notes

- One continuous run. Trimming idle waiting is allowed; splicing two takes is an
  integrity failure.
- The URL, harness and model on camera must match `REPLAY_Copper_Bottle.txt`.
- Nothing under `brand-ai-readiness-audit/` may be edited before or after
  recording. The engine is frozen at the Round 3 submission.
- The literature ledger (`docs/EVIDENCE.md`) is repo-level, **not** in the
  submitted package. The checks, constants and guards on the diagram all are. If
  a judge asks, say that plainly.
