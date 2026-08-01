#!/usr/bin/env python3
"""把 work_dashboard 下的看板 markdown 渲染为一个自包含 HTML（看板.html）。

用法：python scripts/build_kanban.py
输出：work_dashboard/看板.html（内联 CSS/JS，双击即可离线查看）
"""
from __future__ import annotations

import datetime
import html
import re
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
:root { --ink:#16243a; --muted:#66758a; --line:#dfe6ee; --canvas:#f5f7fa; --paper:#fff;
        --blue:#2563a9; --blue-soft:#eaf2fb; --green:#19734b; --green-soft:#e7f6ee;
        --amber:#a45b08; --amber-soft:#fff3df; --red:#b33a3a; --red-soft:#fceced; }
* { box-sizing:border-box; }
body { margin:0; background:var(--canvas); color:var(--ink); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif; line-height:1.6; }
header { background:#172b4d; color:#fff; padding:22px max(24px, calc((100% - 1180px)/2)); }
header h1 { margin:0; font-size:24px; letter-spacing:.01em; }
header .meta { margin-top:3px; color:#cbd7e7; font-size:13px; }
nav { display:flex; gap:24px; padding:0 max(24px, calc((100% - 1180px)/2)); background:var(--paper); border-bottom:1px solid var(--line); overflow-x:auto; }
nav button { appearance:none; border:0; border-bottom:3px solid transparent; background:none; padding:14px 0 11px; white-space:nowrap; color:var(--muted); font:600 14px inherit; cursor:pointer; }
nav button.active { color:var(--blue); border-color:var(--blue); }
main { max-width:1180px; margin:0 auto; padding:30px 24px 56px; }
.page { display:none; }
.page.active { display:block; }
.page.technical { background:var(--paper); border:1px solid var(--line); border-radius:10px; padding:28px 34px; }
.pm-lead { display:flex; justify-content:space-between; gap:28px; align-items:flex-end; padding:2px 0 25px; border-bottom:1px solid var(--line); }
.pm-lead h2 { margin:0; font-size:28px; letter-spacing:-.02em; line-height:1.25; }
.pm-lead p { margin:7px 0 0; color:var(--muted); max-width:680px; }
.health { flex:none; color:var(--green); background:var(--green-soft); padding:6px 11px; font-size:13px; font-weight:700; }
.section-title { margin:30px 0 12px; font-size:16px; }
.workstreams { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); border:1px solid var(--line); background:var(--paper); }
.stream { padding:20px; border-right:1px solid var(--line); border-bottom:1px solid var(--line); }
.stream:nth-child(2n) { border-right:0; }
.stream:nth-last-child(-n+2) { border-bottom:0; }
.stream-top { display:flex; align-items:center; justify-content:space-between; gap:10px; }
.stream h3 { margin:0; font-size:17px; }
.stream p { margin:9px 0 8px; color:var(--ink); font-size:14px; }
.stream small { color:var(--muted); }
.state { display:inline-block; padding:2px 8px; font-size:12px; font-weight:700; white-space:nowrap; }
.state.green { color:var(--green); background:var(--green-soft); }.state.amber { color:var(--amber); background:var(--amber-soft); }.state.red { color:var(--red); background:var(--red-soft); }
.two-column { display:grid; grid-template-columns:1.16fr .84fr; gap:20px; margin-top:20px; }
.panel { background:var(--paper); border:1px solid var(--line); padding:21px; }
.panel h3 { margin:0 0 13px; font-size:16px; }
.timeline { list-style:none; margin:0; padding:0; }.timeline li { padding:0 0 15px 18px; border-left:2px solid #cbd8e7; position:relative; font-size:14px; }.timeline li:last-child { padding-bottom:0; }.timeline li::before { content:""; position:absolute; left:-5px; top:6px; width:8px; height:8px; border-radius:50%; background:var(--blue); }.timeline time { display:block; color:var(--muted); font-size:12px; margin-bottom:2px; }
.priority { margin:0; padding:0; list-style:none; counter-reset:item; }.priority li { counter-increment:item; display:grid; grid-template-columns:27px 1fr; gap:8px; padding:11px 0; border-top:1px solid var(--line); font-size:14px; }.priority li:first-child { border-top:0; padding-top:0; }.priority li::before { content:counter(item); color:var(--blue); font-weight:700; }
.risk { margin:0; padding:0; list-style:none; }.risk li { border-top:1px solid var(--line); padding:11px 0; font-size:14px; }.risk li:first-child { border-top:0; padding-top:0; }.risk strong { display:block; margin-bottom:2px; font-size:13px; color:var(--amber); }
.deployment { margin-top:20px; display:flex; flex-wrap:wrap; gap:10px 24px; padding:15px 18px; background:#edf3f9; color:#38506b; font-size:13px; }.deployment strong { color:var(--ink); }
.diagram { margin:18px 0 28px; padding:22px; border:1px solid var(--line); background:#fff; overflow-x:auto; }.diagram .mermaid { min-width:620px; text-align:center; }
h1 { font-size:25px; padding-bottom:12px; border-bottom:2px solid var(--line); } h2 { font-size:20px; margin-top:32px; padding-bottom:7px; border-bottom:1px solid var(--line); } h3 { font-size:16px; margin-top:24px; } code { background:#eff3f7; padding:2px 5px; border-radius:3px; font-size:13px; } pre { background:#172b4d; color:#eff6ff; padding:14px; overflow:auto; } pre code { background:none; } table { border-collapse:collapse; display:block; overflow-x:auto; width:100%; font-size:13px; margin:14px 0; } th,td { padding:8px 10px; text-align:left; vertical-align:top; border:1px solid var(--line); white-space:nowrap; } td:last-child,td:nth-last-child(2) { white-space:normal; } th { background:#f1f5f9; } blockquote { margin:14px 0; padding:8px 14px; border-left:3px solid var(--blue); background:var(--blue-soft); color:#42546b; } a { color:var(--blue); }
@media(max-width:720px){ header { padding:18px 18px; } main { padding:22px 16px 40px; }.pm-lead { display:block; }.health { display:inline-block; margin-top:15px; }.workstreams,.two-column { grid-template-columns:1fr; }.stream,.stream:nth-child(2n),.stream:nth-last-child(-n+2) { border-right:0; border-bottom:1px solid var(--line); }.stream:last-child { border-bottom:0; }.page.technical { padding:20px 16px; } nav { padding:0 16px; gap:18px; }.diagram { padding:14px; }.diagram .mermaid { min-width:560px; } }
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


def management_overview() -> str:
    return """
<div class="pm-lead"><div><h2>项目交付总览</h2><p>面向项目管理的当前快照：聚焦已交付能力、主线风险与下一步，不以技术任务清单替代项目判断。</p></div><div class="health">线上服务运行正常</div></div>
<h3 class="section-title">工作流状态</h3>
<div class="workstreams">
  <article class="stream"><div class="stream-top"><h3>业务后端</h3><span class="state green">基础能力已上线</span></div><p>设备、人设、历史、管理端资产、分析/外设读取能力可用。</p><small>下一步：完成记忆、知识库运营与 worker 分析产出。</small></article>
  <article class="stream"><div class="stream-top"><h3>用户端</h3><span class="state amber">内测推进中</span></div><p>注册登录、绑定码认领、设备列表/切换与人设设置已部署。</p><small>下一步：历史与首页摘要；正式发布需 HTTPS。</small></article>
  <article class="stream"><div class="stream-top"><h3>运营管理台</h3><span class="state green">运营基础已上线</span></div><p>资产查询、绑定码、人设、历史、外设与分析入口可用。</p><small>下一步：记忆管理、知识库和分析结果消费。</small></article>
  <article class="stream"><div class="stream-top"><h3>设备与语音</h3><span class="state amber">待真机验收</span></div><p>真机语音与单眼情绪联动已验证；人设刷新和外设回传已部署。</p><small>下一步：获取数据回传的端到端落库证据。</small></article>
</div>
<div class="two-column"><section class="panel"><h3>本周关键进展</h3><ol class="timeline"><li><time>2026-08-02</time>后端上线完整人设种子、管理端资产和用户分析/外设读取。</li><li><time>2026-08-02</time>用户端上线设备列表、设备切换与人设设置。</li><li><time>2026-08-02</time>小智服务上线人设定时刷新和眼睛状态异步回传。</li><li><time>已验证</time>真机激活、首轮语音对话与单眼情绪联动可用。</li></ol></section><section class="panel"><h3>下一步（按优先级）</h3><ol class="priority"><li>用真实设备验收人设变更、转写回传、会话结束和眼睛状态落库。</li><li>推进用户端历史与首页摘要，形成连续可用的内测体验。</li><li>补齐记忆、知识库运营与 worker 分析产出，形成运营闭环。</li></ol></section></div>
<div class="two-column"><section class="panel"><h3>当前风险与待决</h3><ul class="risk"><li><strong>主链路尚待验收</strong>数据回传代码已部署，但尚缺真实设备的人设、消息、断开会话和外设状态落库证据。</li><li><strong>运营闭环未完成</strong>记忆、知识库运营和 worker 分析产出尚未实现，当前分析入口可能无数据。</li><li><strong>正式发布条件不足</strong>用户端当前为 HTTP 内测入口，域名、HTTPS 与备案尚未完成。</li></ul></section><section class="panel"><h3>项目管理建议</h3><ul class="risk"><li><strong>以端到端证据验收</strong>以“激活 → 绑定 → 人设变更生效 → 语音对话 → 历史可见”作为下一阶段验收口径。</li><li><strong>区分内测与发布</strong>功能开发可并行；对外发布前单独完成域名、HTTPS、安全与回归验证。</li><li><strong>优先补运营产出</strong>页面与读取接口已具备后，应优先补充记忆、分析和知识库的实际数据生产链路。</li></ul></section></div>
<div class="deployment"><strong>部署状态</strong><span>看板：80（受访问认证保护）</span><span>管理台：8080</span><span>用户端：8081（内测）</span><span>语音与设备服务：8000 / 8002 / 8003</span></div>
"""


def render_page(md_path: Path) -> str:
    text = md_path.read_text(encoding="utf-8")
    rendered = markdown.markdown(text, extensions=MD_EXTS, output_format="html")
    return re.sub(
        r'<pre><code class="language-mermaid">(.*?)</code></pre>',
        lambda match: f'<div class="diagram"><div class="mermaid">{html.unescape(match.group(1))}</div></div>',
        rendered,
        flags=re.DOTALL,
    )


def main() -> None:
    pages = [("项目总览", management_overview(), "pm")]
    for filename, title in PAGES:
        md_path = ROOT / filename
        if not md_path.exists():
            raise SystemExit(f"缺少文件：{md_path}")
        pages.append((title, render_page(md_path), "technical"))

    tabs = "\n".join(
        f'<button class="{ "active" if i == 0 else "" }" onclick="show({i})">{html.escape(t)}</button>'
        for i, (t, _, _) in enumerate(pages)
    )
    sections = "\n".join(
        f'<section class="page {kind}{ " active" if i == 0 else "" }">{body}</section>'
        for i, (_, body, kind) in enumerate(pages)
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
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<script>{JS}</script>
<script>
if (window.mermaid) {{
  mermaid.initialize({{ startOnLoad: true, securityLevel: 'strict', theme: 'base', themeVariables: {{ primaryColor: '#eaf2fb', primaryTextColor: '#16243a', primaryBorderColor: '#2563a9', lineColor: '#66758a', fontFamily: 'Microsoft YaHei, Segoe UI, sans-serif' }} }});
}}
</script>
</body>
</html>
"""
    OUT.write_text(doc, encoding="utf-8")
    print(f"已生成 {OUT}（{OUT.stat().st_size} 字节）")


if __name__ == "__main__":
    main()
