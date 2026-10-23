#!/usr/bin/env python3
"""Snapshot a page's current copy as the "before" side of a copy comparison.

Run this BEFORE editing any copy. It writes the snapshot under
<serve-root>/_compare/before/, installs the compare viewer at
<serve-root>/_compare/index.html, and keeps _compare/ out of git via
.git/info/exclude (never .gitignore, so nothing in the repo changes).

  # Static site: the page is a file the server serves as-is.
  snapshot.py --serve-root . --page / --from-file index.html

  # Rendered site (React, Next, Astro, ...): save the rendered HTML first
  # (curl for SSR/SSG, or the browser's document.documentElement.outerHTML for
  # client-only apps), then strip scripts so hydration can't swap in the new copy.
  snapshot.py --serve-root public --page /pricing --from-html /tmp/pricing.html --strip-scripts

Prints the "before" URL path to put in changes.json.
"""
import argparse
import pathlib
import re
import shutil
import subprocess
import sys

SKILL = pathlib.Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--serve-root", required=True, help="Directory the dev server serves at /")
    ap.add_argument("--page", required=True, help="URL path of the page, e.g. / or /pricing")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--from-file", help="Source HTML file served as-is")
    src.add_argument("--from-html", help="Saved rendered HTML of the page")
    ap.add_argument("--strip-scripts", action="store_true", help="Remove <script> tags (rendered snapshots)")
    a = ap.parse_args()

    root = pathlib.Path(a.serve_root).resolve()
    html = pathlib.Path(a.from_file or a.from_html).read_text(encoding="utf-8")

    if a.strip_scripts:
        html = re.sub(r"<script\b[^>]*>.*?</script\s*>", "", html, flags=re.S | re.I)

    # Relative asset URLs must still resolve from the page's real location,
    # not from inside _compare/before/.
    page = a.page if a.page.startswith("/") else "/" + a.page
    base_dir = page[: page.rindex("/") + 1]
    if not re.search(r"<base\b", html, re.I):
        html, n = re.subn(r"(<head\b[^>]*>)", rf'\1<base href="{base_dir}">', html, count=1, flags=re.I)
        if not n:
            html = f'<base href="{base_dir}">' + html

    leaf = page.strip("/")
    out_rel = (leaf if leaf.endswith(".html") else (leaf + "/index.html").lstrip("/"))
    out = root / "_compare" / "before" / out_rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")

    shutil.copyfile(SKILL / "assets" / "compare.html", root / "_compare" / "index.html")

    try:
        top = pathlib.Path(subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], cwd=root, text=True).strip())
        exclude = pathlib.Path(subprocess.check_output(
            ["git", "rev-parse", "--git-path", "info/exclude"], cwd=root, text=True).strip())
        if not exclude.is_absolute():
            exclude = root / exclude
        entry = "/" + str((root / "_compare").relative_to(top)) + "/"
        lines = exclude.read_text().splitlines() if exclude.exists() else []
        if entry not in lines:
            exclude.parent.mkdir(parents=True, exist_ok=True)
            exclude.write_text("\n".join(lines + [entry]) + "\n")
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        print("note: not a git repo; remember to delete _compare/ yourself", file=sys.stderr)

    print("/_compare/before/" + out_rel)


if __name__ == "__main__":
    main()
