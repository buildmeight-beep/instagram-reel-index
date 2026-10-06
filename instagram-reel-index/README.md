# Instagram Reel Index (Claude Code skill)

Turns any Instagram creator's reels into one searchable page: for every reel the title, what it covers, what you get out of it, the tools it names, the comment keyword for the free resource, plus views, likes, comments and length. Search by tool ("MCP", "Higgsfield"), sort by views, click a keyword to copy it.

I built it to keep track of Nate Herk's reels. It works for any public account.

## What you need

| | What | Cost |
|---|---|---|
| 1 | **Claude Code** (any paid Claude plan) | Your normal plan. Claude writes the titles and descriptions, which uses your usage limit (see below) |
| 2 | **Python 3** | Free. Windows: python.org or the Microsoft Store; Mac: usually already there. For the Excel file also run once: `pip install openpyxl pillow` |
| 3 | **Node.js** (only to install the Glasser command) | Free, nodejs.org |
| 4 | **A Glasser account with credit**: glasser.ai | Pay per call. This is the only paid outside tool. It fetches the posts and the reel transcripts from Instagram through its ScrapeCreators connection |

You do **not** need Apify, an Instagram login, or an API key from anyone else.

**My experience with Glasser:** I'm testing it. You get **$1 of free credit** when you sign up, which already covers about 500 reels. I added another $10 to keep going.

## What it cost me

My run on @nateherkai, 3 months (4 Jul to 4 Oct 2026), **114 reels**:

| Item | Amount |
|---|---|
| Glasser calls | 125 (10 pages of posts + 114 transcripts + 1 test) at $0.00188 each |
| **Glasser total** | **$0.235** |
| **Per reel** | **about $0.002** (0.2 cents) |
| Claude (titles + "what you get") | about 270,000 tokens on Sonnet for the two biggest writing steps, inside my normal plan, no extra bill. Reading the 114 cover images was the largest part (about 155,000) |

Rule of thumb: 100 reels ≈ $0.20 on Glasser. Every call is logged with its price in `charges.log`, and the skill tells you the expected cost and waits for your OK before it spends anything.

## Install

1. Download and unzip this folder.
2. Copy the folder `instagram-reel-index` into your Claude Code skills folder:
   - Windows: `C:\Users\<you>\.claude\skills\`
   - Mac/Linux: `~/.claude/skills/`
3. Install the Glasser command once: `npm install -g @glasser-ai/cli@latest`, then run `glasser balance` and log in when it asks.
4. Start Claude Code in any folder and say:
   **"Make an Instagram reel index for @nateherkai for the last 3 months"**

Claude shows the expected cost, scrapes after your OK, writes the descriptions, and gives you:
- `overview.html`: open in your browser
- `overview-standalone.html`: the same page as one file with the covers inside, easy to send to someone
- `overview.xlsx`: Excel with the cover pictures, filters on every column, and a **Tools** sheet that ranks every tool by how many reels name it
- `overview.csv`: plain table for Google Sheets

## Good to know

- Only public posts. Use it for your own research, not to republish someone's content.
- Covers have to be downloaded on the day you scrape (Instagram's image links expire after a few days). The script does this for you.
- Re-running continues where it stopped and does not pay twice for what is already downloaded.
