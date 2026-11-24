# GTA Deep Dive: a Claude skill

Give Claude a GTA video idea. It researches the facts, finds and downloads the footage, picks the exact moments, writes the script around what it finds, times everything to your narration and renders the finished video with cards, on-screen credits, music and sound effects.

The style comes from a frame-by-frame study of a successful GTA explainer video (see `references/reference-breakdown.md`): fast clause-by-clause cutting, "in GTA 5... in GTA 6..." comparisons that always show both games, chapters built around game systems that lead into each other, sourced claims, callbacks, and a mix where the music only gets out of the way for the one moment that matters.

## Install

1. Copy the `gta-deep-dive` folder into your Claude skills folder:
   - Claude Code, all projects: `~/.claude/skills/gta-deep-dive/` (Windows: `C:\Users\YOU\.claude\skills\gta-deep-dive\`)
   - One project only: `YOUR_PROJECT/.claude/skills/gta-deep-dive/`
2. Install the tools (Claude can do this with you; it runs `scripts/check_tools.py` first):
   - [FFmpeg](https://ffmpeg.org/download.html) (full build)
   - Python 3.10+ with `pip install pillow faster-whisper yt-dlp`
3. Restart Claude Code.

## Use

> Make a GTA video: "Every way GTA 6's police are smarter than GTA 5's". About 15 minutes. I'll record the voiceover myself. My music is in D:\music\royalty-free.

Claude will:
1. Write the angle (thesis, chapters, open loops) and research the facts with sources.
2. Search YouTube for each moment it needs, download within a safe budget, scan the clips and log usable moments.
3. Write the script and rewrite it as the footage reveals better lines.
4. Hand you the script to record (or use a voice tool you name), then time every cut to your recording.
5. Render the cards, build the edit, render a preview, inspect it, fix it and render the final MP4.

You get the video, the script, an editable edit file (`edit/edit.json`), the card files, and a credits list for your description.

## What's inside

| Path | What it is |
|---|---|
| `SKILL.md` | The workflow Claude follows |
| `references/reference-breakdown.md` | The style study: what happens at each moment and why |
| `references/script-grammar.md` | How the script is built |
| `references/edit-grammar.md` | How picture and sound are cut |
| `references/sourcing.md` | Where footage and facts come from, the write-and-source loop, download and rights rules |
| `scripts/` | Search, download, scan, transcribe, card renderer, sound effects generator, assembler |
| `templates/` | Script, moments log, cards and edit examples |

## Good to know

- **Downloads are limited on purpose** (12 searches, 20 downloads, one at a time, 6 s apart per project). If YouTube shows a rate limit or bot check, Claude stops downloading and finishes with what it has. You can change the limits in `PROJECT/sources/budget.json`.
- **Credit and rights.** Every third-party clip gets an on-screen credit and a line in the credits file. Commentary use of short clips is common on YouTube, but it is not a guarantee against claims; use music you own the rights to, prefer official trailers, and ask creators when you use a lot of their footage.
- **Make it yours.** Change the colours and fonts in `cards/cards.json` (the `theme` block) so your channel has its own look.
- Claude can see frames but cannot listen. Watch the finished video once with sound, especially the big reveal and the ending.
