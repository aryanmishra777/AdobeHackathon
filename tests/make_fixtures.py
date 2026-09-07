#!/usr/bin/env python3
"""Generate the local fixture sites used by the deterministic test layer.

Dev tooling -- outside the submission.

Each fixture is a tiny static site with a deliberate defect, plus one CLEAN site
that must produce zero critical or high findings. The clean site is the
false-positive tripwire and is the most important fixture in the repo: any check
that fires on it is wrong by construction.

    python tests/make_fixtures.py          # write tests/fixtures/*
    python tests/make_fixtures.py --list   # show what each fixture targets

After generating, build bundles with:

    python tests/make_bundles.py
"""

from __future__ import annotations

import argparse
import io
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="http://localhost:{port}{path}">
{extra}
</head>
<body>
<header><nav>
<a href="/">Home</a> <a href="/about.html">About</a>
<a href="/pricing.html">Pricing</a> <a href="/faq.html">FAQ</a>
<a href="/contact.html">Contact</a>
</nav></header>
<main>
"""

FOOT = """</main>
<footer><p>&copy; {year} Northwind Coffee Roasters Ltd, Leeds, United Kingdom.
<a href="/contact.html">Contact us</a></p></footer>
</body></html>
"""

ORG_LD = """<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "http://localhost:{port}/#organization",
  "name": "Northwind Coffee Roasters",
  "description": "Small-batch specialty coffee roaster based in Leeds, United Kingdom.",
  "url": "http://localhost:{port}/",
  "foundingDate": "2014",
  "address": {{
    "@type": "PostalAddress",
    "streetAddress": "14 Kirkgate",
    "addressLocality": "Leeds",
    "postalCode": "LS1 6BY",
    "addressCountry": "GB"
  }},
  "sameAs": [
    "https://www.linkedin.com/company/northwind-coffee-roasters",
    "https://www.wikidata.org/wiki/Q000000"
  ]
}}
</script>"""


def page(port, path, title, desc, body, extra="", year=2026):
    return (HEAD.format(title=title, desc=desc, port=port, path=path, extra=extra)
            + body + FOOT.format(year=year))


def build_clean(port=8901):
    """Everything right. MUST produce zero critical or high findings."""
    f = {}
    f["robots.txt"] = (
        "User-agent: ChatGPT-User\nUser-agent: Claude-User\n"
        "User-agent: PerplexityBot\nUser-agent: OAI-SearchBot\n"
        "Allow: /\n\n"
        "User-agent: *\nAllow: /\nDisallow: /cart\nDisallow: /checkout\n\n"
        f"Sitemap: http://localhost:{port}/sitemap.xml\n")

    f["sitemap.xml"] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(
            f"<url><loc>http://localhost:{port}{p}</loc>"
            f"<lastmod>{d}</lastmod></url>\n"
            for p, d in [("/", "2026-08-30"), ("/about.html", "2026-07-12"),
                         ("/pricing.html", "2026-08-28"), ("/faq.html", "2026-08-20"),
                         ("/contact.html", "2026-06-02")])
        + "</urlset>\n")

    f["llms.txt"] = (
        "# Northwind Coffee Roasters\n\n"
        "> Small-batch specialty coffee roaster based in Leeds, United Kingdom,\n"
        "> shipping across the UK since 2014.\n\n"
        "## Key pages\n\n"
        f"- [Pricing](http://localhost:{port}/pricing.html): Subscriptions from "
        "GBP 29 per month, delivery included.\n"
        f"- [About](http://localhost:{port}/about.html): Founded 2014, 12 staff, Leeds.\n"
        f"- [Contact](http://localhost:{port}/contact.html): Address, hours, phone.\n")

    f["index.html"] = page(
        port, "/", "Northwind Coffee Roasters | Small-batch coffee, Leeds",
        "Small-batch specialty coffee roasted in Leeds and shipped across the UK.",
        """
