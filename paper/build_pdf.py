"""paper.md -> paper.html -> paper.pdf, laid out like the Apart report template (ruled title, author grid, "With Apart Research",
abstract, footnote, numbered sections; the template's font, Old Standard TT, is loaded from Google Fonts and falls back to Times).
Run: uv run --with markdown python paper/build_pdf.py  (needs Google Chrome for the PDF step)"""
import pathlib, re, subprocess, markdown

P = pathlib.Path(__file__).parent
src = (P / 'paper.md').read_text()
meta, body = re.match(r'^---\n(.*?)\n---\n(.*)$', src, re.S).groups()
title = re.search(r'title: "(.*)"', meta).group(1).replace('\\"', '"')
authors = [re.match(r'\s*(.*?)\s*\((.*)\)\s*$', a).groups() for a in re.search(r'author: "(.*)"', meta).group(1).split(';')]
author_html = ''.join(f'<div class="au">{n}<br>{aff}</div>' for n, aff in authors)
note = re.search(r'note: "(.*)"', meta).group(1)

# python-markdown needs a blank line before a list and 4-space nesting; the source uses GitHub style
LIST = re.compile(r'^\s*(?:[-*]|\d+\.) ')
lines = []
for line in body.split('\n'):
    if LIST.match(line) and lines and lines[-1].strip() and not LIST.match(lines[-1]) and not lines[-1].startswith(' '):
        lines.append('')
    indent = len(line) - len(line.lstrip(' '))
    lines.append(' ' * (indent * 2) + line.lstrip(' ') if LIST.match(line) and indent else line)
body = '\n'.join(lines)

# inline the SVG figures so the HTML is self-contained
def figure(m):
    cap, path = m.group(1), m.group(2)
    svg = (P / path).read_text().replace("width='640'", "width='100%'", 1)
    return f'<figure>{svg}<figcaption>{markdown.markdown(cap)[3:-4]}</figcaption></figure>'
body = re.sub(r'!\[(.*?)\]\((figures/[^)]+\.svg)\)', figure, body)
abstract, rest = re.search(r'# Abstract\n(.*?)\n(# 1\..*)$', body, re.S).groups()
html_body = markdown.markdown(rest, extensions=['tables'])
# keep each table's caption on the same page as the table
html_body = re.sub(r'(<p><strong>Table \d+\..*?</p>\s*<table>.*?</table>)', r'<div class="tbl">\1</div>', html_body, flags=re.S)
abstract_html = markdown.markdown(abstract)

css = """
@page { size: Letter; margin: 0.9in 0.9in; }
body { font-family: BODYFONT; font-size: BODYSIZE; line-height: BODYLH; color: #111; }
.titleblock { border-top: 3px solid #000; border-bottom: 1px solid #000; padding: 18px 0 16px; margin: 0 0 16px; }
h1.title { font-family: 'Old Standard TT', 'Times New Roman', serif; font-size: 17pt; text-align: center; margin: 0; line-height: 1.2; break-after: auto; }
h1.title sup, .fn sup { font-size: 60%; font-weight: normal; }
.authors { text-align: center; font-family: 'Old Standard TT', 'Times New Roman', serif; font-size: 10pt; margin-bottom: 6px; }
.au { display: inline-block; margin: 0 22px; line-height: 1.25; }
.with { text-align: center; font-family: 'Old Standard TT', 'Times New Roman', serif; font-size: 10pt; margin-bottom: 12px; line-height: 1.25; }
.abstract { margin: 0 0.75in 8px; font-size: 10pt; text-align: justify; }
.abstract h2 { font-family: 'Old Standard TT', 'Times New Roman', serif; font-size: 12pt; margin: 2px 0 6px; text-align: center; }
.fn { font-size: 8.5pt; margin: 0 0 12px; } .fn hr { width: 1.6in; margin: 0 0 3px; border: 0; border-top: 1px solid #000; }
h1, h2, h3 { font-family: 'Old Standard TT', 'Times New Roman', serif; }
h1 { font-size: 13pt; margin: 16px 0 6px; break-after: avoid; } h2 { font-size: 11.5pt; margin: 12px 0 4px; break-after: avoid; }
p { margin: 4px 0; } li { margin: 1px 0; } ul, ol { margin: 2px 0 3px 16px; padding-left: 4px; } li > ul, li > ol { margin: 0 0 0 14px; }
table { border-collapse: collapse; font-size: 9pt; margin: 6px 0; width: 100%; }
th, td { border: 1px solid #999; padding: 3px 6px; vertical-align: top; text-align: left; }
figure { margin: 8px 0; page-break-inside: avoid; } .tbl { break-inside: avoid; } figure svg { display: block; max-width: 74%; height: auto; margin: 0 auto; } figure:first-of-type svg { max-width: 100%; }
figcaption { font-size: 9pt; margin-top: 2px; }
blockquote { font-size: 9pt; margin: 4px 12px; color: #333; }
code { font-size: 9pt; }
"""
import os
css = css.replace('BODYFONT', os.environ.get('BODYFONT', "'Old Standard TT', 'Times New Roman', Times, serif")).replace('BODYSIZE', os.environ.get('BODYSIZE', '10pt')).replace('BODYLH', os.environ.get('BODYLH', '1.24'))
html = f"""<!doctype html><html><head><meta charset="utf-8"><title>{title}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Old+Standard+TT:ital,wght@0,400;0,700;1,400&display=block">
<style>{css}</style></head><body>
<div class="titleblock"><h1 class="title">{title}<sup>1</sup></h1></div>
<div class="authors">{author_html}</div>
<div class="with"><b>With</b><br>Apart Research</div>
<div class="abstract"><h2>Abstract</h2>{abstract_html}</div>
<div class="fn"><hr><sup>1</sup> {note}</div>
{html_body}
</body></html>"""
(P / 'paper.html').write_text(html)
chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
subprocess.run([chrome, '--headless', '--disable-gpu', '--no-pdf-header-footer', '--virtual-time-budget=8000', f'--print-to-pdf={P / "paper.pdf"}', (P / 'paper.html').as_uri()],
               check=True, capture_output=True, timeout=120)
print('wrote', P / 'paper.pdf')
