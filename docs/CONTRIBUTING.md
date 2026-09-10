# Contributing

Rules that keep three authors producing one coherent marketplace rather than
three that happen to share a folder.

## The one asymmetry that drives everything

> A missed finding costs one rubric point.
> A confident false positive costs the reader's trust in every other finding.

A site owner who spots one obviously-wrong `critical` stops reading the report.
When the evidence does not clearly support a claim, lower `confidence` or drop
the finding. Optimize for being believed, not for finding count.

## Hard rules

**1. The submission is stdlib-only.** Everything under
`brand-ai-readiness-audit/` imports from the Python standard library and nothing
else — no `requests`, no `bs4`, no `yaml`. A grader's machine will not run
`pip install`. `tools/validate.py` enforces this by AST-walking every shipped
file. Dev tooling in `tools/`, `tests/` and `bench/` may take dependencies.

**2. Only the collector touches the network.** Analysis skills read the evidence
bundle from disk. No `urllib`, no sockets, no subprocess curl. One crawl, six
analyses — that is what makes the audit polite, fast, and reproducible.

**3. Everything is deterministic.** No `datetime.now()`, no `time.time()`, no
unseeded `random`, no iteration over an unsorted set. The same bundle must
produce byte-identical findings on every run, or the golden tests are
meaningless. The collector is the sole exception — it stamps real timestamps
into `run.json`.

**4. Emit base severity only.** Your check emits the level its `severity_rule`
specifies. The orchestrator applies the scope and confidence modifiers. Applying
them in both places double-counts and inflates every severity in the report.

**5. Every finding cites resolvable evidence.** `evidence_detail.artifact_refs`
must be non-empty and every path must exist in the bundle. A finding that cannot
point at its own proof is deleted, not downgraded.

**6. `false_positive_guards` are binding.** Implement every mechanically-testable
guard as code. Leave an explicit comment for each guard needing agent judgment.
A guard was written by someone who already met the site pattern that fools that
check.

## Writing a check

Copy the structure in
`brand-ai-readiness-audit/skills/crawl-access-audit/scripts/check_access.py`:

```python
def check_read_001(b: Bundle) -> list[dict]:
    """One function per check, named check_<id>."""
    # Guard: a framework marker alone proves nothing -- require the combination.
    ...
    return [finding("READ-001", title, "high", evidence, refs, ...)]

CHECKS = [check_read_001, ...]   # the driver wraps each in try/except
```

The `finding()` and `act()` helpers are copied verbatim into each skill. That is
deliberate: each skill must run standalone from inside its own folder, so a
shared module would break portability for a few saved lines.

## Writing the finding text

**`title`** — the defect in the site owner's language. Not "READ-001 triggered"
but "Page content is missing from the HTML a crawler receives".

**`evidence`** — quantified, and never a restatement of the title. The validator
rejects an `evidence` equal to its `title`.

> Bad: "No structured data was found."
> Good: "Crawled 12 product pages; 0/12 contain any `application/ld+json` block."

**`impact_rationale`** — why the fix resolves the *mechanism*, not a restatement
of the fix. This is the field that proves a recommendation is mechanism-sound
rather than cargo-culted.

**`suggested_action.code`** — tailored to this site, using real values from the
bundle. A snippet containing `YOUR_DOMAIN` gets pasted into production verbatim
by someone. The validator warns on placeholders; the test suite fails on them.

**`verification`** — one step letting a human disagree with us. If a finding
cannot be falsified in one step, it is an opinion and belongs in
`proactive_recommendations`.

## Adding or changing a check

- **Never renumber a published check ID.** Retire it and add a new one.
- Registry first, code second. If they disagree, the registry wins.
- A new check needs a fixture that makes it fire, and must not fire on `clean`.
- Found a new way to be wrong? Add a `false_positive_guard`. That is the one part
  of the contract expected to keep growing.

## Testing

```bash
python tests/make_fixtures.py && python tests/make_bundles.py   # after fixture edits
python -m pytest tests/ -q
python tools/validate.py
python bench/run.py --live        # pinned 8-site subset
```

`test_clean_site_produces_no_serious_findings` is the most important test in the
repo. It has already caught one real false positive — an FP guard specified in
`checks.yaml` but never implemented in the script. If it fails, you have shipped
a false positive; fix the check, never the fixture.

## Before you open a PR

- [ ] `python tools/validate.py` passes
- [ ] `python -m pytest tests/ -q` passes
- [ ] the clean fixture produces zero critical/high from your skill
- [ ] two runs on one bundle are byte-identical
- [ ] no non-stdlib imports inside `brand-ai-readiness-audit/`
- [ ] every new check has a fixture and a `false_positive_guard`

## Scope discipline

The rubric penalises padding explicitly. Before adding a check, ask whether it
names a *distinct mechanism by which a site fails*. Twenty variations on "add
more markup" score worse than eight checks that each explain a different reason
a brand is invisible.

The same applies to recommendations: a proactive suggestion must cite something
actually observed in the bundle. Generic advice is worth nothing here.

## A check that never fires

`python tools/check_coverage.py` runs every analysis skill over every bundle it
can find and lists the checks that produced no finding anywhere.

This exists because two checks once shipped as dead code and every other gate
stayed green. `REACH-014` raised an exception that the driver swallowed;
`REACH-013` read a manifest key that does not exist. Neither produced a single
finding on any site. The tests passed, the validator passed, the bench passed --
because all of them ask "did anything go wrong?" and none asked "did this check
ever do anything?".

A silent check is not automatically broken. Some detect genuinely rare things.
So say which, in the registry entry:

```yaml
  - id: PARSE-002
    rarity: rare
    rarity_reason: >-
      Fires only when a JSON-LD block is present but malformed. Most published
      markup parses.
```

Declaring it is a claim someone made deliberately, and that is the point. The
alternative is silence, and silence is what let the dead checks through.

Run it before you claim a check is finished, and with `--strict` in any final
pass: it exits non-zero on an undeclared silent check, and on any check that
crashes.

Two traps it will not catch, both of which have bitten us:

- **A gate that never closes.** `REACH-017` read `run.site_profile`, which the
  collector never writes, so its "ecommerce only" restriction silently applied to
  every site. If your check gates on something, assert that the something exists.
- **A metric on the wrong scale.** `format_density` counted list *items* where
  the paper counts list *elements*, so it read 0.65 against a published band of
  0.25-0.35. It fired, so coverage looked fine; it was measuring a different
  quantity. When a threshold comes from a paper, check the definition, not just
  the number.
