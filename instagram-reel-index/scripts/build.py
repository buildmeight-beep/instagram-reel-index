"""Build overview.html (+ overview.csv) from raw/posts-all.json and notes.json.
    python build.py --out ./nateherkai            -> overview.html next to thumbs/
    python build.py --out ./nateherkai --embed    -> overview-standalone.html, covers inside (one file to share)
"""
import argparse, base64, csv, datetime as dt, html, json
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--embed", action="store_true", help="put the cover images inside the HTML file")
a = ap.parse_args()
OUT = Path(a.out)
posts_file = OUT / "raw" / "posts-all.json"
posts = json.loads(posts_file.read_text(encoding="utf-8"))
notes = json.loads((OUT / "notes.json").read_text(encoding="utf-8"))
handle = posts[0].get("user", {}).get("username") or OUT.name
scraped = dt.date.fromtimestamp(posts_file.stat().st_mtime)

rows = []
for p in sorted(posts, key=lambda p: p["taken_at"], reverse=True):
    n = notes.get(p["code"], {})
    rows.append({
        "code": p["code"],
        "date": dt.datetime.fromtimestamp(p["taken_at"], dt.timezone.utc).strftime("%Y-%m-%d"),
        "title": n.get("title", ""), "title_source": n.get("title_source", ""),
        "about": n.get("about", ""), "gain": n.get("gain", ""), "tools": n.get("tools", []),
        "keyword": n.get("keyword", ""), "freebie": n.get("freebie", ""),
        "views": p.get("ig_play_count") or p.get("play_count") or 0,
        "likes": p.get("like_count") or 0, "comments": p.get("comment_count") or 0,
        "seconds": round(p.get("video_duration") or 0),
        "sponsored": bool(p.get("is_paid_partnership")),
        "link": f"https://www.instagram.com/reel/{p['code']}/",
    })

