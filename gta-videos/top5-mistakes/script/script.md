# Top 5 Mistakes to Avoid in GTA 6 (draft v1, visual notes)

Spine: In GTA 5, a mistake cost you a hospital trip. In GTA 6, a mistake follows you.
Open loops: (1) "these five feed into each other" → paid off in the ending (complete map). (2) "one mission in Chapter 1 takes your car, your house and your wallet" → paid off at #1.
Callbacks planted: pocket cash (#5 → #1), the hat (#4 → ending), 15 slots (#2 → #1), Psycho (#3 → ending), buying a car late (fast round → #1).

Target ~1,850 words ≈ 9.5 min at 195 wpm. Status: **wanted** = footage to find (see the shot list in `sources/moments.md`), **card** = deliberate graphic (in `cards/cards.json`), **found** = logged moment.

Footage IDs: `gta6_t1`, `gta6_t2` = official Rockstar GTA 6 trailers 1 and 2; `gta6_launch` = official launch trailer / gameplay video if Rockstar published one; `gta5_*` = no-commentary GTA 5 story gameplay; `gta6_play_*` = no-commentary GTA 6 gameplay from creators (post-launch, credited). **Never** label GTA 5 or modded footage as GTA 6.

## Cold open

| # | Narration | What the viewer sees (exact moment) | Sound | Status |
|---|---|---|---|---|
| 1 | In GTA 5, you die, you wake up outside a hospital, and you carry on. | GTA 5 "WASTED" screen → respawn walking out of a hospital (`gta5_wasted`) | Game audio hot 0.5 s before the first word | wanted |
| 2 | In GTA 6, the cash in your pocket is just… gone. | GTA 6 "WASTED" or death in gameplay (`gta6_play_death`); fallback: trailer chase ending | bed dip + hit on "pocket" | wanted |
| 3 | In GTA 5, you lose the cops and they forget you exist. | GTA 5 stars flash and vanish behind a building (`gta5_wanted_escape`) | | wanted |
| 4 | In GTA 6, they remember your shirt. | `stars_heat` card over blurred GTA 6 police shot (`gta6_t2` cop shot) | hit on "shirt" | card |
| 5 | In GTA 5, you can replay any mission from the pause menu. | GTA 5 pause menu → Replay Mission list (`gta5_replay`) | tick | wanted |
| 6 | In GTA 6, you can't. Not even after the credits. | `stamp_no_replay` stamp over the GTA 5 menu frozen | hit | card |
| 7 | And there's one mission in Chapter 1 that takes your car, your house, and your wallet, and you can start it by accident. | Fast 3-shot: Jason's car / house / wallet in GTA 6 gameplay (`gta6_play_ch1`), then black-out frame | music drop 0.3 s on "wallet" | wanted |
| 8 | Rockstar North's Rob Nelson told Famitsu that Jason and Lucia keep bank accounts alongside the cash they carry, and that getting wasted or busted puts that cash at risk. | `famitsu_nelson` headline card over blurred trailer | | card |
| 9 | So I went through the guides written since launch, and the money, police and save systems behind them, and boiled it down to five. | Fast montage 0.7 s shots of GTA 6 gameplay variety | music up slightly | wanted |
| 10 | These five feed into each other. Make one, and you're halfway to the next. | `map_1` preview (all 5 nodes dim) | whoosh | card |
| 11 | And number one is that mission. We'll get there. | Same Ch.1 car shot from line 7, frozen | | wanted |

## Number 5: Walking around with your cash

| # | Narration | What the viewer sees | Sound | Status |
|---|---|---|---|---|
| 12 | Number five. Walking around with your cash. | `map_1` (node 1 lit, "MISTAKE 05 · POCKET CASH") | whoosh + hit | card |
| 13 | GTA 6 splits your money in two. There's what's in the bank, and there's what's in your pocket. | `money_split` card (BANK / POCKET) over blurred GTA 6 store robbery | | card |
| 14 | Rob a store, and the money goes in your pocket. | GTA 6 store robbery, cash grabbed (`gta6_t1` robbery shot) | register / game audio up | wanted |
| 15 | And pocket money is the money you lose. | Same shot, freeze | | wanted |
| 16 | Get wasted or busted, and according to every guide I've read, that cash is gone. Not dropped. Not recoverable. Gone. | GTA 6 arrest or death (`gta6_play_busted`) | music chops on each one-word sentence | wanted |
| 16a | Picture it. You rob a liquor store. Then a gas station. Then a second liquor store, because the first one went so well. | GTA 6 store robbery ×3, fast cuts (`gta6_t1`, `gta6_play_robbery`), `label_count` chips 1 / 2 / 3 | register ding per store | wanted |
| 16b | You're carrying the best afternoon of your life. Then a guy in a pickup clips you at an intersection, you come off the bike, and the cops arrive before you stand up. | GTA 6 bike crash or traffic chaos (`gta6_play_crash`); fallback: trailer traffic shot, **no** GTA 5 footage here | crash audio up | wanted |
| 16c | Every dollar of that afternoon: gone. | `stamp_gone` over freeze | music drop 0.4 s + hit | card |
| 17 | The bank is safe. Death doesn't touch it. Arrest doesn't touch it. | ATM / bank interior in GTA 6 gameplay (`gta6_play_atm`) | | wanted |
| 18 | GTA 5 never really had this problem. Your money just lived in a bank account. Three of them, actually. | GTA 5 character switch wheel (Michael/Franklin/Trevor) (`gta5_switch`) | | wanted |
| 19 | So the habit you bring from GTA 5 is to stop thinking about money. That's the habit that costs you. | GTA 5 Trevor rampage clip | | wanted |
| 20 | The fix is boring: after a robbery, a job or a big sale, bank it before you do anything else. | `check_bank` checklist: "Rob it. Bank it. Then be an idiot." | tick ×3 | card |
| 21 | Because the fastest way to lose that cash… is getting caught. | GTA 6 police lights in trailer (`gta6_t2` police) | bridge: music lift | wanted |

## Number 4: Thinking a new hat fools the cops

| # | Narration | What the viewer sees | Sound | Status |
|---|---|---|---|---|
| 22 | Number four. Thinking a new hat fools the cops. | `map_2` (node 2 lit, "MISTAKE 04 · THE HAT") | whoosh + hit | card |
| 23 | GTA 6's police don't just count stars. Previews call it Heat: icons under your wanted level that show what the police actually know. | `stars_heat` card (stars + icons OUTFIT / FACE / VEHICLE) over blurred police footage | | card |
| 24 | Your outfit. Your face. Your car. | Same card, each icon highlighted in turn (3 states) | tick ×3 | card |
| 25 | And it needs a trigger. A witness calling it in, an alarm, a camera. | GTA 6 trailer: NPC filming on a phone (`gta6_t1`/`gta6_t2` phone shot) | | wanted |
| 26 | When the stars turn red, the cops can't see you, but they're looking for anyone who matches the description. | `stars_red` card | low riser | card |
| 26a | That's a real change from GTA 5, where a cop seeing you was the whole investigation. Here, the information has to reach them first, and it can be wrong, or incomplete, or about your car instead of you. | GTA 5 cop spotting player (`gta5_wanted_escape`) → `stars_heat` card with only VEHICLE icon lit | | card |
| 27 | Which is where the mistake comes in. | GTA 6 character in a clothing store (`gta6_play_clothes`) | | wanted |
| 28 | In GTA 5, the move was to drive out of the circle and wait. | GTA 5 minimap search cone / circle (`gta5_wanted_escape`) | | wanted |
| 29 | In GTA 6, people grab a hat, put on sunglasses and walk past the cop like nothing happened. | GTA 6 gameplay: character puts on hat/glasses (`gta6_play_clothes`) | | wanted |
| 30 | According to preview coverage, that doesn't work. A hat and shades don't change the description. A full outfit change does. | `stamp_hat` stamp "HAT ≠ DISGUISE" over the same shot | hit | card |
| 31 | Changing your hair reportedly clears your face, but not your clothes. | GTA 6 barber shot (`gta6_play_barber`) or label card | | wanted |
| 32 | So keep a spare outfit in the trunk. Previews say that's now an actual feature. And if there's a camera, wear a mask before the crime, not after. | GTA 6 car trunk opened (`gta6_play_trunk`); `label_mask` chip | | wanted |
| 33 | The cops can forget your shirt. | Clean GTA 6 walk-away shot, police car passing | | wanted |
| 34 | Your reputation doesn't forget anything. | `meter_profile` meter card slides right | hit | card |

## Number 3: Living in the Psycho tier

| # | Narration | What the viewer sees | Sound | Status |
|---|---|---|---|---|
| 35 | Number three. Living in the Psycho tier. | `map_3` (node 3 lit, "MISTAKE 03 · PSYCHO") | whoosh + hit | card |
| 36 | GTA 6 tracks what kind of criminal you are. Guides list five Criminal Profile levels, from Professional at one end to Irredeemable at the other. | `meter_profile` card (Professional → Irredeemable) | | card |
| 37 | Four of those levels move. Do some clean jobs, calm down for a while, and your profile drifts back. | Meter slider moving back left (2 states) | | card |
| 37a | That's the system working as intended. Have a bad day, have a good week, and the game lets you be a different person again. Mostly. | GTA 6 calm activity shot (`gta6_t2` beach / gym) | | wanted |
| 38 | Irredeemable doesn't. Guides agree it's permanent, for that character, for that playthrough. | `stamp_permanent` stamp over meter | music drop 0.3 s + hit | card |
| 39 | The good news: one bad afternoon won't get you there. Polygon's description is that one rampage isn't enough. You have to keep it up for hours. | GTA 6 gameplay chaos shot (`gta6_play_chaos`); fallback trailer action | | wanted |
| 40 | The bad news is that GTA 5 trained us to do exactly that for hours. | GTA 5 rampage: Trevor, tank, five stars (`gta5_rampage`) | game audio up briefly | wanted |
| 41 | According to guides, once you're Irredeemable, police shoot on sight, surrendering stops being an option, and you lose a passive way of building Focus. | `check_irredeemable` checklist (3 items) over blurred GTA 6 police | tick ×3 | card |
| 42 | How it changes the story, nobody's fully mapped yet. I'm not going to guess. | `label_unclear` chip "STORY EFFECT: UNCONFIRMED" | | card |
| 43 | If you want to go full Psycho, and honestly, fair, make a manual save first. | GTA 6 pause menu save screen (`gta6_play_save`) | | wanted |
| 44 | Because Irredeemable is permanent… unless you have a save from before it. | Freeze on save screen | | wanted |
| 45 | Do you? | Black frame with `title_do_you` | bed drop 0.5 s | card |

## Number 2: Trusting the autosave

| # | Narration | What the viewer sees | Sound | Status |
|---|---|---|---|---|
| 46 | Number two. Trusting the autosave. | `map_4` (node 4 lit, "MISTAKE 02 · AUTOSAVE") | whoosh + hit | card |
| 47 | GTA 6 gives you fifteen manual save slots. And one autosave. | `stat_slots` card: "15 MANUAL / 1 AUTO" | | card |
| 48 | Remember that number. Fifteen. It comes back. | Same card, "15" highlighted | tick | card |
| 49 | Here's the part that catches people. There's no mission replay. | `stamp_no_replay` over GTA 6 mission-complete screen (`gta6_play_mission`) | hit | card |
| 50 | GTA 5 let you replay any story mission from the pause menu. | GTA 5 replay menu (`gta5_replay`) (callback to line 5) | | wanted |
| 51 | GTA 6, according to every save guide out there, does not, not even after the credits. If you want a mission back, you need a manual save from before it. | GTA 6 pause menu save list (`gta6_play_save`) | | wanted |
| 52 | And you can't manual save in the middle of a mission. | Mission HUD on screen in GTA 6 gameplay | | wanted |
| 53 | One more trap: you only get one autosave slot. Guides warn that loading an older save can overwrite it. So before you load anything, save where you are now, in a spare slot. | `check_saves` checklist: "Save now. Then load." | tick ×2 | card |
| 53a | Here's the routine I'd use. One slot per chapter, saved at the start, and never overwritten. One rolling slot you save to every session. And one spare, for right before anything that looks important. | `check_slots` checklist: ONE PER CHAPTER / ONE ROLLING / ONE SPARE | tick ×3 | card |
| 53b | Fifteen slots sounds like a lot. Across a whole story, with no replays, it isn't. | `stat_slots` card, "15" pulses | | card |
| 54 | The habit to build: before every big mission, new slot. | GTA 6 save menu, cursor moving to an empty slot | | wanted |
| 55 | And there's one mission you really want a save in front of. | Hold on empty slot | bridge: music lift | wanted |

## Fast round: four quick ones

| # | Narration | What the viewer sees | Sound | Status |
|---|---|---|---|---|
| 56 | Before number one, four quick ones. | `title_four_quick` title card | whoosh | card |
| 57 | Banks and loan stores, early. Guides agree the cash has dye packs that go off if you get too far from the building, and the money's ruined. | GTA 6 bank robbery (`gta6_t1` bank or `gta6_play_bank`), `label_dye` chip | | wanted |
| 58 | You need the Dye Pack Jammer, and that comes from the Chapter 3 mission Credit Check. Until then, stick to stores. | `label_jammer` chip over same footage | tick | card |
| 59 | Stolen cars. Early on, they aren't yours to keep. From Chapter 2, guides say you can register one, for a fee. | GTA 6 car theft (`gta6_t1` carjack) | | wanted |
| 60 | Cameras. A mask before the crime means CCTV has nothing useful to send. | Security camera shot in GTA 6 trailer (`gta6_t2`) | | wanted |
| 60a | Settings. Before your first big chase, spend two minutes on camera speed, aim sensitivity and subtitles. Every guide says it. Almost nobody does it. | GTA 6 settings menu (`gta6_play_settings`) | tick | wanted |
| 61 | And buying a new personal car late in Chapter 1. | GTA 6 car dealership / customisation (`gta6_play_ch1`) | | wanted |
| 62 | That last one's a hint. | Freeze | bed drop 0.4 s | wanted |

## Number 1: Starting Tourist Trap unprepared

| # | Narration | What the viewer sees | Sound | Status |
|---|---|---|---|---|
| 63 | Number one. Starting Tourist Trap unprepared. | `map_5` (node 5 lit, "MISTAKE 01 · TOURIST TRAP") | **music out** for lines 63-66 | card |
| 64 | Tourist Trap is the point of no return in Chapter 1. Start it, and guides say you're locked into a three-mission run straight into Chapter 2. | GTA 6 mission start for Tourist Trap (`gta6_play_tourist`) if a creator shows the title card; else map shot | | wanted |
| 65 | When it's over, you lose Jason's personal vehicles. Every upgrade on them. Even the Ultimate Edition cars. | Jason's car (callback to line 7) + `stamp_gone` | hit | wanted |
| 66 | You lose the house. The cash in your wallet. Your checking account balance. | `check_lose` checklist (unchecked style): VEHICLES / UPGRADES / HOUSE / WALLET / CHECKING | tick ×5 | card |
| 67 | Remember mistake five? The pocket cash? This is where it hurts most. | Callback: the robbery cash shot from line 14 | music back in, low | wanted |
| 68 | What you keep, according to guides: a capped amount of family savings, your relationship with Lucia, and your unique weapons. | `check_keep` checklist (3 items, checked) | | card |
| 68a | Several guides also list Chapter 1 side activities you can miss for good once Tourist Trap starts. Check a missables list before you go, because the game doesn't hand you one. | Chapter 1 side activity in GTA 6 gameplay (`gta6_play_ch1`), `label_missable` chip | | wanted |
| 69 | So that car you bought late in Chapter 1? That was the hint. | Callback: dealership shot from line 61 | | wanted |
| 70 | Before you start Tourist Trap: finish the Chapter 1 side activities you care about, spend the money you'd lose on things that last, and make a manual save. | `check_before` checklist (3 items) | tick ×3 | card |
| 71 | Remember fifteen? This is what one of those slots is for. | `stat_slots` card again (callback) | hit | card |

## Ending

| # | Narration | What the viewer sees | Sound | Status |
|---|---|---|---|---|
| 72 | Rob Nelson told Famitsu that getting wasted or busted puts your cash at risk. That's the whole game in one sentence. | `famitsu_nelson` card again (bookend) | | card |
| 73 | GTA 5 asked how fast you could get back into the action. GTA 6 asks what you're still carrying when you do. | GTA 5 hospital respawn (line 1) → GTA 6 walk-away shot | | wanted |
| 74 | The cash in your pocket. The shirt a witness remembers. The hat that fooled nobody. The profile you can't take back. The save you didn't make. The car you bought too late. | One long-held calm GTA 6 shot (sunset drive, `gta6_t2`) | music steady | wanted |
| 75 | See? They connect. | `map_all` complete map, all nodes lit and connected | whoosh + hit | card |
| 76 | Is that more punishing than GTA 5? Yes. It's great until you lose twenty minutes of loot to a fender bender. It's great until the cops recognise your favourite jacket. | Quick GTA 6 crash + police shot | | wanted |
| 76a | And if you play the way GTA 5 taught you, the first ten hours of GTA 6 will feel like the game is against you. | GTA 5 chaos clip → GTA 6 busted | | wanted |
| 76b | It isn't. It just keeps receipts. | `stamp_receipts` stamp "IT KEEPS RECEIPTS" | hit | card |
| 77 | But nobody ever told a good GTA story about a mistake they avoided. It's always the one they made. | Chaotic GTA 6 gameplay montage | music lift | wanted |
| 78 | So which one got you: the pocket cash, or Tourist Trap? | `title_comment` title card | | card |
| 79 | Bank your money. See you in Leonida. | Wide sunset over Vice City (`gta6_t1` skyline) | music out on last word | wanted |
