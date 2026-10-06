---
name: instagram-reel-index
description: Build a searchable overview page of every reel an Instagram account posted since a date, with title, what each reel covers, what the viewer gets, the tools it names, the comment keyword for the free resource, and views/likes/comments. Use when the user asks to index, overview, catalogue or scrape the reels of an Instagram creator.
---

# Instagram reel index

Input: an Instagram handle and a start date (default: 3 months back). Output folder `./instagram-index/<handle>/` with
`overview.html` (open in a browser), `overview-standalone.html` (one file with covers inside, to share), `overview.xlsx` (Excel with cover pictures and a Tools sheet) and `overview.csv`.

Scripts live next to this file in `scripts/`. Run them with the user's Python (`python`, or `py` on Windows).

## 1. Check Glasser (paid data, about $0.002 per reel)

Run `glasser balance`.
- Command not found: install with `npm install -g @glasser-ai/cli@latest` (or `curl -fsSL https://glasser.ai/install.sh | sh`), then `glasser balance` again; it walks the user through login.
- Never ask the user to paste a key into the chat.
- Before scraping, tell the user the expected cost: calls = (posts ÷ 12, rounded up) + one per reel, at $0.00188 each. A creator posting daily for 3 months is about 125 calls, about $0.24. Wait for their go.

## 2. Scrape

```
python scripts/scrape.py --handle <handle> --since <YYYY-MM-DD> --out ./instagram-index/<handle>
```
If `glasser` is installed but not on PATH, add `--glasser <full path to the glasser command>`. Fetches posts, reel transcripts and cover images; logs every charge to `charges.log`. Safe to re-run; it skips what is on disk. Covers must be fetched on the same day (Instagram image links expire).

## 3. Prepare

```
python scripts/prepare.py --out ./instagram-index/<handle>
```
Writes `work/reels.json`: per reel the date, caption, transcript, cover image path and the keyword found in the caption.

## 4. Write notes.json (Claude does this)

Read `work/reels.json` and write `./instagram-index/<handle>/notes.json`:

```json
{"<code>": {
  "title": "cover headline, or the opening spoken line",
  "title_source": "cover | spoken",
  "about": "one line: what the reel covers",
  "gain": "one line, max ~18 words: what the viewer concretely gets (a skill, a workflow, a business idea). 'Opinion piece, no tool or method' if nothing actionable",
  "tools": ["only products, apps, models, MCP servers named in caption or transcript, max 5"],
  "keyword": "comment keyword: caption_keyword if present, else the word the creator says to comment in the transcript, else empty",
  "freebie": "what commenting the keyword sends, max ~8 words; 'Resource link (unspecified)' if not said; empty if no keyword"
}}
```

Rules:
- **Title:** open the cover image (Read tool) and use the printed headline in Title Case. Covers without a headline (face only, screenshot, or filler like "Stitch Incoming..") get the first sentence of the transcript, trimmed to ~100 characters, with `title_source: "spoken"`.
- Only facts in the caption, transcript or cover. Never invent tools or freebies. Fix obvious transcription errors of product names ("cloud code" = Claude Code).
- For more than ~30 reels, split the work across subagents on a cheaper model (e.g. Sonnet), about 40 reels each, one batch at a time, then merge. Reading covers costs the most tokens.
- Check the result: valid JSON, one entry per reel code in `work/reels.json`.

## 5. Build

```
python scripts/build.py --out ./instagram-index/<handle>
python scripts/build.py --out ./instagram-index/<handle> --embed
python scripts/excel.py --out ./instagram-index/<handle>
```
`excel.py` needs `pip install openpyxl pillow` (install it if the import fails).
Then tell the user the full `file:///` path of `overview.html`, the size of `overview-standalone.html`, and the total from `charges.log`. Delete `work/` at the end.
