#!/usr/bin/env python3
"""Generate the public profile from local, reviewed JSON. Python 3.10+, no packages."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PALETTES = {
    "dark": {"bg": "#171717", "fg": "#f3eddc", "muted": "#aab4bf", "line": "#39434c", "accent": "#ff795f"},
    "light": {"bg": "#f3eddc", "fg": "#171717", "muted": "#535e67", "line": "#cec9bd", "accent": "#b93420"},
}


def text(x, y, value, size=22, color="fg", weight=400, mono=False):
    family = "'Courier New', monospace" if mono else "Arial, Helvetica, sans-serif"
    return f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{COLORS[color]}">{escape(str(value))}</text>'


def rect(x, y, w, h, fill="bg", radius=16, stroke=None):
    border = f' stroke="{COLORS[stroke]}"' if stroke else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{COLORS[fill]}"{border}/>'


def path(d, color="line", width=2):
    return f'<path d="{d}" fill="none" stroke="{COLORS[color]}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'


def svg(width, height, title, description, body, lang):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc" xml:lang="{lang}">\n'
        f'<title id="title">{escape(title)}</title>\n<desc id="desc">{escape(description)}</desc>\n'
        + rect(1, 1, width - 2, height - 2, "bg", 0) + "\n" + "\n".join(body) + "\n</svg>\n"
    )


def hero(identity, lang, mobile):
    cs = lang == "cs"
    width, height = (600, 780) if mobile else (1200, 620)
    x = 34 if mobile else 48
    label = "SERVISNÍ LIST / LIDSKÝ EXEMPLÁŘ" if cs else "SERVICE MANUAL / HUMAN SPECIMEN"
    status = "DOKUMENTACE NEÚPLNÁ." if cs else "DOCUMENTATION INCOMPLETE."
    running = "AUTOR STÁLE V PROVOZU." if cs else "AUTHOR STILL RUNNING."
    spare = "NEROZEBÍRAT." if cs else "DO NOT DISASSEMBLE."
    body = [text(x, 42, label, 17, "accent", mono=True),
            text(x-3, 147, "SVATAS", 104 if mobile else 126, "fg", 900),
            text(x, 185, "// HUMAN SOURCE CODE", 22, "accent", mono=True),
            path(f"M{x} 212 H{width-x}", "fg", 2)]
    # A deliberately sparse technical drawing, constructed as editable paths.
    # Exploded human outline and a leftover screw: a metaphor, not a portrait.
    ox, oy = (36, 233) if mobile else (52, 248)
    def line(d, color="fg", weight=3):
        return f'<path d="{d}" transform="translate({ox} {oy})" fill="none" stroke="{COLORS[color]}" stroke-width="{weight}" stroke-linecap="round" stroke-linejoin="round"/>'
    body += [line("M105 57 C76 52 76 10 101 3 C130 -4 150 12 145 31 L156 43 L144 47 L144 64 L124 64"),
             line("M96 99 L151 99 L171 124 L165 232 L77 232 L80 124 Z"),
             line("M49 111 L30 214 L57 221 L72 117 Z M196 111 L214 214 L188 221 L174 117 Z"),
             line("M93 262 L85 317 L119 317 L123 269 L128 317 L165 317 L156 262 Z"),
             line("M96 120 L120 142 L147 119", "accent"),
             line("M121 73 V90 M121 80 V84 M89 245 H154", "accent", 1),
             line("M293 123 H320 V151 H293 Z M294 134 H257 L241 138 L257 143 H294 M264 130 V147 M274 130 V147 M284 130 V147 M306 124 V150", "accent", 3),
             text(ox+232, oy+241, "ZBYL." if cs else "LEFT OVER.", 20, "accent", 700, mono=True),
             text(ox+232, oy+267, "FUNGUJE I TAK." if cs else "STILL WORKS.", 18, "accent", mono=True)]
    if mobile:
        body += [path("M34 603 H566", "fg"), text(34, 638, spare, 20, "accent", 700, mono=True), text(34, 674, "MAJITEL TO JIŽ PROVEDL." if cs else "OWNER ALREADY DID.", 19, mono=True), text(34, 712, running, 19, mono=True), text(34, 755, "Svatopluk Vít / svatas", 18)]
    else:
        body += [text(640, 303, "30 YEARS IN IT." if not cs else "30 LET V IT.", 42, "fg", 700),
                 text(640, 355, "NO FACTORY RESET." if not cs else "BEZ TOVÁRNÍHO RESETU.", 32, "accent", 700),
                 path("M640 394 H1152", "fg"), text(640, 432, spare, 22, "accent", 700, mono=True),
                 text(640, 481, "MAJITEL TO JIŽ PROVEDL." if cs else "OWNER ALREADY DID.", 21, mono=True), text(640, 513, running, 21, mono=True), text(640, 574, "Svatopluk Vít / svatas", 22)]
    desc = "An absurd service manual: an exploded human outline and a leftover screw labelled Still works. " if not cs else "Absurdní servisní list: rozložený obrys člověka a přebytečný šroubek s popiskem Funguje i tak. "
    return svg(width, height, identity["brand"], desc + status + " " + running, body, lang)


def picture(name, alt, width=1200):
    return (
        '<picture>\n'
        f'  <source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="assets/{name}-mobile-dark.svg">\n'
        f'  <source media="(max-width: 600px) and (prefers-color-scheme: light)" srcset="assets/{name}-mobile-light.svg">\n'
        f'  <source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg">\n'
        f'  <source media="(prefers-color-scheme: light)" srcset="assets/{name}-light.svg">\n'
        f'  <img alt="{escape(alt, quote=True)}" src="assets/{name}-light.svg" width="{width}">\n'
        '</picture>'
    )


def readme(identity, projects, timeline, threads, lang):
    copy = identity[lang]
    cs = lang == "cs"
    nav = "[English](README.md) · **Česky**" if cs else "**English** · [Česky](README.cs.md)"
    header = picture("hero-" + lang, identity["brand"] + " — " + copy["headline"])
    chapters = []
    for thread in threads:
        item = thread[lang]
        opened = " open" if thread["open"] else ""
        links = "\n\n".join(f'[{link["label"]}]({identity["links"][link["key"]]})' for link in item["links"])
        chapters.append(f'''<details{opened}>
<summary><strong>{escape(item["title"])}</strong> — {escape(item["topics"])}</summary>

{item["body"]}

**{copy["lens_label"]}:** {item["lens"]}

{links}

</details>''')
    chapters = "\n\n".join(chapters)
    products = "\n\n".join(f'**{p["name"]}** — {p[lang]["purpose"]}' for p in projects)
    history = "\n\n".join(f'**{e["year"]} · {e[lang]["title"]}** — {e[lang]["detail"]}' for e in timeline)
    return f'''<!-- Generated by scripts/generate.py; edit profile/*.json instead. -->
{header}

{nav}

# {identity["name"]} / {identity["handle"]}

*{copy["experience_mobile"]}*

{copy["intro"]}

## {copy["threads_heading"]}

{copy["threads_hint"]} {copy["work_language"]}

{chapters}

## {copy["gravister_heading"]}

{copy["gravister_intro"]}

{products}

{copy["gravister_note"]}

[{copy["gravister_link"]}]({identity["links"]["gravister"]}) · *{copy["gravister_motto"]}*

<details>
<summary><strong>{escape(copy["timeline_summary"])}</strong></summary>

{copy["timeline_intro"]}

{history}

</details>

## {copy["connect_heading"]}

{copy["connect_body"].format(**identity["links"])}

---

*{copy["footer"]}*
'''


def generate():
    identity = json.loads((ROOT / "profile/identity.json").read_text(encoding="utf-8"))
    projects = json.loads((ROOT / "profile/projects.json").read_text(encoding="utf-8"))
    timeline = json.loads((ROOT / "profile/timeline.json").read_text(encoding="utf-8"))
    threads = json.loads((ROOT / "profile/threads.json").read_text(encoding="utf-8"))
    if [p["name"] for p in projects] != ["Modularis", "Thematis", "Derivis"]:
        raise ValueError("Review the public product list before changing it.")
    if [t["key"] for t in threads] != ["connect", "build", "explain", "observe"]:
        raise ValueError("Review the four public threads before changing them.")
    files = {}
    global COLORS
    for mode, COLORS in PALETTES.items():
        for lang in ("en", "cs"):
            for mobile in (False, True):
                size = "-mobile" if mobile else ""
                files[f"assets/hero-{lang}{size}-{mode}.svg"] = hero(identity, lang, mobile)
    for lang, filename in [("en", "README.md"), ("cs", "README.cs.md")]:
        files[filename] = readme(identity, projects, timeline, threads, lang)
    return files


class ChapterStructure(HTMLParser):
    """Verify native expandable chapters without executing or writing anything."""

    def __init__(self):
        super().__init__()
        self.chapters = []
        self.active = None

    def handle_starttag(self, tag, attrs):
        if tag == "details":
            if self.active is not None:
                raise ValueError("Nested chapters are not supported")
            self.active = {"summaries": 0, "open": "open" in dict(attrs)}
        elif tag == "summary":
            if self.active is None:
                raise ValueError("A summary must belong to a chapter")
            self.active["summaries"] += 1

    def handle_endtag(self, tag):
        if tag == "details":
            if self.active is None or self.active["summaries"] != 1:
                raise ValueError("Each chapter needs exactly one summary")
            self.chapters.append(self.active)
            self.active = None


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
            if tags - {"svg", "title", "desc", "rect", "text", "path"}:
                raise ValueError(f"Unexpected active or external SVG element: {name}")
            for element in root.iter():
                if any(key.startswith("on") or "href" in key for key in element.attrib):
                    raise ValueError(f"External or active SVG attribute: {name}")
        else:
            structure = ChapterStructure()
            structure.feed(content)
            if structure.active is not None or len(structure.chapters) != 5:
                raise ValueError(f"Expected four threads and one history chapter: {name}")
            if [c["open"] for c in structure.chapters] != [True, False, False, False, False]:
                raise ValueError(f"Unexpected initial chapter state: {name}")
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
