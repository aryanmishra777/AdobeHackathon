# What this audit can and cannot see

This marketplace audits **one website**. Several of the factors that decide
whether a generative engine cites that website are not properties of the website
at all. Every report must say so, because a discoverability grade that quietly
ignores them overstates what was measured.

Copy the relevant entries into `coverage.limitations` on every report. Say them
plainly, in the report's own voice — not as a disclaimer footer.

## Outside the reach of any site crawl

**Whether the engine searches at all.** Roughly 58% of ChatGPT runs answer from
the model without retrieving anything, and Google AI Overviews fire on a minority
of queries (far more often when the query is phrased as a question). A site can
be perfectly readable and still never enter the running, because the query never
triggered retrieval. Nothing in the HTML predicts this.

**What third parties say.** For niche brand queries, assistants cite third-party
sources far more often than the brand's own domain — in one multi-engine audit,
about 95% third-party against 5% brand-owned on ChatGPT. The corpus that decides
the answer is mostly not the site being audited. A clean bill of health here says
nothing about whether the brand is present in that corpus.

**Who else is competing.** Citation share is redistributive, not absolute. When
competing pages in the same retrieval pool change, a page's share moves even
though the page did not. Measured on one benchmark: under one strategy the
5th-ranked page gained while the 1st-ranked page lost share. We audit one
candidate, never the pool.

**Which engine is asking.** Retrieval and citation behaviour differ sharply
between architectures — how much they favour brand domains, whether they cite
social platforms at all, how they rerank. A change that helps on one assistant
can be neutral or negative on another. We test none of them directly.

**Where the page lands in the context window.** Position inside the retrieved
context strongly affects selection. We can see where a fact sits in the page's
own DOM; we cannot see where the page sits among the documents the engine
retrieved.

**Off-site content placed to steer retrieval.** Commercial optimisation often
works by publishing on forums, wikis and review sites rather than by editing the
brand's own pages. That activity is invisible from here.

## Inside our reach, and worth stating anyway

- **Renderer availability.** Without a browser, JavaScript-dependency is inferred
  from raw-HTML signals rather than measured. Say `inferred`, not `measured`, and
  cap confidence at medium.
- **Sample size.** A finding generalised from a handful of pages is a claim about
  those pages. The sampled count belongs in the evidence string.
- **Skills that did not run.** If a mechanism had no analyzer, its axis is
  reported as `not assessed`. Never as a grade.
- **Drift.** Live sites change between runs. A finding is true of the fetch it
  cites, at the time it cites.

## The rule

State the boundary in the report, not in a footnote, and never let a grade imply
coverage the audit did not have. A tool that names its blind spots can be
trusted about what it did measure; one that hides them cannot be trusted about
anything.