<h1>Northwind Coffee Roasters</h1>
<p>Northwind Coffee Roasters is a small-batch specialty coffee roaster based in
Leeds, United Kingdom. Northwind has roasted and shipped single-origin coffee
across the United Kingdom since 2014.</p>

<h2>Coffee subscriptions</h2>
<p>Northwind subscriptions start at GBP 29 per month. Every Northwind
subscription includes free UK delivery and a rotating single-origin selection
chosen by our roasting team.</p>
<p><a href="/pricing.html">See full Northwind pricing</a></p>

<h2>Where Northwind coffee is roasted</h2>
<p>Northwind roasts every batch at its Leeds roastery at 14 Kirkgate, Leeds
LS1 6BY. The roastery is open to visitors on Saturdays from 9am to 4pm.</p>
<p><a href="/about.html">More about the Northwind roastery</a></p>

<img src="/roastery.jpg" alt="The Northwind roasting room in Leeds"
     width="800" height="600" loading="lazy">
""",
        extra=ORG_LD.format(port=port))

    f["pricing.html"] = page(
        port, "/pricing.html", "Pricing | Northwind Coffee Roasters",
        "Northwind coffee subscriptions from GBP 29 per month, UK delivery included.",
        """
<h1>Northwind coffee subscription pricing</h1>
<p>Northwind offers three subscription tiers. All Northwind prices include free
delivery within the United Kingdom and can be cancelled at any time.</p>

<h2>Northwind Explorer &mdash; GBP 29 per month</h2>
<p>The Northwind Explorer plan costs GBP 29 per month and delivers 250g of a
rotating single-origin coffee every month.</p>

<h2>Northwind Roaster &mdash; GBP 49 per month</h2>
<p>The Northwind Roaster plan costs GBP 49 per month and delivers 500g of coffee
each month, with a choice of grind.</p>

<h2>Northwind Wholesale &mdash; from GBP 180 per month</h2>
<p>Northwind wholesale accounts start at GBP 180 per month with a minimum order
of 5kg. Wholesale customers should contact the Northwind team directly.</p>
""",
        extra=ORG_LD.format(port=port))

    f["about.html"] = page(
        port, "/about.html", "About | Northwind Coffee Roasters",
        "Northwind Coffee Roasters was founded in Leeds in 2014.",
        """
<h1>About Northwind Coffee Roasters</h1>
<p>Northwind Coffee Roasters is a specialty coffee roaster founded in Leeds,
United Kingdom, in 2014. Northwind employs 12 people and roasts approximately
four tonnes of coffee each year.</p>
<h2>The Northwind roastery</h2>
<p>The Northwind roastery sits at 14 Kirkgate, Leeds LS1 6BY. Northwind roasts
on a 15kg drum roaster and cups every batch before it ships.</p>
<p>Published <time datetime="2026-07-12">12 July 2026</time>.</p>
""",
        extra=ORG_LD.format(port=port))

    f["faq.html"] = page(
        port, "/faq.html", "FAQ | Northwind Coffee Roasters",
        "Common questions about Northwind coffee subscriptions and delivery.",
        """
<h1>Northwind frequently asked questions</h1>
<h2>How much does a Northwind subscription cost?</h2>
<p>Northwind subscriptions start at GBP 29 per month for the Explorer plan and
GBP 49 per month for the Roaster plan. Every Northwind plan includes free UK
delivery.</p>
<h2>Where does Northwind ship?</h2>
<p>Northwind ships to all United Kingdom addresses. Northwind does not currently
ship outside the United Kingdom.</p>
<h2>Can a Northwind subscription be cancelled?</h2>
<p>Yes. A Northwind subscription can be cancelled at any time from the account
page, and cancellation takes effect at the end of the current billing month.</p>
""",
        extra="""<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {"@type": "Question", "name": "How much does a Northwind subscription cost?",
     "acceptedAnswer": {"@type": "Answer",
      "text": "Northwind subscriptions start at GBP 29 per month for the Explorer plan and GBP 49 per month for the Roaster plan."}},
    {"@type": "Question", "name": "Where does Northwind ship?",
     "acceptedAnswer": {"@type": "Answer",
      "text": "Northwind ships to all United Kingdom addresses."}}
  ]
}
</script>""")

    f["contact.html"] = page(
        port, "/contact.html", "Contact | Northwind Coffee Roasters",
        "Contact Northwind Coffee Roasters in Leeds.",
        """
