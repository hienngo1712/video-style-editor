---
name: video-style-editor
description: Edit raw phone footage into a finished 9:16 vlog in a learned style (Vietnamese storytelling vlog by default) - transcribe, plan teaser/cuts/captions/effects/SFX, render with FFmpeg, QA, optional listening review with Gemini - and learn the user's own taste from their feedback (my-style). Also 6 designed reel layouts (trial-reels, behind-the-person, explainer, split-screen, ranking-list, storytelling) that turn one 3-8 s talking-head stretch into an animated 9:16 reel. Use when asked to edit or re-edit videos from raw clips, to learn an editing style from reference videos, or to record / apply editing feedback and preferences.
---

# Video style editor

Turns a folder of raw clips into a finished vertical video in a style from `profiles/`, tuned to the user's own
taste in `<VSE_HOME>/my-style/` (preferences + feedback journal - `docs/personalize.md`).
Machine work is scripted; the editorial decisions (story, teaser, cuts, caption fixes, emphasis, SFX)
are yours, written down as an **edit plan** (`docs/edit-plan.md`). Everything goes through one command:

```
V="python3 SKILL_DIR/scripts/vse.py"      # SKILL_DIR = folder of this file (${CLAUDE_SKILL_DIR} in Claude Code)
```

## 0. Setup (first command of every session)
- **Claude desktop / Cowork:** run everything in the shell of the user's linked computer, where the footage is
  (its Linux VM has Python 3 + FFmpeg; the user installs nothing). Prefix every command with
  `VSE_HOME=<connected folder>/vse-workspace VSE_BUDGET=150 PYTHONDONTWRITEBYTECODE=1`. VSE_HOME is the user's
  workspace and survives plugin updates: `models/ fonts/ sfx/ overlays/` (downloaded once, ~300 MB),
  `my-style/` (their taste), `projects/<job>/` (footage + outputs), `references/` (sample videos for learning styles).
  Never write projects, renders or test files into the plugin / repo folder.
- **Claude Code on the user's machine:** Python 3.10+ and FFmpeg must be installed; no budget needed.
- `$V doctor --fix` installs Python packages and downloads what is missing. If SFX downloads are blocked,
  fetch the URLs in `assets/sfx/manifest.json` with a browser into `$VSE_HOME/sfx/`.
- **New user / "how do I start"**: `docs/huong-dan-nguoi-moi.md` is the user-facing guide (Vietnamese) with the
  copy-paste prompts (setup -> interview -> first edit -> feedback). Follow the step the user is on; answer in the
  user's language, plain words, no command names unless asked.
- **Exit code 3 / `CONTINUE`** = time budget reached, progress saved: run the same command again.
- Cowork: writing a file back to the user's computer with `device_commit_files` - stage each revision under a NEW
  path (re-using a staged path wrote an older copy) and compare `md5sum` on both sides. Background jobs started from
  the computer's shell are killed when the call ends: every long step must be resumable (render already is).

## 1. Edit a job
PROJECT = a folder with the footage in `PROJECT/raw/` (sub-folders fine), by default `$VSE_HOME/projects/<job>/`.
Outputs go to `PROJECT/work`, `PROJECT/plans`, `PROJECT/output` only - keep the user's folders tidy.

