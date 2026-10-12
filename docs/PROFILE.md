# Maintaining Human Source Code

The profile is a small, local publishing pipeline. The English entry point is
`README.md`; `README.cs.md` is its complete Czech alternative. Ten SVG assets
provide light and dark artwork. Essential information is also ordinary Markdown.

## Change the content

Edit the reviewed public content in `profile/identity.json`, `profile/projects.json`
or `profile/timeline.json`. JSON keeps the generator dependency-free. Then run:

```sh
python3 scripts/generate.py
python3 scripts/generate.py --check
```

Commit the inputs, generator and generated outputs together. The check mode never
writes files and fails when generated outputs are stale. Python 3.10+ is sufficient;
the generator uses only the standard library, with no network access or credentials.

## Content boundaries

All three products are introduced by their approved public purpose. Do not copy
private STATE documents, version numbers, roadmaps, commits, screenshots or source
links into these inputs. A public release and its link require an explicit decision;
the generator does not discover or publish releases. No product repositories are
queried by this repository's profile generator or validation workflow.

The profile contains no third-party image widgets, visitor counters, remote fonts,
scripts, embedded HTML in SVG or generated activity statistics. Links are normal
links; the artwork is checked into this repository. The existing snake-generation
workflow is retained unchanged but its image is no longer embedded in the README.

## Review the appearance

Use GitHub's rendered branch README to review both languages, in light and dark
mode and at a narrow width. Relative asset paths follow the current branch. The
`picture` element chooses the palette; the light asset is the fallback. Inspect
the illustrations and check that the text, product purposes and dates agree with
the equivalent Markdown. No information depends on color or an illustration alone.

Local validation checks deterministic output, XML structure, accessible SVG titles
and descriptions, passive SVG elements and local image/language links. It does not
claim to emulate GitHub's renderer or verify public site availability.

## Public references

The identity and professional background are based on the owner's approved profile
content and previously published biography. Its old URL returned HTTP 404 during
this iteration and is intentionally omitted from the profile. The 2004 Linux
milestone and Gravister purposes were supplied by the owner. The
[Root.cz author page](https://www.root.cz/autori/svatopluk-vit/) and
[2008 series summary](https://www.root.cz/clanky/serial-pro-zacatecniky-shrnuti/)
support the writing milestone. Dates mark selected milestones, not product releases.

GitHub documents [theme-aware README images](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/quickstart-for-writing-on-github)
and [relative image and link paths](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes).
