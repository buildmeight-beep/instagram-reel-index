"""Bundle each reel's caption, transcript and caption keyword into work/reels.json, the input Claude
reads to write notes.json. Keyword = the word inside quotes after "Comment" in the caption; reels
where that finds nothing are listed so Claude can check the transcript.
    python prepare.py --out ./nateherkai
"""
import argparse, datetime as dt, json, re
from pathlib import Path

ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
OUT = Path(a.out); RAW = OUT / "raw"
Q = r"""[“”"'‘’]"""
CAP_RX = re.compile(r"comm?e?n?t\s*" + Q + r"+\s*([^“”\"'‘’]{1,40}?)\s*" + Q, re.I)

reels = []
for p in json.loads((RAW / "posts-all.json").read_text(encoding="utf-8")):
    c = p.get("caption") or {}
    cap = c.get("text", "") if isinstance(c, dict) else str(c)
    t = RAW / "transcripts" / f"{p['code']}.json"
    tr = ""
    if t.exists():
        d = json.loads(t.read_text(encoding="utf-8"))
        tr = " ".join((x.get("text") or "") for x in (d.get("transcripts") or [])).strip()
    m = CAP_RX.search(cap)
    reels.append({"code": p["code"],
                  "date": dt.datetime.fromtimestamp(p["taken_at"], dt.timezone.utc).strftime("%Y-%m-%d"),
                  "caption_keyword": m.group(1).strip().upper() if m else "",
                  "caption": cap, "transcript": tr,
                  "cover": str((OUT / "thumbs" / f"{p['code']}.jpg").resolve())})
(OUT / "work").mkdir(exist_ok=True)
(OUT / "work" / "reels.json").write_text(json.dumps(reels, ensure_ascii=False, indent=1), encoding="utf-8")
miss = [r["code"] for r in reels if not r["caption_keyword"]]
print(f"{len(reels)} reels -> work/reels.json; {len(reels) - len(miss)} keywords from captions, {len(miss)} to check in transcripts")