<h1>Contact Northwind Coffee Roasters</h1>
<p>Northwind Coffee Roasters, 14 Kirkgate, Leeds LS1 6BY, United Kingdom.</p>
<p>Telephone: <a href="tel:+441130000000">+44 113 000 0000</a></p>
<p>The Northwind roastery is open Monday to Friday, 8am to 5pm, and Saturday
9am to 4pm.</p>
<form action="/enquiry" method="post">
<label for="email">Your email</label>
<input id="email" type="email" name="email" required>
<label for="msg">Message</label>
<textarea id="msg" name="msg" required></textarea>
<button type="submit">Send</button>
</form>
""")
    return f


def build_js_shell(port=8902):
    """READ-001: content assembled in the browser, absent from the HTML."""
    f = {"robots.txt": f"User-agent: *\nAllow: /\n\nSitemap: http://localhost:{port}/sitemap.xml\n"}
    f["sitemap.xml"] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>http://localhost:{port}{p}</loc></url>\n"
                  for p in ["/", "/pricing.html", "/about.html", "/faq.html"])
        + "</urlset>\n")
    shell = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title></head>
<body>
<div id="root"></div>
<script id="__NEXT_DATA__" type="application/json">
{{"props":{{"pageProps":{{"content":"%s"}}}},"page":"{page}","buildId":"x"}}
</script>
<script src="/app.js"></script>
</body></html>
""" % ("lorem ipsum dolor sit amet " * 400)
    for path, title, pg in [("index.html", "Meridian Analytics", "/"),
                            ("pricing.html", "Pricing | Meridian", "/pricing"),
                            ("about.html", "About | Meridian", "/about"),
                            ("faq.html", "FAQ | Meridian", "/faq")]:
        f[path] = shell.format(title=title, page=pg)
    return f


def build_blocked_crawlers(port=8903):
    """REACH-002 defect vs REACH-003 informational -- the retrieval/training split."""
    f = build_clean(port)
    f["robots.txt"] = (
        "# Retrieval agents blocked -- this IS a defect (REACH-002)\n"
        "User-agent: ChatGPT-User\nUser-agent: Claude-User\n"
        "User-agent: PerplexityBot\nDisallow: /\n\n"
        "# Training crawlers blocked -- this is NOT a defect (REACH-003)\n"
        "User-agent: GPTBot\nUser-agent: Google-Extended\nUser-agent: CCBot\n"
        "Disallow: /\n\n"
        "User-agent: *\nAllow: /\n")
    return f


def build_contradictory_markup(port=8904):
    """PARSE-007: markup that disagrees with the visible page."""
    f = build_clean(port)
    f["pricing.html"] = page(
        port, "/pricing.html", "Pricing | Northwind Coffee Roasters",
        "Northwind coffee subscriptions.",
        """
<h1>Northwind coffee subscription pricing</h1>
<h2>Northwind Explorer &mdash; GBP 29 per month</h2>
<p>The Northwind Explorer plan costs GBP 29 per month, delivery included.</p>
<h2>Northwind Roaster &mdash; GBP 49 per month</h2>
<p>The Northwind Roaster plan costs GBP 49 per month.</p>
""",
        extra="""<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Northwind Explorer subscription",
  "offers": {
    "@type": "Offer",
    "price": "12.00",
    "priceCurrency": "GBP",
    "availability": "https://schema.org/OutOfStock"
  }
}
</script>""")
    return f