0. **Personal style** - `$V style show` (first run: `$V style init`). If it says **NOT ONBOARDED**, interview the user
   first with `docs/onboarding.md` (rounds of <= 4 questions: goal & platform, pacing & hook, on-screen text, audio,
   picture, brand & no-gos, reference videos & review flow; always end with "what annoys you most when someone else
   edits for you?"), record the answers with `$V style set / rule / word`, write `my-style/brief.md`, then
   `$V style set onboarded <date>`. Analysis of the footage can run meanwhile. For the very first video, render a
   ~15 s preview plan (teaser + first lines) and confirm text / pacing / sound before the full render.
   Every job: apply the `style` defaults (render reads them automatically), `sfx` likes/bans, `words` spellings,
   the brief and every line of `rules`; read the recent feedback and the topics with the most notes - do not repeat
   a mistake that is already in the journal.

1. **Analyse** - `$V analyze PROJECT` (prepare -> transcribe -> sound events).
   Look at every `work/thumbs/sheet_*.jpg`, read all of `work/transcript.json` and `work/audio_events.json`.
   Audio-only files (voice memos) are often a narration script - read them first.
2. **Style** - pick a profile from `docs/styles.md` unless the user named one (one storyteller ->
   `story-vlog`; people acting out a situation -> `office-sitcom` + format; a host reviewing ->
   `review-xam`; vendors/customers -> `street-kindness`; scripted actors -> `mini-drama`; pets -> `pet-dub`;
   wordless mood clip -> `trend-aesthetic`). Read `docs/viral-formula.md` once.
   **Story** - decide, before any cut: the payoff / ending, the teaser (2-4 strongest lines, 5-15 s, each
   understandable alone - include the subject), the opening line, the body order (usually chronological),
   what to drop. If the footage supports two videos (e.g. two places), make two.
3. **Cuts** - for every piece run `$V inspect PROJECT CLIP START END`: words + a loudness strip + pauses.
   Cut in pauses: `a` just after the pause before the first kept word, `b` in the pause after the last word
   (a word is often audible 0.1-0.2 s after its ASR end). Drop restarts and stray words at the cut.
   **Craft** - read `docs/editing-craft.md` section 0 (pre-export checklist from a CapCut course + pro editor
   feedback): safe zones, audio levels, SFX variety, colour order, transitions at topic changes.
4. **Plan** - write `PROJECT/plans/<name>.json` (fields: `docs/edit-plan.md`, real example:
   `examples/plan-example.json`). Take structure, captions, emphasis, SFX names, gains and timing from the chosen
   profile; give each SFX a reason. Sitcom style: `style.caption_mode: static`, `speakers` colours, `speaker`
   per piece, reaction punch-ins (`zoom` 1.25 + `tint: pink`), a ducked `music` bed if the user supplies music.
   Correct ASR errors in `fix` from context (same word count; `_` hides, `+` glues).
   **Tighten** - `$V tighten PROJECT plans/<name>.json plans/<name>-t.json` cuts filler sounds (ờ, ừm, a lone à/ừ)
   and pauses > 0.45 s inside every speaking piece (pro editor: "cắt hết ừ, à, phần thừa - video liền mạch"). It lists
   voiced gaps with no word (an "ờ" the ASR dropped, or a missed word): check them with `inspect`, `--sounds` cuts
   them. Lint and render the `-t` plan.
5. **Lint** - `$V lint PROJECT plans/<name>.json` prints the timeline and must show 0 errors.
   Read every warning: clipped cut, level hint (`vol`), SFX on a word, same zoom on a jump cut.
6. **Render** - `$V render PROJECT plans/<name>.json` (pieces -> final mix -> 540p review copy). Only pieces
   whose picture/audio changed re-render, so iterate freely.
7. **Check** - `$V check PROJECT plans/<name>.json`, then look at `work/check/<name>_sheet.jpg`
   (captions readable, big text, framing). Fix and render again.
8. **Listen** - you cannot hear. If Claude in Chrome and the user's Gemini are available, follow
   `docs/gemini-review.md`; otherwise ask the user to listen to the review copy. Verify each note
   (timeline from lint + inspect), apply it in `<name>-v2.json`, render, and repeat until the listener
   has no must-fix items (target 8.5+/10).
   If the user finishes in CapCut, see `docs/capcut-guide.md` (captions.ass imports into CapCut).
9. **Report** - output path and length, teaser and payoff, captions you guessed, what a human should check.
10. **Learn** - ask the user for feedback (where, which second, what they want instead) and log each point:
   `$V style note "TEXT" --project P --video NAME --at 0:12 --tag captions --by user|editor|gemini --fix "what you did"`.
   If the user corrected a plan, `$V style learn PROJECT plans/A.json plans/B.json`. When a note repeats (2x) or the user
   says "always / lần sau cứ thế", PROPOSE the change to `my-style/preferences.yaml` (a `style`/`sfx`/`pacing`/`words`
   value or one concrete line in `rules`) and write it only after the user agrees. Skill-wide lessons (true for every
   user) belong in section 3 below / `docs/editing-craft.md` instead.

## 1b. Designed reel layouts (`vse.py reel`)
Six layouts from claude-editing-skills by Artem Novitckii (MIT, `reels/NOTICE.md`), adapted to Vietnamese and to
running locally: overview and routing in `docs/reels.md`, each layout's steps / spec / taste in
`reels/<layout>/GUIDE.md` (read it before writing a spec). Use one when the user names it or asks for that look
("2 bản để test", "chữ sau lưng người", "chia đôi màn hình", "bảng xếp hạng", "3 ảnh + tiêu đề", "trước / sau").
- Flow: `$V reel words <clip>` -> pick ONE point (3-8 s, whole breath groups) -> `$V reel frame <clip> <t> <job>/work/reels/frame.jpg`
  (eyes / chin y) -> spec in `<job>/plans/<clip>.<layout>.json` -> `$V reel build <layout> <spec>` (exit 3 = run again)
  -> look at `<job>/output/<clip>.<layout>.sheet.jpg` (red = covered by the app UI) -> fix -> hand over.
- Visuals land on the spoken word (anchor times to words). Never invent numbers, comments or names. Titles in proper
  Vietnamese; captions come from the local ASR (fix spellings with `"fix"` or my-style `words`).
- First build in a session installs the runtime by itself (`$V reel setup`, npm, ~30 s).

## 2. Learning a new style
Sample library (REFROOT, default `$VSE_HOME/references`): `REFROOT/<style>/videos/<style>__<format>__<content>__<views>.<ext>` - never a person's or
channel's name in a file or folder name; channels are source codes (k1, k2) whose real handles live only in the
private `REFROOT/_sources/`. `REFROOT/INDEX.md` lists every sample (format, content, views, source, length,
cuts/min, first line); find samples with globs (`*/videos/*__brand-skit__*`). Before editing in a style, open
`REFROOT/<style>/analysis/_hooks.jpg` and the INDEX rows of that style.
New style: take top, middle and low view videos of each source, name them as above, put them in
`REFROOT/<style>/videos/` -> `$V reference REFROOT/<style>`, `$V transcribe ...`, `$V events ...`,
`$V library REFROOT` -> study hooks, sheets, summary, transcripts and what separates high from low views ->
write `profiles/<style>.yaml`, add a row to `docs/styles.md` and the evidence (source codes, not names) to
`docs/viral-formula.md`. Only use videos the user may download; never commit them.

## 3. Rules learned from feedback (keep adding)
- No "next episode" card at the end unless asked (keep it if the creator's own narration says it).
- A teaser line must make sense alone; no single-word or overlapping teaser chunks.
- Never cut inside a word; a restart ("Đây, phòng...") left at a cut sounds like an error - trim it.
- Two pieces of one sentence that sound choppy -> merge them into one piece.
- Quiet take: `vol` +3..+5; boosting also lifts room noise -> add `denoise`. Wind outdoors: `denoise`.
- Reaction SFX (boing, fail piano) go in the pause after the line, never over the key word.
- A cue SFX that illustrates a word (elevator ding on "thang máy") sits under it at -18.
- Same take, consecutive pieces: alternate zoom 1.0 / 1.12 (render.py gives them 10 ms fades).
- Captions show 3 words at a time; a reviewer sampling 1 frame/s will report "missing words" - check the
  ASS/plan before changing captions.

From 3 professional editors (10/2026, all 8 test videos) + the CapCut course - details in `docs/editing-craft.md`:
- TikTok safe zone on 1080x1920: no text in the top ~190 px, the bottom ~420 px, or the right ~130 px of the lower
  half. Captions centred at ~75 % height (`caption_margin_v` 470 is the default now; teaser 520, title 230).
  `check` draws the zone on its sheet.
- Speech is denoised by default (RNNoise at 60 %, `denoise: light`); `"strong"` (100 %) only for very noisy takes -
  it muffles outdoor voices, swallows off-mic replies and clips soft word endings. Off-mic speaker or a room's sound
  you want: `denoise: false` (+ `vol`). Voice peaks "yellow, never red"; final -12 LUFS. Leave `compress` off.
- SFX: no single sound more than twice per video, rotate variants; normal gain -12, subtle -16, -8 only for the
  one big hit. Part-2 style stacks of loud SFX sound harsh.
- Transitions: hard cuts by default, plus 1-3 of one kind (`transition: zoom`) at topic/section changes - not only at
  the start, never on every cut (lint warns).
- Keywords and headings: one fixed look and 1-2 fixed in/out animations for the whole video.
- Colour: `color_match` (default on) evens out exposure per clip and `style.look` (default `clean`) gives one shared
  look; never stack two looks, never per-frame auto-normalise (flicker). Landscape clip in 9:16: `fit: blur`.
- Output: 1080x1920, constant 30 fps, SDR Rec.709 (tonemap iPhone HLG), H.264; check total length and make frame 1
  a cover-worthy shot.
- Captions land ~0.2 s AFTER the word is heard and fill in word by word (`caption_lag` 0.2, `caption_reveal`): text
  that arrives first gives the line away. Big text lines appear when their first word is said. render.py does this;
  in CapCut shift imported captions +0.2 s and check sync at 3 points (one CapCut import was 1-2 s off in a car clip).
- Movement: every piece of 1.5 s+ gets a slow eased push-in / pull-out (6 %), a big-text moment gets a punch-in on the
  face that says it (`style.motion` auto; `move` per piece). Text is moved off faces automatically (YuNet faces:
  caption to the top, teaser up, big text down) - `caption_pos` in the plan still wins.
- In CapCut: transitions only between touching clips on the main track; keep Auto snapping on (gaps = black
  frames); use a Vietnamese-supported font (Oswald-Bold works; template fonts break uppercase diacritics).
