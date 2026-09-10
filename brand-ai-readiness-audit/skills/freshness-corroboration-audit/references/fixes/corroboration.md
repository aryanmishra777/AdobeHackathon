# Fix: corroboration

A claim repeated consistently across independent sources is believed. A claim
that lives in exactly one place -- the site's own copy -- is fragile, and a
machine weighing which sources to trust discounts it.

Covers `TRUST-006` (claims appear nowhere else), `TRUST-009` (absent from the
sources machines check), `TRUST-012` (off-site descriptions disagree),
`TRUST-013` (no independent coverage), `TRUST-014` (dead outbound sources),
`TRUST-015` (unattributed claims).

**Uncorroborated is not untrue.** Nothing here implies a claim is false because
no one else repeats it. The goal is to give accurate facts more places to live.

## Seed the facts where machines look

Pick the handful of load-bearing facts -- founding year, headquarters, scale,
credentials, category -- and make sure they are stated, identically, in the
places retrieval systems actually read:

- **Structured data** on the site (`Organization` / `LocalBusiness` with
  `foundingDate`, `address`, `sameAs`).
- **Directory and map listings** for a local business; **review platforms** for
  SaaS and ecommerce; **sector registries** for a nonprofit. The right set
  depends on the category -- do not apply one checklist to every site.
- **Wikidata** where the organisation is genuinely notable. (Wikipedia has a
  notability bar most organisations do not clear; do not chase an article.)

Keep the wording of a fact the same everywhere. "Founded 2014" in one place and
"since 2015" in another is a contradiction a machine will notice.

## Give other people a reason to cite you

Corroboration you do not control is the durable kind. The way to earn it is to
publish something worth restating in someone else's words:

- Original data, a benchmark, an annual survey, a methodology page.
- A clearly-licensed facts page or press kit with the canonical numbers.

Never solicit fake reviews or pay for placements -- discovered, it poisons every
real signal.

## Attribute the claims on the page

For any specific statistic or research claim ("cuts onboarding time by 40%",
"used by 2,000 teams"), put the source next to it: a linked study, a named
customer, a "methodology" note. A claim about the company's own operations
("we roast four tonnes a year") needs no external source, but a claim about the
world does.

## Keep outbound citations alive

Links that support factual claims are themselves a trust signal, and a dead one
is a small negative. Check them on a schedule; when a source moves, update the
link; when it is gone for good, replace it or remove the claim it supported. A
`403` from an automated check is not proof the link is dead -- verify in a
browser before acting.
