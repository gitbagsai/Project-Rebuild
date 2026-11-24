# Sourcing footage and facts

## Where things come from

| Need | First choice | Fallbacks |
|---|---|---|
| Facts about a new game | Developer posts (Rockstar Newswire, official site), developer interviews | Hands-on previews (magazines, big outlets), then reputable reporting. Fan wikis only as leads. |
| New-game footage | Official trailers and official gameplay videos | Previews' embedded footage, creators' analysis videos (credited) |
| Old-game footage (GTA 5, 4, San Andreas, RDR2) | Gameplay creators' no-commentary videos, credited | Your own recordings if you have the game |
| A specific mechanic | Search the mechanic + game ("gta 5 wanted level escape no commentary") | Mod showcase videos show systems clearly, but label modded footage |
| HUD / UI details | Frame-grab from official footage, then redraw as a card | `stars`, `meter`, `checklist` cards |
| People | Official press photos, the outlet's interview images | A `photo` card with the name and role only |
| Quotes | The original article or interview | Re-typeset it with the `quote` card; never paste a screenshot of someone else's design |

Use whatever web search and browser tools are available in your Claude environment for facts and for finding non-YouTube pages. `scripts/search.py` searches YouTube through yt-dlp.

## Facts file

Keep `research/facts.md`: one line per claim with the source URL, who said it, and its status: **confirmed** (developer), **reported** (preview/outlet), **seen** (visible in official footage, describe it), **rumour**. The script may only state a fact at its status. When sources disagree, say so in the script or leave the claim out.

## Write and source in one loop

Do not write the full script and then hunt for pictures, and do not collect footage blindly. Alternate:

1. **Outline → shot wishlist.** For each beat in the outline, write the exact moment that would prove it ("GTA 5: cops lose you after you drive around a block, stars flash and disappear").
2. **Search for the wishlist, not for the topic.** Queries name the moment: `"gta 5" lose wanted level hide no commentary`, `gta 6 trailer 2 gas station`, `san andreas gym workout`.
3. **Scan before choosing.** Download a candidate (within the budget), then run `scripts/scan.py` and look at the sheets. Write down every usable moment with its timestamp in `sources/moments.md`: what is visible, how long it lasts, whether the game audio is useful.
4. **Let the footage edit the script.** While scanning you will find moments you did not plan: an NPC reaction, a HUD message, a funny fail. Log them under *Discoveries*. If one proves a point better than your line, rewrite the line around it. If a planned line has no footage after a real search, rewrite the line so it can be shown, move it to a card, or cut it.
5. **Repeat per chapter.** Lock a chapter's script only when every specific clause has a moment or a deliberate card.

Example of the loop: the outline says "cars can run out of fuel". Scanning a trailer reveals a shot where a character taps a fuel gauge at a pump. The line becomes "Every car has a working fuel gauge" landing on that exact shot, and the next line ("running out can leave you stranded mid-chase") gets a chase shot.

## Download rules (protect the user's connection and account)

The bundled tools enforce a per-project budget in `sources/budget.json` (created on first use):

| Setting | Default |
|---|---|
| `max_searches` | 12 |
| `max_downloads` | 20 (failed attempts count) |
| `min_gap_seconds` | 6 between one download finishing and the next starting |
| `max_height` | 1080 |

- One download at a time. No parallel downloads, no background footage library.
- Prefer `--section` downloads (only the minutes you need) for long videos.
- On a 429, a bot check, a sign-in or CAPTCHA request, the tools stop and record a block. Do not retry, switch downloaders, use cookies, proxies or a VPN to get around it. Continue with footage already downloaded and tell the user.
- Only the user may raise the budget (by editing `budget.json` themselves or telling you to). Never delete the ledger or start a new project folder to reset it.
- Reuse downloaded footage across beats before searching again.

## Rights and credit

This style is commentary: narrated analysis that transforms short clips. That supports a fair-use argument in many places, but it is not a guarantee, and platforms make their own decisions.

- Use short excerpts that serve a specific line. Do not run someone's video for long stretches.
- Credit every third-party clip on screen (the assembler does this from `credit`) and list sources in the description (the assembler writes `credits.txt`).
- Prefer official trailers and footage from creators who allow reuse with credit; ask permission for heavy use.
- Check the game publisher's video policy for monetisation of game footage.
- Use music you have rights to. No radio songs from the game.
- Do not present modded footage, fan concepts or other games as the real thing. Label them.
