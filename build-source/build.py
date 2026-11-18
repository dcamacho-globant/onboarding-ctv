"""Expand the page parts into one plain HTML document.

Usage: python3 -I build.py <output.html>

Each {{C:path:line}} / {{P:path:line|shown}} token becomes a link to the file on
the main branch. If REPO (path to the nfl-fe checkout) is set, every file and
line is also verified; otherwise the check is skipped.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("REPO", "")
BASE = "https://github.com/nfl/nfl-fe/blob/main/"
PFX = {"C": "packages/apps/Connected/", "P": "packages/"}
PAT = re.compile(r"\{\{([CP]):([^:|}]+):(\d+)(?:\|([^}]*))?\}\}")
SECTIONS = [
    ("part1.html", False), ("part2.html", True), ("part3.html", False),
    ("part4.html", False),
]
EXTRA = ["part5.html", "part6.html", "part7.html", "part8.html",
         "part9a.html", "part9b.html", "part10a.html", "part10b.html"]
problems = []
count = 0


def expand(text, svg):
    def repl(m):
        global count
        kind, path, line, shown = m.group(1), m.group(2), int(m.group(3)), m.group(4)
        full = PFX[kind] + path
        if REPO:
            fp = os.path.join(REPO, full)
            if not os.path.isfile(fp):
                problems.append("NO FILE " + full)
            else:
                lines = open(fp, errors="replace").read().split("\n")
                if line > len(lines) or not lines[line - 1].strip():
                    problems.append("BAD LINE %s:%d" % (full, line))
        count += 1
        label = shown or "%s:%d" % (path, line)
        href = BASE + full + "#L%d" % line
        if svg:
            return '<a href="%s" target="_blank" rel="noopener">%s</a>' % (href, label)
        return '<a href="%s" target="_blank" rel="noopener"><code>%s</code></a>' % (href, label)
    return PAT.sub(repl, text)


def read(name):
    with open(os.path.join(HERE, name)) as f:
        return f.read()


out = ""
head4, tail4 = read("part4.html").split("<script>", 1)
for name, svg in SECTIONS[:3]:
    out += expand(read(name), svg)
out += expand(head4, False)
for name in EXTRA:
    out += expand(read(name), False)
out += "<script>" + tail4

with open(sys.argv[1], "w") as f:
    f.write(out)
print("refs:", count, "problems:", problems)
if PAT.search(out):
    sys.exit("unexpanded tokens remain")
sys.exit(1 if problems else 0)
