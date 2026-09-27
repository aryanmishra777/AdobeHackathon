# Round 4 video script — 5:00 hard cap

**Budget:** Part 1 methodology ≤ 3:00 · Part 2 live trial run ≤ 2:00.

Every claim below is anchored to a path **inside the submitted package**
(`brand-ai-readiness-audit/`). Narration that cannot be traced to submitted code
earns no credit, so each beat names its file. Keep the file open on screen while
you say the line, or show the path in the terminal.

Word counts are sized for ~135 wpm. Beats marked **[cut if long]** can go.

---

## Part 1 — Thought process (≤ 3:00)

### Beat 1 · How we discovered the findings (0:00 – 1:05)

> An assistant fails to cite a site at one of six sequential points: it can't get
> in, can't read the page, can't parse a fact out, can't lift a quotable claim,
> won't trust it, or the visitor who arrives leaves. The marketplace is those six
> stages, one skill each — `marketplace.json`, entrypoint `audit-orchestrator`.
>
> We didn't guess the signals. Two sources. First, the published retrieval
> research — and we wrote down what it does *not* support. Structured-data markup
> has no controlled evidence of citation lift, so our PARSE checks report what a
> machine cannot extract and never promise a ranking or traffic gain.
>
> Second, a 64-site corpus labelled by *measurement*, never assertion — GEO from
> the blocking mechanism we actually observed. That corpus is what separates GEO
> from SEO: fourteen sites a conventional SEO linter passes clean score sixteen
> points lower with us, because the edge returns 429 to ClaudeBot.
>
> Every signal became a registry entry before it became code — 91 checks across
> six `references/checks.yaml` files. Each carries its inputs, whether it's
> deterministic or model-judged, an evidence template, a verification command a
> human can run, and binding false-positive guards. All 91 have guards.

**On screen:** `marketplace.json`, then
`skills/crawl-access-audit/references/checks.yaml` scrolled to one entry so the
`false_positive_guards:` block is visible.

### Beat 2 · How we assigned severities (1:05 – 2:05)

> Severity is computed, never chosen by feel. `references/severity-rubric.md`
> defines the four bands; `scripts/merge_findings.py` applies them
> deterministically — same bundle in, same findings and same IDs out, every run.
>
> Base severity comes from the check's own `severity_rule`. Then a scope
> modifier, a de-escalation when confidence is low, and the gates.
>
> Three rules carry most of the weight. The **model-judged ceiling**: a finding a
> model judged can never be critical unless a deterministic finding corroborates
> it — gate 3 in `references/false-positive-gates.md`. **`severity_locked`**: some
> registry guards forbid movement outright, so REACH-015 is never above medium
> from timing alone, because our measurement includes network distance we can't
> subtract.
>
> And **intentionality**. Blocking GPTBot — a training crawler — is a licensing
> decision, usually taken after legal review. We report it informational, and a
> test asserts the words "error", "defect", "bug" and "problem" never appear in
> that finding. Blocking ChatGPT-User — a retrieval agent fetching because a user
> just asked about you — is a high-severity defect. Same HTTP status, opposite
> meaning. Getting that backwards discredits the whole report.

**On screen:** `severity-rubric.md`, then `merge_findings.py` at the severity
function, then `false-positive-gates.md`.

### Beat 3 · How we derived the suggested actions (2:05 – 3:00)

> Every finding carries a `suggested_action` — the shape is fixed in
> `references/finding.schema.json` — with steps, an effort estimate, an owner,
> and an impact rationale. The wording comes from a fixes library: twenty-six
> files under `references/fixes/`, one per failure mode.
>
> The constraint is mechanism-soundness: a fix has to act on the stage that
> actually failed. That's why supersession exists — `references/subskills.json`.
> A page whose content is absent from the HTML *also* has no structured data and
> no quotable chunk. That's one defect, not three, and fixing the render clears
> all three. Reporting them as peers triples the apparent problem count and
> misdirects the fix.
>
> Prioritisation is impact over effort, grouping findings that share one fix —
> a single robots.txt edit can clear four.
>
> **[cut if long]** And we state the boundary. `references/audit-boundary.md`
> lists the causal factors no single-site crawl can see — whether the engine
> retrieved anything, what third parties say, the competing pool. Every report
> carries them, and an axis nothing measured is reported "not assessed", never
> graded.

**On screen:** `finding.schema.json`, `ls references/fixes/`, `subskills.json`
at `supersession_rules`.

---

## Part 2 — Live trial run (≤ 2:00)

Site: **<SITE>** — never used in development. See `round4/RUNBOOK.md` for the
pre-flight checks to run *before* the camera rolls.

### 0:00 – 0:15 · Harness, model, wiring

> Harness is Claude Code v2.1.283, model Claude Opus 5. Before I run anything:
> this proves the agent loads the submitted engine, not a demo.

Run on camera:

```
python round4/verify_wiring.py
```

> Same fingerprint over the installed skills and over the Round 3 zip. Sixty-three
> files, byte for byte.

### 0:15 – 0:30 · Enter the URL

Type into Claude Code, on camera, verbatim:

```
audit <SITE>
```

> No flags, no path — the agent picks the entrypoint skill from its description.

### 0:30 – 1:10 · Let the agent work *(trim idle time here)*

> It's activating `audit-orchestrator`, which calls the collector — one polite,
> robots-respecting crawl — then dispatches the six analysis skills over that one
> evidence bundle. Nothing re-fetches. That's what makes it deterministic.

### 1:10 – 1:50 · Drill into one finding with real evidence

<FINDING_WALKTHROUGH — filled once the site is chosen>

Show, in this order: the finding in `report.md` → the **raw evidence file in the
bundle** it points at → the `verification` command → the `suggested_action`.

### 1:50 – 2:00 · Sorted by impact

> And the priority plan ranks the fixes by impact over effort, grouping the ones
> that share a single change.

**On screen:** the "Fix these first" section of `report.md`.

---

## Integrity notes

- The run must be **one continuous session**. Trimming idle waiting is allowed
  and expected; splicing two takes is an integrity failure.
- The URL typed on camera, the harness, and the model must match
  `REPLAY_<TeamName>.txt` exactly.
- Do not edit anything under `brand-ai-readiness-audit/` before or after
  recording. The engine is frozen at the Round 3 submission.
