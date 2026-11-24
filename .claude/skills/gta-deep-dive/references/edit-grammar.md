# Edit grammar

The narration drives everything. The picture's job is to *prove* each clause as it is spoken; the sound's job is to stay out of the way except when a moment needs weight.

## Picture

**Cut rate.** Median shot ~2 s, average under 3 s. Cut on the clause, not on the beat of the music. Exceptions are deliberate:
- Hold 8-17 s when the narration is a list or an emotional summary (the viewer listens; the picture should stop asking for attention).
- Hold for as long as a quote card is being read.
- Go faster (0.7-1.2 s) only for montages that *mean* volume: "I went through everything", fast rounds, ending recaps.

**One clause, one proof.** For each clause ask: what would someone need to see to believe this? Pick the exact moment: the HUD element, the animation, the place, the character. Generic driving footage is the last resort, and never for a specific claim.

**Old vs new is shown, not said.** Whenever the script says "In GTA 5..." or names an older game, the picture is that older game. Then cut to the new game on the "In GTA 6..." line. The contrast works because the viewer recognises the older look instantly.

**Order inside a shot.** Choose `in` so that the action the clause describes happens in the first half of the shot, while the words are still on screen. If an action (crash, punch, bust) is the payoff, let the shot start just before it and let it complete.

**Cards** (rendered with `scripts/cards.py`, placed as full-frame overlays):

| Use | Card | Placement |
|---|---|---|
| A press quote, developer statement, report | `quote` with highlight states | Over the same gameplay shot blurred (`"blur": 18, "dim": 0.45`). Advance the highlight when that phrase is spoken. |
| A headline or outlet announcement | `headline` | Same blurred backdrop. 2-4 s. |
| A person or a magazine cover | `photo` (with name and role) | Blurred backdrop. Show when the person is first named. |
| Naming an activity, place, or which game this is | `label` (lower-left chip) | On the footage, for the full shot. |
| Flipping the meaning of a shot ("not in GTA 6", "cut", "rumour") | `stamp` | On the footage, landing on the key word. |
| A number change or comparison | `stat` | Blurred or plain backdrop, 2-3 s, appears on the number word. |
| A rule ("three days in a row") | `checklist` | On blurred footage of the activity. |
| A HUD detail (wanted level, star loss) | `stars`, `meter` | Over blurred or darkened footage. |
| A new chapter | `chapter` (systems map) | Full-screen, ~2-3 s, in the breath between the bridge line and the chapter's first line. |
| The ending ("they all connect") | `chapter` with `"complete": true` | When the narration states the connection. |

Keep cards original: your own palette and fonts (set in the cards theme). Do not copy another channel's graphics.

**Credit every third-party clip.** Give each shot from someone else's video a `credit`; the assembler draws a small "FOOTAGE · NAME" pill top-right for the shot. Official trailers can carry the publisher ("ROCKSTAR GAMES").

**Repetition.** The same shot may only come back on purpose (a callback in the ending). Never reuse a shot with a different label to cover missing footage.

**Reframing.** `zoom` 1.1-1.4 to isolate a HUD element or a face; set `focus` to that point. Stills (screenshots, covers) get `push` 1.03-1.08 so they are never frozen.

## Sound

**Voice** on top, always intelligible. Music bed about 20 dB under the voice (`"gain_db": -20` with the assembler's level matching), constant across the video. Do not duck and swell under every sentence.

**Game audio** from the clips is kept low under narration (`game_db` -24 to -30) so the world feels alive. Raise it (`-8` to `-12`) when:
- the video opens cold on gameplay (first 0.5-2 s before the first word),
- a shot's sound *is* the point (a crash, a gunshot that answers a line, a character's reaction line), placed in a breath.

**Accents.** When a card, chapter map or stamp lands, add a short music drop (0.2-0.3 s) just before it and a hit or whoosh on it. One accent per idea, not per cut.

**The big reveal gets silence.** Remove the music entirely (a `music_drops` entry of 4-8 s) under the single most important line in the video, usually the payoff of the withheld open loop. Use it once.

**Staccato lists.** For one-word sentences ("Trays. Webs. No wheel at all."), chop the music with short drops between the words instead of adding cuts.

**Music choice.** Mid-tempo, warm, synth-led or lo-fi instrumentals that loop well; avoid vocals. Change track at chapter boundaries or at mood changes (the rumour pile, the flip side, the ending). Use music you have the right to use. Licensed songs from the game's radio will trigger copyright claims.

## Pauses

There is almost no dead air in this style. A "pause" is made by:
- the music dropping out,
- a shot holding while the narrator takes a normal breath,
- a chapter card landing in the breath between two lines.

Do not insert silent gaps into the narration. If a line needs to land, leave the breath in the recording and give the picture something to show during it.

## Timing reference

| Element | Typical length |
|---|---|
| Gameplay proof shot | 1.5-3 s |
| Montage shot | 0.7-1.2 s |
| Chapter map | 2-3 s |
| Quote card | Reading time of the quote at narration speed, plus 0.5 s |
| Stat / checklist | 2-3 s, enters on the number word |
| Long hold (lists, endings) | 8-17 s |
| Cold-open game-audio lead | 0.3-1.5 s |

## Final checks

- Every clause that names a specific thing has a shot of that thing, or a deliberate card.
- Old-game lines show the old game.
- No label claims something the shot does not show.
- Highlights advance with the words, not before them.
- Music is gone under the big reveal and back afterwards.
- Credits present on every third-party shot; sources listed for the description.
