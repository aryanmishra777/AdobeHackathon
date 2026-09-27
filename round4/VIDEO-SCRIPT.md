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

**On screen:** hold `round4/methodology-1-signals.svg` for the whole beat — it
carries the papers, the effect sizes, the three exits and the owning module, so
you can narrate against it instead of listing. Cut to
`skills/crawl-access-audit/references/checks.yaml`, scrolled to one entry with
the `false_positive_guards:` block visible, on the last sentence. Diagram
explains; the file proves.

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

**On screen:** `round4/methodology-2-severity.svg`, top half — the six-stage
chain and the two red clamps hanging off it. The GPTBot / ChatGPT-User panel at
the foot of that diagram is the intentionality beat; point at it rather than
describing it. Cut to `merge_findings.py` at the severity function on "computed,
never chosen".

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

**On screen:** `round4/methodology-2-severity.svg`, lower half — FINDING versus
PROACTIVE RECOMMENDATION feeding one `priority_plan`. Cut to
`ls references/fixes/` (26 files) and `subskills.json` at `supersession_rules`.

---

## Part 2 — Live trial run (≤ 2:00)

Site: **https://www.grammarly.com/** — never used in development (not in the
64-site corpus, the 15-site unseen sweep, or the 8 hand-audited sites). See
`round4/RUNBOOK.md` for the pre-flight checks to run *before* the camera rolls.

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
audit https://www.grammarly.com/
```

> No flags, no path — the agent picks the entrypoint skill from its description.

### 0:30 – 1:10 · Let the agent work *(trim idle time here)*

> It's activating `audit-orchestrator`, which calls the collector — one polite,
> robots-respecting crawl — then dispatches the six analysis skills over that one
> evidence bundle. Nothing re-fetches. That's what makes it deterministic.

### 1:10 – 1:50 · Drill into one finding with real evidence

Target: **PARSE-002 — "Structured data is present but does not parse"**, high,
site-wide, 10 of 25 pages. Verified true before recording (see RUNBOOK).

> Top finding, high severity: ten of eighteen structured-data blocks on this
> site fail to parse. Here's the evidence the report points at — the raw HTML we
> actually fetched.

Open the bundle file the finding cites, `pages/p007/raw.html`, and show the
block. Then prove it against the live site:

```
curl -sL https://www.grammarly.com/premium | grep -o 'application/ld+json[^>]*></script>'
```

> The tag closes immediately. The block is empty. On seven of these pages the
> *only* structured-data block is empty — including `/premium`, the page that
> sells the product. A person sees a perfect page. A crawler asking "what is
> this, what does it cost" gets nothing back.

Then the fix, read off the report:

> And the action isn't generic advice — it names the mechanism: inspect the
> template rendering the `ld+json` block, escape the dynamic fields, validate
> with a strict linter. Effort small, owner engineering. The rationale is the
> part I'd put to a CTO — they're *paying the engineering cost of structured
> data without receiving any of the machine-readability benefit*.

**[cut if long]** Second finding, one line: `/paraphrasing-tool` carries fifteen
question-shaped headings with answers and declares no `FAQPage` entity.

### 1:50 – 2:00 · Sorted by impact

> And the priority plan ranks the fixes by impact over effort, grouping the ones
> that share a single change.

**On screen:** the "Fix these first" section of `report.md`.

---

## Integrity notes

- The run must be **one continuous session**. Trimming idle waiting is allowed
  and expected; splicing two takes is an integrity failure.
- The URL typed on camera, the harness, and the model must match
  `REPLAY_Copper_Bottle.txt` exactly.
- Do not edit anything under `brand-ai-readiness-audit/` before or after
  recording. The engine is frozen at the Round 3 submission.
