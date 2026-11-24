---
name: gta-deep-dive
description: Make a long-form GTA explainer video from just an idea, in the narrated "deep dive" style (fast, sourced, funny, old-game vs new-game comparisons, chapters as game systems). Researches the facts, finds and downloads footage from YouTube and the web, picks exact moments, writes the script and the edit together, then assembles a finished MP4 with cards, credits, music and sound. Use when someone asks for a GTA video, a GTA 6 vs GTA 5 comparison, a Rockstar game deep dive, or "a video like those GTA explainer channels".
---

# GTA deep dive

You make a complete narrated GTA video from an idea: research, footage, script, voice timing, edit, finished MP4. The style comes from a study of a successful GTA explainer channel; read [the reference breakdown](references/reference-breakdown.md) once before your first video to understand *why* it works.

The two halves are written together. The script decides what footage you look for; what you find in the footage changes the script. Never finish one side alone.

## What you need from the user

Only the idea is required. Ask at most these, once, at the start, and pick sensible defaults if they don't care:
1. **Length**: long (15-25 min, default) or mid (8-12 min).
2. **Narration**: will they record it themselves (default: you deliver the script and wait for `audio/vo.wav`), or do they have a voice tool they want you to use?
3. **Music**: a folder of tracks they have the rights to. Without it the video is made without music and you say so.

Do not ask anything else you can decide yourself.

## Setup (first run)

```bash
python SKILL_DIR/scripts/check_tools.py PROJECT
```

`SKILL_DIR` is this skill's folder; `PROJECT` is a new folder for this video (e.g. `gta-videos/six-stars`). It creates `research/ script/ sources/ scans/ audio/ music/ sfx/ cards/ edit/ renders/`. Install anything reported missing (ask before installing). Run `python SKILL_DIR/scripts/make_sfx.py PROJECT/sfx` if the user has no sound effects.

All scripts take project paths as arguments; run them from anywhere. Run them one at a time and keep the computer usable: no parallel downloads or renders.

## 1. Find the angle

From the idea, write `script/angle.md`:
- The **spine**: one sentence comparing old and new ("GTA 5 was about what you can get away with; GTA 6 is about what you leave behind"). This becomes the ending.
- 5-9 **systems** that become chapters, ordered so each one causes the next (the bridges).
- The **cold-open contrasts** you would like to use (draft).
- Two **open loops**: one structural ("these connect"), one withheld specific item paid off late.
- A list of 3-5 **callback** candidates.

## 2. Research the facts

Use the available web search and browsing tools. Record every claim in `research/facts.md` with source, URL and status (confirmed / reported / seen / rumour). Rules in [sourcing](references/sourcing.md). Find 1-2 quotable lines from real outlets or developers for the authority line and ending. The script may never state a claim more strongly than its status.

## 3. Source and write in one loop

For each chapter, in order:

1. **Shot wishlist.** Draft the chapter's beats in `script/script.md` using the two-column format in [templates/script-template.md](templates/script-template.md): each line of narration with the exact moment that proves it.
2. **Search** for the moments, not the topic:
   ```bash
   python SKILL_DIR/scripts/search.py PROJECT "gta 5 lose wanted level hide no commentary"
   ```
   Prefer official trailers for the new game and no-commentary gameplay for older games.
3. **Download** the best candidate (or only the minutes you need):
   ```bash
   python SKILL_DIR/scripts/fetch.py PROJECT gta5_wanted "URL" --credit "Channel name" --section 3:10-5:40
   ```
   The project budget (12 searches, 20 downloads, 6 s spacing) is enforced. A block (429 / bot check) stops all network requests: continue with what you have and tell the user. Never work around it, never reset the ledger, never raise the budget yourself.
4. **Look inside it:**
   ```bash
   python SKILL_DIR/scripts/scan.py PROJECT/sources/gta5_wanted.mp4 PROJECT/scans/gta5_wanted
   ```
   Open the sheet images and read them. For a promising moment, export full frames (`--frames 192.4,193.1`) and look closely: HUD, characters, which game, whether it is modded.
