#!/usr/bin/env python3
"""把 work_dashboard 下的看板 markdown 渲染为一个自包含 HTML（看板.html）。

用法：python scripts/build_kanban.py
输出：work_dashboard/看板.html（内联 CSS/JS，双击即可离线查看）
"""
from __future__ import annotations

import datetime
import html
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
PAGES = [
    ("AI-Pet项目全景与进度.md", "项目全景与进度"),
    ("AI-Pet协作看板.md", "协作看板"),
    ("AI-Pet固件联调看板.md", "固件联调看板"),
]
OUT = ROOT / "看板.html"
MD_EXTS = ["tables", "fenced_code", "sane_lists", "toc"]

CSS = """
:root { --bg:#f6f8fa; --card:#fff; --line:#d0d7de; --text:#1f2328; --muted:#656d76;
        --accent:#0969da; --tab-bg:#eaeef2; }
* { box-sizing: border-box; }
body { margin:0; font-family:-apple-system,"Segoe UI","Microsoft YaHei",sans-serif;
       background:var(--bg); color:var(--text); }
header { background:#0d1117; color:#fff; padding:14px 20px; }
header h1 { margin:0; font-size:18px; font-weight:600; }
header .meta { font-size:12px; color:#8b949e; margin-top:4px; }
nav { display:flex; gap:4px; padding:10px 20px 0; background:var(--tab-bg);
      border-bottom:1px solid var(--line); flex-wrap:wrap; }
nav button { border:1px solid var(--line); border-bottom:none; background:transparent;
      padding:8px 16px; font-size:14px; cursor:pointer; border-radius:8px 8px 0 0;
      color:var(--muted); }
nav button.active { background:var(--card); color:var(--accent); font-weight:600; }
main { padding:20px; }
.page { display:none; background:var(--card); border:1px solid var(--line);
        border-radius:0 8px 8px 8px; padding:24px 32px; max-width:1100px; }
.page.active { display:block; }
h1 { font-size:22px; border-bottom:2px solid var(--line); padding-bottom:8px; }
h2 { font-size:18px; border-bottom:1px solid var(--line); padding-bottom:6px; margin-top:28px; }
h3 { font-size:16px; margin-top:22px; }
code { background:#eff1f3; padding:2px 5px; border-radius:4px; font-size:13px; }
pre { background:#0d1117; color:#e6edf3; padding:14px; border-radius:8px; overflow:auto; }
pre code { background:none; color:inherit; padding:0; }
table { border-collapse:collapse; width:100%; margin:14px 0; font-size:13.5px;
        display:block; overflow-x:auto; }
th, td { border:1px solid var(--line); padding:6px 10px; text-align:left;
         vertical-align:top; white-space:nowrap; }
td:last-child, td:nth-last-child(2) { white-space:normal; }
th { background:var(--tab-bg); }
tr:nth-child(even) td { background:#fafbfc; }
blockquote { border-left:4px solid var(--accent); margin:12px 0; padding:4px 14px;
             color:var(--muted); background:#f0f6ff; border-radius:0 6px 6px 0; }
a { color:var(--accent); }
@media (max-width:640px) { .page { padding:14px; } }
"""

JS = """
function show(i) {
  document.querySelectorAll('.page').forEach((p, j) => p.classList.toggle('active', i === j));
  document.querySelectorAll('nav button').forEach((b, j) => b.classList.toggle('active', i === j));
  location.hash = 'p' + i;
}
window.addEventListener('load', () => {
  const m = location.hash.match(/^#p(\\d+)$/);
  if (m) show(+m[1]);
});
"""


def render_page(md_path: Path) -> str:
    text = md_path.read_text(encoding="utf-8")
    return markdown.markdown(text, extensions=MD_EXTS, output_format="html")


def main() -> None:
    pages = []
    for filename, title in PAGES:
        md_path = ROOT / filename
        if not md_path.exists():
            raise SystemExit(f"缺少文件：{md_path}")
        pages.append((title, render_page(md_path)))

    tabs = "\n".join(
        f'<button class="{ "active" if i == 0 else "" }" onclick="show({i})">{html.escape(t)}</button>'
        for i, (t, _) in enumerate(pages)
    )
    sections = "\n".join(
        f'<section class="page{ " active" if i == 0 else "" }">{body}</section>'
        for i, (_, body) in enumerate(pages)
    )
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Pet 协作看板</title>
<style>{CSS}</style>
</head>
<body>
<header>
  <h1>AI Pet 协作看板</h1>
  <div class="meta">生成时间 {now} ｜ 真源为 work_dashboard 仓 markdown，本页只读，修改请改 md 后重新生成</div>
</header>
<nav>{tabs}</nav>
<main>{sections}</main>
<script>{JS}</script>
</body>
</html>
"""
    OUT.write_text(doc, encoding="utf-8")
    print(f"已生成 {OUT}（{OUT.stat().st_size} 字节）")


if __name__ == "__main__":
    main()