with (OUT / "overview.csv").open("w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows({**r, "tools": "; ".join(r["tools"])} for r in rows)


def cover(code):
    f = OUT / "thumbs" / f"{code}.jpg"
    if a.embed and f.exists():
        return "data:image/jpeg;base64," + base64.b64encode(f.read_bytes()).decode()
    return f"thumbs/{code}.jpg"


e = html.escape
fmt = lambda x: f"{x:,}"
n_kw = sum(1 for r in rows if r["keyword"])
views = sum(r["views"] for r in rows)
d0 = dt.date.fromisoformat(rows[-1]["date"]).strftime("%d %b %Y").lstrip("0")
d1 = dt.date.fromisoformat(rows[0]["date"]).strftime("%d %b %Y").lstrip("0")

trs = "\n".join(f"""<tr>
<td class="c-cover"><a href="{r['link']}" target="_blank" rel="noopener"><img src="{cover(r['code'])}" alt="Cover of the reel from {r['date']}" loading="lazy" width="72" height="128"></a></td>
<td class="c-date num" data-v="{r['date']}">{r['date']}</td>
<td class="c-kw" data-v="{e(r['keyword'])}">{f'<button type="button" class="kw" data-kw="{e(r["keyword"])}" aria-label="Copy keyword {e(r["keyword"])}">{e(r["keyword"])}</button>' if r['keyword'] else '<span class="none">No keyword</span>'}{f'<div class="free">{e(r["freebie"])}</div>' if r['freebie'] else ''}</td>
<td class="c-about" data-v="{e(r['title'])}"><div class="r-title">{e(r['title'])}{' <span class="src" title="No headline on the cover; this is the opening spoken line">spoken</span>' if r['title_source'] == 'spoken' else ''}{' <span class="src">ad</span>' if r['sponsored'] else ''}</div><div class="r-covers">{e(r['about'])}</div>{f'<div class="r-gain"><b>You get:</b> {e(r["gain"])}</div>' if r['gain'] else ''}{'<div class="chips">' + ''.join(f'<span class="chip">{e(t)}</span>' for t in r['tools']) + '</div>' if r['tools'] else ''}</td>
<td class="c-views num" data-v="{r['views']}"><span class="lbl">Views </span>{fmt(r['views'])}</td>
<td class="c-likes num" data-v="{r['likes']}"><span class="lbl">Likes </span>{fmt(r['likes'])}</td>
<td class="c-comments num" data-v="{r['comments']}"><span class="lbl">Comments </span>{fmt(r['comments'])}</td>
<td class="c-len num" data-v="{r['seconds']}">{r['seconds']}s</td>
<td class="c-link"><a href="{r['link']}" target="_blank" rel="noopener">Watch</a></td>
</tr>""" for r in rows)

page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>@{e(handle)} Reels Index</title>
<style>
:root {{ --bg:#f6f7f9; --surface:#fff; --fg:#121826; --muted:#5b6474; --line:#e3e6ec; --accent:#1f4fd1; --chip:#e8eefc; --chip-fg:#163a9c;
  --sans:system-ui,-apple-system,"Segoe UI",sans-serif; --mono:ui-monospace,Consolas,monospace; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#0d1119; --surface:#151b26; --fg:#e8ecf3; --muted:#9aa4b5; --line:#263041; --accent:#8fb0ff; --chip:#1d2a47; --chip-fg:#c7d6ff; color-scheme:dark; }} }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--fg); font:15px/1.5 var(--sans); }}
main {{ max-width:1180px; margin:0 auto; padding:28px 16px 56px; display:grid; gap:20px; }}
header {{ display:grid; gap:6px; }}
.eyebrow {{ font:600 12px var(--mono); letter-spacing:.06em; text-transform:uppercase; color:var(--muted); }}
h1 {{ font-size:clamp(24px,4vw,34px); line-height:1.15; margin:0; }}
.sub {{ color:var(--muted); margin:0; max-width:70ch; }}
.stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; }}
.stat {{ background:var(--surface); border:1px solid var(--line); border-radius:10px; padding:12px 14px; display:grid; gap:2px; }}
.stat b {{ font-size:22px; font-variant-numeric:tabular-nums; }}
.stat span {{ color:var(--muted); font-size:13px; }}
.bar {{ display:flex; flex-wrap:wrap; gap:10px; align-items:center; }}
#q {{ flex:1 1 280px; max-width:440px; min-height:44px; padding:8px 12px; font:inherit; color:var(--fg); background:var(--surface); border:1px solid var(--line); border-radius:8px; }}
#count {{ color:var(--muted); font-size:13px; }}
.wrap {{ background:var(--surface); border:1px solid var(--line); border-radius:12px; overflow-x:auto; }}
table {{ border-collapse:collapse; width:100%; }}
th, td {{ text-align:left; padding:10px 12px; border-bottom:1px solid var(--line); vertical-align:top; }}
th {{ font-size:12px; font-weight:600; color:var(--muted); white-space:nowrap; }}
th button {{ all:unset; cursor:pointer; padding:4px 0; }}
th button[aria-sort="ascending"]::after {{ content:" ↑"; }}
th button[aria-sort="descending"]::after {{ content:" ↓"; }}
.num {{ font-variant-numeric:tabular-nums; white-space:nowrap; }}
.c-about {{ min-width:320px; }}
.c-cover img {{ display:block; width:72px; height:128px; object-fit:cover; border-radius:6px; background:var(--line); }}
.r-title {{ font-weight:700; font-size:16px; line-height:1.35; }}
.r-covers {{ margin-top:4px; }}
.r-gain {{ color:var(--muted); font-size:13px; margin-top:6px; }}
.src {{ font:500 11px var(--mono); color:var(--muted); border:1px solid var(--line); border-radius:4px; padding:0 4px; vertical-align:2px; }}
.chips {{ display:flex; flex-wrap:wrap; gap:4px; margin-top:6px; }}
.chip {{ font-size:12px; background:var(--chip); color:var(--chip-fg); border-radius:999px; padding:1px 8px; }}
.kw {{ font:600 13px var(--mono); background:var(--chip); color:var(--chip-fg); border:0; border-radius:6px; padding:6px 9px; min-height:32px; cursor:pointer; }}
.kw.copied::after {{ content:"  copied"; font-weight:500; }}
.free {{ color:var(--muted); font-size:12px; margin-top:4px; max-width:160px; }}
.none {{ color:var(--muted); font-size:13px; }}
.lbl {{ display:none; }}
a {{ color:var(--accent); }}
a:focus-visible, button:focus-visible, #q:focus-visible {{ outline:2px solid var(--accent); outline-offset:2px; }}
footer {{ color:var(--muted); font-size:13px; max-width:70ch; }}
@media (max-width:720px) {{
  thead {{ display:none; }} table, tbody {{ display:block; }}
  tbody tr {{ display:grid; grid-template-columns:72px minmax(0,1fr); column-gap:12px; row-gap:4px; padding:12px; border-bottom:1px solid var(--line); }}
  td {{ padding:0; border:0; min-width:0; }} .c-cover {{ grid-row:1 / span 7; }} .c-about {{ min-width:0; }}
  .c-date {{ color:var(--muted); font-size:13px; }}
  .c-views, .c-likes, .c-comments {{ font-size:13px; color:var(--muted); }} .lbl {{ display:inline; }} .c-len {{ display:none; }}
  td:not(.c-cover) {{ grid-column:2; }}
}}
</style></head><body><main>
<header>
  <span class="eyebrow">Instagram · @{e(handle)}</span>
  <h1>Every @{e(handle)} reel from {d0} to {d1}</h1>
  <p class="sub">{len(rows)} reels. Each row has the title, what the reel covers, what you get, the tools it names and the word to comment for the free resource. Click a keyword to copy it.</p>
</header>
<section class="stats" aria-label="Totals">
  <div class="stat"><b>{len(rows)}</b><span>reels</span></div>
  <div class="stat"><b>{n_kw}</b><span>with a comment keyword</span></div>
  <div class="stat"><b>{fmt(views)}</b><span>total views</span></div>
  <div class="stat"><b>{fmt(round(views / len(rows)))}</b><span>average views per reel</span></div>
</section>
<div class="bar">
  <input type="search" id="q" placeholder="Search a tool, topic or keyword" aria-label="Search reels">
  <span id="count" aria-live="polite">{len(rows)} reels shown</span>
</div>
<div class="wrap"><table id="t"><thead><tr>
<th>Cover</th><th><button type="button" aria-sort="descending">Date</button></th><th><button type="button">Keyword</button></th>
<th><button type="button">Title · what it covers</button></th><th><button type="button" data-n>Views</button></th>
<th><button type="button" data-n>Likes</button></th><th><button type="button" data-n>Comments</button></th>
<th><button type="button" data-n>Length</button></th><th>Reel</th>
</tr></thead><tbody>
{trs}
</tbody></table></div>
<footer>Unofficial index of public posts, not made or endorsed by @{e(handle)}. Data pulled on {scraped:%d %b %Y}; view and like counts were correct on that day.</footer>
</main>
<script>
const tb = document.querySelector('#t tbody'), count = document.getElementById('count');
document.getElementById('q').addEventListener('input', ev => {{
  const q = ev.target.value.trim().toLowerCase(); let n = 0;
  for (const tr of tb.rows) {{ const hit = !q || tr.textContent.toLowerCase().includes(q); tr.hidden = !hit; if (hit) n++; }}
  count.textContent = n + (n === 1 ? ' reel shown' : ' reels shown');
}});
const heads = [...document.querySelectorAll('th button')];
heads.forEach(b => b.addEventListener('click', () => {{
  const i = b.closest('th').cellIndex, asc = b.getAttribute('aria-sort') === 'descending';
  heads.forEach(h => h.removeAttribute('aria-sort')); b.setAttribute('aria-sort', asc ? 'ascending' : 'descending');
  const num = b.hasAttribute('data-n');
  tb.append(...[...tb.rows].sort((x, y) => {{ const p = x.cells[i].dataset.v, q = y.cells[i].dataset.v; const r = num ? p - q : p.localeCompare(q); return asc ? r : -r; }}));
}}));
tb.addEventListener('click', ev => {{
  const k = ev.target.closest('.kw'); if (!k) return;
  navigator.clipboard.writeText(k.dataset.kw).then(() => {{ k.classList.add('copied'); setTimeout(() => k.classList.remove('copied'), 1400); }});
}});
</script>
</body></html>"""
name = "overview-standalone.html" if a.embed else "overview.html"
(OUT / name).write_text(page, encoding="utf-8")
print(f"{name}: {len(rows)} reels, {n_kw} keywords, {len(page.encode()) / 1e6:.1f} MB")
