"""paper.md -> paper.html -> paper.pdf, laid out like the Apart report template (title, authors, abstract box, numbered sections).
Run: uv run --with markdown python paper/build_pdf.py  (needs Google Chrome for the PDF step)"""
import pathlib, re, subprocess, markdown

P = pathlib.Path(__file__).parent
src = (P / 'paper.md').read_text()
meta, body = re.match(r'^---\n(.*?)\n---\n(.*)$', src, re.S).groups()
title = re.search(r'title: "(.*)"', meta).group(1).replace('\\"', '"')
author = re.search(r'author: "(.*)"', meta).group(1)
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
body { font-family: 'Times New Roman', Times, serif; font-size: 10.5pt; line-height: 1.3; color: #111; }
h1.title { font-size: 17pt; text-align: center; margin: 0 0 10px; line-height: 1.2; }
.authors { text-align: center; font-size: 10.5pt; margin-bottom: 14px; }
.abstract { border: 1px solid #999; padding: 8px 14px; margin: 0 0 14px; font-size: 10pt; }
.abstract h2 { font-size: 11pt; margin: 2px 0 4px; text-align: center; }
h1 { font-size: 13pt; margin: 16px 0 6px; break-after: avoid; } h2 { font-size: 11.5pt; margin: 12px 0 4px; break-after: avoid; }
p { margin: 4px 0; } li { margin: 1px 0; } ul, ol { margin: 2px 0 3px 16px; padding-left: 4px; } li > ul, li > ol { margin: 0 0 0 14px; }
table { border-collapse: collapse; font-size: 9pt; margin: 6px 0; width: 100%; }
th, td { border: 1px solid #999; padding: 3px 6px; vertical-align: top; text-align: left; }
figure { margin: 8px 0; page-break-inside: avoid; } .tbl { break-inside: avoid; } figure svg { display: block; max-width: 74%; height: auto; margin: 0 auto; } figure:first-of-type svg { max-width: 100%; }
figcaption { font-size: 9pt; margin-top: 2px; }
blockquote { font-size: 9pt; margin: 4px 12px; color: #333; }
code { font-size: 9pt; }
.note { font-size: 8.5pt; color: #444; text-align: center; margin-bottom: 10px; }
"""
html = f"""<!doctype html><html><head><meta charset="utf-8"><title>{title}</title><style>{css}</style></head><body>
<h1 class="title">{title}</h1>
<div class="authors">{author}<br>With Apart Research</div>
<div class="note">{note}</div>
<div class="abstract"><h2>Abstract</h2>{abstract_html}</div>
{html_body}
</body></html>"""
(P / 'paper.html').write_text(html)
chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
subprocess.run([chrome, '--headless', '--disable-gpu', '--no-pdf-header-footer', f'--print-to-pdf={P / "paper.pdf"}', (P / 'paper.html').as_uri()],
               check=True, capture_output=True, timeout=120)
print('wrote', P / 'paper.pdf')
