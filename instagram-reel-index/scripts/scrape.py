"""Fetch every post of an Instagram account back to a date, the reel transcripts and the cover images.

Uses the Glasser CLI (provider ScrapeCreators). Every call is logged with its charge in charges.log.
    python scrape.py --handle nateherkai --since 2026-07-04 --out ./nateherkai
Re-running continues where it stopped: pages, transcripts and covers already on disk are skipped.
"""
import argparse, datetime as dt, json, re, shutil, subprocess, sys, urllib.request
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--handle", required=True)
ap.add_argument("--since", required=True, help="oldest post date to keep, YYYY-MM-DD")
ap.add_argument("--out", required=True)
ap.add_argument("--glasser", help="path to the glasser command if it is not on PATH")
a = ap.parse_args()

G = a.glasser or shutil.which("glasser")
if not G:
    sys.exit("Glasser CLI not found. Install it: npm install -g @glasser-ai/cli@latest, then run: glasser balance")
OUT = Path(a.out); RAW = OUT / "raw"; RAW.mkdir(parents=True, exist_ok=True)
LOG = OUT / "charges.log"
CUTOFF = dt.datetime.fromisoformat(a.since).replace(tzinfo=dt.timezone.utc).timestamp()


def run(endpoint, payload, out):
    if out.exists():
        return json.loads(out.read_text(encoding="utf-8"))
    cmd = [G, "run", "-p", "scrapecreators", "-e", endpoint, "--endpoint-version", "2",
           "-i", json.dumps(payload), "-o", str(out)]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    meta = {k: (re.search(rf"^{k}:\s+(.+)$", p.stdout + "\n" + p.stderr, re.M) or [None, None])[1]
            for k in ("Status", "Charge")}
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"endpoint": endpoint, "input": payload, "exit": p.returncode, **meta}) + "\n")
    print(endpoint, "->", meta.get("Status"), meta.get("Charge"), flush=True)
    if p.returncode != 0 or not out.exists():
        print(p.stderr.strip()[:500], file=sys.stderr)
        return None
    return json.loads(out.read_text(encoding="utf-8"))


# 1) posts, 12 per page, newest first, until the cutoff date
items, n, payload = [], 1, {"handle": a.handle, "trim": True}
while True:
    page = run("/v2/instagram/user/posts", payload, RAW / f"posts-p{n}.json")
    if not page or not page.get("items"):
        sys.exit(f"posts page {n} failed; see charges.log")
    items += page["items"]
    if min(i["taken_at"] for i in page["items"]) < CUTOFF or not page.get("more_available") or not page.get("next_max_id"):
        break
    n += 1
    payload = {"handle": a.handle, "trim": True, "next_max_id": page["next_max_id"]}

seen, keep = set(), []
for i in items:
    if i["taken_at"] >= CUTOFF and i["code"] not in seen:
        seen.add(i["code"]); keep.append(i)
(RAW / "posts-all.json").write_text(json.dumps(keep, ensure_ascii=False), encoding="utf-8")
print(f"{n} pages, {len(keep)} posts since {a.since}", flush=True)

# 2) transcripts (videos only) and 3) covers (Instagram image links expire within days, so fetch now)
(RAW / "transcripts").mkdir(exist_ok=True); (OUT / "thumbs").mkdir(exist_ok=True)
for i in keep:
    if i.get("media_type") == 2:
        run("/v2/instagram/media/transcript", {"url": f"https://www.instagram.com/reel/{i['code']}"},
            RAW / "transcripts" / f"{i['code']}.json")
    thumb = OUT / "thumbs" / f"{i['code']}.jpg"
    cands = (i.get("image_versions2") or {}).get("candidates") or []
    if not thumb.exists() and cands:
        req = urllib.request.Request(cands[0]["url"], headers={"User-Agent": "Mozilla/5.0"})
        try:
            thumb.write_bytes(urllib.request.urlopen(req, timeout=30).read())
        except Exception as e:
            print("cover failed", i["code"], e, file=sys.stderr)

total = sum(float(json.loads(l)["Charge"].split()[0].lstrip("$")) for l in LOG.read_text(encoding="utf-8").splitlines()
            if json.loads(l).get("Charge"))
print(f"done. Glasser spend logged in charges.log: ${total:.4f}")