def build_stale_content(port=8905):
    """TRUST-002 and TRUST-004: stale content and stamps."""
    f = build_clean(port)
    f["index.html"] = page(
        port, "/", "Northwind Coffee Roasters", "Small-batch coffee.",
        """
<h1>Northwind Coffee Roasters</h1>
<p>Northwind Coffee Roasters is a small-batch coffee roaster in Leeds.</p>
<h2>Our 2019 harvest selection</h2>
<p>Published <time datetime="2019-03-04">4 March 2019</time>. Our current
selection features the 2019 Colombian harvest, available now.</p>
""", year=2019, extra=ORG_LD.format(port=port))
    # Every URL claims the same very recent lastmod while content is from 2019.
    f["sitemap.xml"] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>http://localhost:{port}{p}</loc>"
                  f"<lastmod>2026-09-06</lastmod></url>\n"
                  for p in ["/", "/about.html", "/pricing.html", "/faq.html",
                            "/contact.html"])
        + "</urlset>\n")
    return f


def build_unquotable(port=8906):
    """QUOTE-001: passages that collapse once retrieved on their own."""
    f = build_clean(port)
    f["pricing.html"] = page(
        port, "/pricing.html", "Pricing", "Our plans.",
        """
<h1>Pricing</h1>
<p>We believe great coffee should be simple to buy, and we have built our plans
around that belief from the very beginning of our journey together.</p>
<h2>The basics</h2>
<p>It starts at 29 a month. They include delivery, and it can be cancelled
whenever you like. As mentioned above, this is the one most people choose.</p>
<h2>Going further</h2>
<p>This one is 49. It doubles what you get, and they also let you pick the
grind. See the table below for the full breakdown of what each of them offers.</p>
<h2>For businesses</h2>
<p>Those start at 180 and need a minimum order. Get in touch and we will sort
it out with you directly.</p>
""")
    return f


def build_low_engagement(port=8907):
    """STAY-001 and STAY-010: no orientation, no viewport."""
    f = build_clean(port)
    f["index.html"] = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Welcome</title></head>
<body>
<header><nav><a href="/about.html">About</a></nav></header>
<main>
<h1>Excellence, delivered.</h1>
<p>Redefining what matters. Discover the difference.</p>
<img src="/hero.jpg">
</main>
</body></html>
"""
    return f


FIXTURES = {
    "clean": (build_clean, 8901,
              "TRIPWIRE: must produce ZERO critical or high findings"),
    "js-shell": (build_js_shell, 8902, "READ-001 content absent from raw HTML"),
    "blocked-crawlers": (build_blocked_crawlers, 8903,
                         "REACH-002 defect vs REACH-003 informational"),
    "contradictory-markup": (build_contradictory_markup, 8904,
                             "PARSE-007 markup contradicts the page"),
    "stale-content": (build_stale_content, 8905,
                      "TRUST-002 staleness, TRUST-003 dishonest lastmod"),
    "unquotable-chunks": (build_unquotable, 8906,
                          "QUOTE-001 chunks fail standalone comprehension"),
    "low-engagement": (build_low_engagement, 8907,
                       "STAY-001 no orientation, STAY-010 no viewport"),
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args(argv)

    if args.list:
        print(f"{'fixture':24} {'port':6} targets")
        for name, (_fn, port, desc) in FIXTURES.items():
            print(f"{name:24} {port:<6} {desc}")
        return 0

    for name, (fn, port, desc) in FIXTURES.items():
        out = os.path.join(ROOT, name)
        os.makedirs(out, exist_ok=True)
        files = fn(port)
        for fname, content in files.items():
            with io.open(os.path.join(out, fname), "w",
                         encoding="utf-8", newline="\n") as fh:
                fh.write(content)
        print(f"{name:24} port {port}  {len(files)} files  -- {desc}")
    print(f"\nwrote {len(FIXTURES)} fixtures to {ROOT}")
    print("next: python tests/make_bundles.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