5. **Log moments** in `sources/moments.md` ([template](templates/moments-template.md)): file, in-point, length, what is visible, game audio worth hearing. Add anything surprising to *Discoveries*.
6. **Rewrite with what you found.** Turn discoveries into better lines; rewrite or cut lines nobody can show; mark deliberate cards. A chapter is done when every specific clause has a moment or a card.

Follow [script grammar](references/script-grammar.md) for the writing: cold open of contrasts, authority line, method line, two open loops, chapters as systems with bridges, feature beats (claim → old-game contrast → source → tag), callbacks, one or two pace modules (fast round, rumour pile, flip side), thesis ending with one comment question. ~190-200 words per spoken minute.

When the whole script is ready, give the user `script/script.md` (narration only, plus a version with visual notes). If they are recording it, stop here until `audio/vo.wav` exists.

## 4. Time the narration

```bash
python SKILL_DIR/scripts/transcribe.py PROJECT/audio/vo.wav PROJECT/audio/vo.json
python SKILL_DIR/scripts/transcribe.py find PROJECT/audio/vo.json "they remember your shirt"
```

Check the transcript against the script (the recording wins if the speaker changed words). Every cut, card and sound accent is placed on these real word times, never estimated from word counts.

## 5. Build the edit

1. **Cards.** Write `cards/cards.json` (example: [templates/cards.example.json](templates/cards.example.json)) and render:
   ```bash
   python SKILL_DIR/scripts/cards.py PROJECT/cards/cards.json PROJECT/cards/out
   ```
   Pick an original theme (colours, fonts) for the user's channel; don't copy another channel's look. Open a few PNGs to check them.
2. **EDL.** Write `edit/edit.json` (schema at the top of `scripts/assemble.py`, example [templates/edit.example.json](templates/edit.example.json)). Follow [edit grammar](references/edit-grammar.md):
   - a new shot on almost every clause (median ~2 s); long holds only for lists, quotes and the ending;
   - "In GTA 5" shows GTA 5, "In GTA 6" shows GTA 6;
   - `credit` on every third-party shot (the credit pill is drawn automatically);
   - quote cards over the same footage blurred (`blur` 18, `dim` 0.45), highlight states switched on the spoken phrase;
   - chapter map in the breath after each bridge line; complete map when the ending says it all connects;
   - music ~20 dB under the voice and steady; one `music_drops` silence for the biggest reveal; short drop + hit when a card lands;
   - clip audio low under narration, raised for the cold open and for sounds that are the point.
3. **Check, then preview:**
   ```bash
   python SKILL_DIR/scripts/assemble.py PROJECT/edit/edit.json PROJECT/renders/v1_preview.mp4 --check
   python SKILL_DIR/scripts/assemble.py PROJECT/edit/edit.json PROJECT/renders/v1_preview.mp4 --preview
   ```
4. **Inspect the preview.** Run `scan.py` on it with `--every 2` for the opening, each chapter start, the big reveal and the ending, and read the sheets: right picture under each line, cards readable and timed, credits present, no black or frozen frames. Fix the EDL and re-render (unchanged shots are cached).
5. **Final render** without `--preview` to a new file name (`v1.mp4`); never overwrite earlier renders.

## 6. Deliver

Give the user:
- the MP4 path,
- `script/script.md`,
- `edit/edit.json` and the cards (editable and re-renderable),
- `*_credits.txt` for the video description (all footage creators and music),
- a short list of anything you could not find footage for and how you handled it.

State what you actually checked (frames inspected, durations, audio present). You cannot listen; say that the mix was checked by levels and placement, and ask the user to watch the reveal and the ending once with sound.

## Hard rules

- Facts: never upgrade a rumour; attribute surprising claims in the sentence.
- Footage: never label a shot as something it is not; never present mods, fan concepts or another game as the real thing.
- Credit every creator whose footage you use; short, transformative excerpts only.
- Downloads: one at a time, within the budget, stop on any block.
- Music: only tracks the user has rights to.
- Keep earlier outputs; write new versions next to them.
