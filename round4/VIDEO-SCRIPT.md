# Round 4 video script, 5:00 hard cap

Budget: Part 1 methodology ≤ 3:00, Part 2 live trial run ≤ 2:00.

Part 1 runs at **110 words per minute**, which is an explaining pace: slower than
conversation (130 to 150), fast enough that an expert does not start reading
ahead of you. Part 2 is deliberately thin, so most of its two minutes is spent
watching the agent work rather than listening.

The judge has never seen this project. The first thirty seconds therefore buy
context and nothing else: what breaks, how often, and what the engine does about
it. No introductions, no architecture tour, no reading the six stage names aloud.

One image carries Part 1: `round4/methodology.svg`. The voice carries the
argument, the diagram carries the detail. Do not narrate the diagram. Point at a
region and say the sentence that makes it mean something.

Beats 1 to 3 each own a region of it, in reading order: the three triage columns,
then the severity chain with its two clamps, then the fix lane and the
GPTBot/ChatGPT-User strip at the foot. Beat 0 has no region. It plays over the
header band and one cut to the benchmark scoreboard.

Measure before recording. The script reports the pace it requires, so you can
check yourself against a stopwatch:

```
python round4/check_timing.py
```

Cut to a real file four times in Part 1 (the scoreboard, `checks.yaml`,
`merge_findings.py`, `references/fixes/`). That is enough to prove the anchoring
the rubric asks for without turning the pitch into a code tour.

---

## Part 1 · Thought process (≤ 3:00)

### Beat 0 · Why this engine exists (0:00 – 0:35)

> Fifty of the sixty-four brand sites we benchmarked carry a defect bad enough to
> stop an AI assistant citing them. Twenty-six of those rank fine on Google.
>
> Nothing is down. The page looks right to a person. The break only surfaces when
> an assistant tries to answer a question about you.
>
> So we built an engine that finds them and says what to change.

**On screen:** the diagram's header band, then cut to `bench/scoreboard/latest.txt`
on "twenty-six of those". Say nothing about the corpus beyond the two numbers.

### Beat 1 · How we found the signals (0:35 – 1:31)

> Where does it break? Six places, from getting in to coming back, one skill
> each.
>
> The signals came out of nine primary GEO papers, and each one had to pass two
> questions: is there a controlled measurement, and is its absence a defect?
>
> Pass both and it ships as a check; real but page-dependent and it ships as a
> recommendation; flat or negative and it does not ship, with the reason
> recorded.
>
> Ninety-one checks survived, each with a false-positive guard. A naive auditor
> fails a site the moment a crawler meets a firewall. Ours reports only when the
> agent came away empty.

**On screen:** the three triage columns, which carry the six stage names so you
never have to read them. Rest on the red column while you say "does not ship".
Keyword stuffing is sitting in it, so the diagram makes the point for you. Then
cut to `checks.yaml` with a `false_positive_guards:` block on screen.

If a judge asks how many papers: nine primary sources, listed by arXiv and SSRN id
at the top of `docs/EVIDENCE.md`, plus a survey of 45 studies that we cite for
what it found *absent* (no controlled evidence that JSON-LD lifts citations). Do
not say "forty-five studies" as though we read them. That number is Martinez's
review scope, not ours.

### Beat 2 · How we assign severity (1:31 – 2:24)

> Once a check fires, how bad is it? Nobody types that in. The check proposes a
> severity, site-wide scope raises it, and confidence and six false-positive gates
> can only pull it down.
>
> One rule clamps it from above: a model-judged finding never reaches critical
> unless a deterministic check agrees.
>
> Severity also depends on which agent was refused. A 403 to GPTBot is a training
> crawler turned away, a licensing decision, so we report it as information. A 403 to ChatGPT-User is a retrieval agent fetching
> the page because somebody just asked about you.
>
> Same status code. Opposite severity.

**On screen:** the severity chain, then both red clamps, then the contrast strip
at the foot. You only speak the second clamp (the model-judged ceiling), so let
the first one, `severity_locked`, be read rather than narrated. Cut to
`merge_findings.py` on "the check proposes a severity".

Pause a beat and a half after "Same status code" before you say "Opposite
severity". It is the one non-obvious thing in the three minutes and it needs the
room.

### Beat 3 · How we derive the fix (2:24 – 3:00)

> Then, what to do about it. Every finding carries its fix: steps, effort, an
> owner, and why it works.
>
> A fix has to act on the stage that failed. A page missing its content
> from the HTML has no structured data and nothing quotable. That is one defect,
> not three, and supersession collapses it.
>
> They rank by impact over effort, grouping fixes that share one change.

**On screen:** the fix lane and `priority_plan`. Cut to `ls references/fixes/`,
26 files.

### Spare · only if you land early (11 seconds)

Outside the budget. Say it only if Beat 3 ends before 2:49, over the same frame.

> We also state our own limit. Five of seven causal factors sit outside any site
> crawl, and every report says so.

---

## Part 2 · Live trial run (≤ 2:00)

Site: **https://www.grammarly.com/**, never used in development (not in the
64-site corpus, the 15-site unseen sweep, or the 8 hand-audited sites). Run the
pre-flight in `round4/RUNBOOK.md` first.

Narration here stays thin on purpose. The run is the evidence, not the voiceover.

### 0:00 – 0:15 · Harness, model, wiring

> Claude Code, Claude Opus 5. One fingerprint over the skills the agent loads,
> and over the submitted zip. They match.

```
python round4/verify_wiring.py
```

### 0:15 – 0:28 · Enter the URL

```
audit https://www.grammarly.com/
```

> A site the audit has never seen. No flags, so the agent picks the entrypoint
> itself.

### 0:28 – 1:10 · Let the agent work *(trim idle time here)*

> One polite crawl. Six skills read that single bundle. Nothing re-fetches.

### 1:10 – 1:48 · Drill into one finding

Target: **PARSE-002**, high, site-wide, 10 of 25 pages. Verified true before
recording, see RUNBOOK.

> Ten of eighteen structured-data blocks do not parse. Here it is live.

```
curl -sL https://www.grammarly.com/premium | grep -o 'application/ld+json[^>]*></script>'
```

> The tag closes immediately. Empty, including on the page that sells the
> product. A person sees a perfect page. A crawler gets nothing.
>
> The fix names the mechanism and the cost: they are paying for structured data
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
| Anchor every claim to your code | 3 file cuts in Part 1; every path on the diagram is inside the package |
| Enter the URL on camera | Part 2, 0:15 |
| Let the agent work in the CLI | Part 2, 0:28 |
| Drill into findings with real evidence | Part 2, 1:10, invalid JSON-LD, named in the brief |
| Show fixes sorted/prioritised by impact | Part 2, 1:48 |
| State harness and model on camera | Part 2, 0:00 |
| One line on wiring | Part 2, 0:00, `verify_wiring.py` |

## Integrity notes

- One continuous run. Trimming idle waiting is allowed. Splicing two takes is an
  integrity failure.
- The URL, harness and model on camera must match `REPLAY_Copper_Bottle.txt`.
- Nothing under `brand-ai-readiness-audit/` may be edited before or after
  recording. The engine is frozen at the Round 3 submission.
- Two files shown or cited in Part 1 are repo-level and **not** in the submitted
  package: the benchmark scoreboard (`bench/scoreboard/latest.txt`, source of the
  50-of-64 and 26-of-38 numbers) and the literature ledger (`docs/EVIDENCE.md`,
  source of the nine primary papers and the five-of-seven limit). The checks, constants
  and guards are all inside the package. If a judge asks, say that plainly.
