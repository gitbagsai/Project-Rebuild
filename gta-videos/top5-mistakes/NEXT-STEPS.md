# Next steps: Top 5 Mistakes to Avoid in GTA 6

## Done (cloud session, 2026-11-24)
- Angle: `script/angle.md`
- Research: `research/facts.md` (each claim with its status and source; ⚑ = open the article and check the wording before publishing)
- Script: `script/script.md` (with visual notes) and `script/narration.md` (to read aloud), about 1,450 words, roughly 8-8.5 min
- Cards: `cards/cards.json` → `cards/out/*.png` (33 graphics, original orange/teal theme)
- Sound effects: `sfx/` (hit, whoosh, tick, riser)
- Shot list and search plan: `sources/moments.md`

## Your part
1. **Record** `script/narration.md` to `audio/vo.wav`. Small wording changes are fine.
2. **Music (optional):** put tracks you have the rights to in `music/`. Without them the video is made with no music.
3. **On your computer** (needs YouTube): open Claude Code in this repo and say *"continue the GTA 6 mistakes video"*. The `gta-deep-dive` skill is installed in `.claude/skills/`. It will:
   - run `check_tools.py` (needs ffmpeg, `pip install pillow yt-dlp faster-whisper`, plus deno for yt-dlp)
   - search and download the clips in `sources/moments.md`, scan them and log the moments
   - rewrite lines around what the footage shows
   - transcribe your `vo.wav`, build `edit/edit.json`, then render a preview, inspect it and render the final MP4

## Before publishing
- Check every ⚑ fact in `research/facts.md` against the article, or in your own save.
- The Famitsu line is a paraphrase. Keep it off quotation marks unless you find the exact wording.
- Watch the "music out" moment at Number 1 and the ending once with sound.
