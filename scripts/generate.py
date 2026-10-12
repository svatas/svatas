#!/usr/bin/env python3
"""Generate the public profile from local, reviewed JSON. Python 3.10+, no packages."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PALETTES = {
    "dark": {"bg": "#111b1c", "card": "#1a2829", "fg": "#edf3ec", "muted": "#a9bcb5", "line": "#3a514d", "accent": "#c0ed8a", "warm": "#ffba8c"},
    "light": {"bg": "#f4f5ee", "card": "#ffffff", "fg": "#182c27", "muted": "#52665e", "line": "#bdc9bc", "accent": "#356540", "warm": "#a74d21"},
}


def text(x, y, value, size=22, color="fg", weight=400, mono=False):
    family = "'Courier New', monospace" if mono else "Arial, Helvetica, sans-serif"
    return f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{COLORS[color]}">{escape(str(value))}</text>'


def rect(x, y, w, h, fill="card", radius=16, stroke=None):
    border = f' stroke="{COLORS[stroke]}"' if stroke else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{COLORS[fill]}"{border}/>'


def path(d, color="line", width=2):
    return f'<path d="{d}" fill="none" stroke="{COLORS[color]}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'


def dot(x, y, r=5, color="accent"):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{COLORS[color]}"/>'


def svg(height, title, description, body, lang="en"):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" aria-labelledby="title desc" xml:lang="{lang}">\n'
        f'<title id="title">{escape(title)}</title>\n<desc id="desc">{escape(description)}</desc>\n'
        + rect(1, 1, 1198, height - 2, "bg", 20, "line") + "\n" + "\n".join(body) + "\n</svg>\n"
    )


def hero(identity):
    body = [
        text(48, 48, "SVATAS / PERSONAL REPOSITORY", 17, "muted", mono=True),
        text(48, 158, "SVATAS", 108, weight=700),
        text(52, 211, "// HUMAN SOURCE CODE", 31, "accent", weight=700, mono=True),
        text(52, 269, identity["name"], 27),
        text(52, 308, identity["location"], 21, "muted"),
        path("M48 337 H746"),
        text(52, 370, "SYSTEMS THINKING. HUMAN PERSPECTIVE.", 18, "muted", mono=True),
    ]
    # Four orthogonal routes meet a stack of modules, without a diamond or slash.
    body += [rect(811, 52, 342, 287, "card", 24, "line")]
    for x, y, dx, dy in [(863, 104, 1, 1), (1101, 104, -1, 1), (863, 287, 1, -1), (1101, 287, -1, -1)]:
        body += [path(f"M{x} {y} h{dx * 48} V{196 - dy * 26} H{982 - dx * 52}", "line", 3), dot(x, y, 6, "warm")]
    body += [
        rect(930, 146, 104, 100, "bg", 14, "accent"),
        rect(950, 166, 64, 12, "accent", 3),
        rect(950, 190, 46, 12, "muted", 3),
        rect(950, 214, 64, 12, "accent", 3),
        text(846, 83, "systems", 16, "muted", mono=True),
        text(1041, 83, "code", 16, "muted", mono=True),
        text(846, 317, "words", 16, "muted", mono=True),
        text(1041, 317, "light", 16, "muted", mono=True),
        text(853, 370, "curiosity: continuous", 18, "accent", mono=True),
    ]
    return svg(400, identity["brand"], "Svatopluk Vít, Prague, Czechia. Systems thinking and human perspective: systems, code, words and light.", body)


def project_icon(icon, x, y):
    if icon == "compose":
        return [rect(x, y, 124, 91, "bg", 8, "line"), rect(x + 12, y + 13, 100, 24, "accent", 4), rect(x + 12, y + 47, 44, 31, "line", 4), rect(x + 65, y + 47, 47, 31, "line", 4)]
    if icon == "present":
        return [rect(x, y, 124, 91, "bg", 8, "line"), path(f"M{x + 12} {y + 24} H{x + 112}"), dot(x + 18, y + 12, 3), dot(x + 29, y + 12, 3, "warm"), rect(x + 12, y + 36, 47, 43, "accent", 4), path(f"M{x + 71} {y + 44} H{x + 111} M{x + 71} {y + 58} H{x + 102} M{x + 71} {y + 72} H{x + 108}", "muted")]
    if icon == "derive":
        return [path(f"M{x + 24} {y + 14} V{y + 74} M{x + 24} {y + 44} H{x + 96} V{y + 74}", "accent", 3), dot(x + 24, y + 14, 9, "warm"), rect(x + 10, y + 63, 29, 26, "accent", 5), rect(x + 81, y + 63, 29, 26, "accent", 5)]
    raise ValueError(f"Unknown project icon: {icon}")


def gravister(projects, lang):
    heading = "GRAVISTER / THREE DISTINCT JOBS" if lang == "en" else "GRAVISTER / TŘI JASNÉ ÚLOHY"
    body = [text(32, 40, heading, 18, "muted", mono=True)]
    for i, project in enumerate(projects):
        x = 24 + i * 390
        body += [rect(x, 66, 372, 245, "card", 14, "line"), text(x + 22, 98, f"0{i + 1}", 18, "muted", mono=True)]
        body += project_icon(project["icon"], x + 120, 104)
        body += [text(x + 22, 246, project["name"], 35, weight=700), text(x + 22, 282, project[lang]["label"], 22, "accent")]
    return svg(335, "Gravister", "; ".join(p["name"] + ": " + p[lang]["purpose"] for p in projects), body, lang)


def changelog(timeline, lang):
    heading = "HUMAN CHANGELOG / SELECTED MILESTONES" if lang == "en" else "HUMAN CHANGELOG / VYBRANÉ MILNÍKY"
    body = [text(32, 40, heading, 18, "muted", mono=True), path("M50 151 H1150", "line", 3)]
    for i, event in enumerate(timeline):
        x = 40 + i * 290
        body += [text(x, 98, event["year"], 41, weight=700), text(x, 126, event["kind"], 18, "muted", mono=True), dot(x + 8, 151, 7), text(x, 199, event[lang]["title"], 25, "accent", weight=700)]
    return svg(232, "Human Changelog", "; ".join(e["year"] + ": " + e[lang]["title"] for e in timeline), body, lang)


def picture(name, alt, width=1200):
    return (
        '<picture>\n'
        f'  <source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg">\n'
        f'  <source media="(prefers-color-scheme: light)" srcset="assets/{name}-light.svg">\n'
        f'  <img alt="{escape(alt, quote=True)}" src="assets/{name}-light.svg" width="{width}">\n'
        '</picture>'
    )


def readme(identity, projects, timeline, lang):
    copy = identity[lang]
    cs = lang == "cs"
    nav = "[English](README.md) · **Česky**" if cs else "**English** · [Česky](README.cs.md)"
    label = "Oblast | Co do ní přináším" if cs else "Area | What I bring"
    project_label = "Produkt | Účel" if cs else "Product | Purpose"
    header = picture("hero", "SVATAS // Human Source Code — Svatopluk Vít")
    domains = "\n".join(f"| **{title}** | {body} |" for title, body in copy["domains"])
    products = "\n".join(f'| **{p["name"]}** | {p[lang]["purpose"]} |' for p in projects)
    history = "\n\n".join(f'**{e["year"]} · {e[lang]["title"]}** — {e[lang]["detail"]}' for e in timeline)
    return f'''<!-- Generated by scripts/generate.py; edit profile/*.json instead. -->
{header}

{nav}

# {identity["name"]} / {identity["handle"]}

{copy["intro"]}

> {copy["motto"]}

## {copy["domains_heading"]}

| {label} |
| --- | --- |
{domains}

## {copy["gravister_heading"]}

{copy["gravister_intro"]}

{picture("gravister-" + lang, "Gravister — Modularis / Thematis / Derivis")}

| {project_label} |
| --- | --- |
{products}

{copy["gravister_note"]}

## {copy["timeline_heading"]}

{copy["timeline_intro"]}

{picture("human-changelog-" + lang, "Human Changelog — 1987 / 2004 / 2008 / 2026")}

{history}

## {copy["writing_heading"]}

{copy["writing_body"].format(**identity["links"])}

## {copy["connect_heading"]}

{copy["connect_body"].format(**identity["links"])}

---

*{copy["footer"]}*
'''


def generate():
    identity = json.loads((ROOT / "profile/identity.json").read_text(encoding="utf-8"))
    projects = json.loads((ROOT / "profile/projects.json").read_text(encoding="utf-8"))
    timeline = json.loads((ROOT / "profile/timeline.json").read_text(encoding="utf-8"))
    if [p["name"] for p in projects] != ["Modularis", "Thematis", "Derivis"]:
        raise ValueError("Review the public product list before changing it.")
    files = {}
    global COLORS
    for mode, COLORS in PALETTES.items():
        files[f"assets/hero-{mode}.svg"] = hero(identity)
        for lang in ("en", "cs"):
            files[f"assets/gravister-{lang}-{mode}.svg"] = gravister(projects, lang)
            files[f"assets/human-changelog-{lang}-{mode}.svg"] = changelog(timeline, lang)
    for lang, filename in [("en", "README.md"), ("cs", "README.cs.md")]:
        files[filename] = readme(identity, projects, timeline, lang)
    return files


def validate(files):
    """Check XML, accessibility, passive assets and all local README references."""
    for name, content in files.items():
        if name.endswith(".svg"):
            root = ET.fromstring(content)
            if root.get("viewBox") is None or root.get("aria-labelledby") != "title desc":
                raise ValueError(f"Missing accessible SVG metadata: {name}")
            tags = {element.tag.rsplit("}", 1)[-1] for element in root.iter()}
            if not {"title", "desc"} <= tags:
                raise ValueError(f"Missing title or description: {name}")
            if tags - {"svg", "title", "desc", "rect", "text", "path", "circle"}:
                raise ValueError(f"Unexpected active or external SVG element: {name}")
            for element in root.iter():
                if any(key.startswith("on") or "href" in key for key in element.attrib):
                    raise ValueError(f"External or active SVG attribute: {name}")
        else:
            for reference in re.findall(r'(?:src|srcset)="([^"]+)"|\]\(([^)]+)\)', content):
                target = reference[0] or reference[1]
                if urlsplit(target).scheme:
                    if urlsplit(target).scheme != "https":
                        raise ValueError(f"Non-HTTPS public link: {target}")
                    continue
                if target not in files:
                    raise ValueError(f"Broken local reference in {name}: {target}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check committed output without writing files")
    args = parser.parse_args()
    files = generate()
    validate(files)
    stale = []
    for name, content in files.items():
        target = ROOT / name
        if args.check:
            if not target.exists() or target.read_text(encoding="utf-8") != content:
                stale.append(name)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
    if stale:
        print("Stale generated files: " + ", ".join(stale), file=sys.stderr)
        return 1
    print(f'{"Checked" if args.check else "Generated"} {len(files)} files: bilingual README, passive SVGs and local references OK.')
    return 0


if __name__ == "__main__":
    sys.exit(main())
