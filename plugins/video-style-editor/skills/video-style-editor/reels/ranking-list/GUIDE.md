<!-- From claude-editing-skills by Artem Novitckii (MIT) - adapted for video-style-editor; see reels/NOTICE.md -->
> **When:** Edits a talking-head clip into a tier-list ranking reel. An S-to-F tier table sits on the speaker's chest, each item pops up as it is named and drops into its tier when the verdict lands, with an orange title on top and spoken captions just under the chin. Use when the user runs /ranking-list or asks for a tier list, a ranking reel or "rank these" on a 9:16 clip.

# Layout: ranking-list

```
┌──────────────────────┐
│  BEST CONTENT FORMATS│  orange skewed title
│        (face)        │
│     at c tier        │  caption just under the chin
│ S ▓▓  ┌──────────┐   │
│ A     │ FACEBOOK │   │  item pops on the chest, then drops into its row
│ B     └──────────┘   │
│ … F                  │
└──────────────────────┘
```

## Before you start (video-style-editor)
This layout lives in the video-style-editor skill (`reels/ranking-list/`). Run everything through `$V` (SKILL.md section 0:
`VSE_HOME=... VSE_BUDGET=150 PYTHONDONTWRITEBYTECODE=1 python3 SKILL_DIR/scripts/vse.py`).
- Once per computer: `$V reel setup` (HyperFrames + GSAP + Chromium from npm into `$VSE_HOME/reels-runtime`; the
  cutout model downloads on first use). No API key: words come from the local Vietnamese speech model.
- Work on a project clip: `$VSE_HOME/projects/<job>/raw/<clip>`; write the spec to `<job>/plans/<clip>.ranking-list.json`.
  The reel goes to `<job>/output/`, cache to `<job>/work/reels/`.
- The speech model writes no punctuation: `reel words` ends a line at every pause (`[ends …]`), use those as
  sentence edges. Captions are lower case; spellings come from my-style `words` plus the spec's `"fix": {"asr": "Right"}`.
- Titles / labels are typed by you: write proper Vietnamese with capitals and diacritics. Fonts with Vietnamese
  glyphs stand in for the originals (Montserrat Black for Archivo Black, Playfair / Noto Serif Display for the
  serifs, VT323 for the pixel font).
- Exit code 3 / `CONTINUE` = time budget reached (cutout or render), run the same command again.
- Apply my-style (`$V style show`) where it does not fight the layout: rules, banned words, caption spellings.

## Steps
1. **Clip.** A 9:16 talking head where the speaker names things and judges them ("carousels are S tier… reels, B").
2. **Words.** Run `$V reel words <video>`. It prints one sentence per line with `[ends …]` (when its last word ends). Find each item's name and its verdict. The item pops on its name and drops on its verdict. Pick a stretch that holds 1 to 5 items, and keep `end` at least 0.4 s after the last drop.
3. **Chin.** Run `$V reel frame <video> <t> <job>/work/reels/frame.jpg` and read the y of the chin.
   - Set `caption_top` about 40 px under the chin.
   - Set `table_top` 80 px under that.
   - On a close-up (chin below about y 1150), use 3 or 4 `tiers` so the table stays above y 1500. The item card shrinks itself to fit.
   - Captions must never sit on the face.
4. **Spec.** Write `<clip>.ranking-list.json` (below). Paths in a spec are relative to the spec file. Times are seconds from `start`, or spoken words.
5. **Build.** Run `$V reel build ranking-list <spec.json>`.
6. **Check.** Look at `<out>.sheet.jpg`:
   - The caption is under the chin.
   - The table and items sit on the chest, above the red bottom zone.
   - Each drop lands on its verdict word.
7. **Hand over** the mp4 path.

## Spec
```json
{
  "video": "my-clip.mp4", "start": 0, "end": 7.1,
  "title": "BEST CONTENT\nFORMATS",
  "table_top": 1100, "caption_top": 1022,
  "items": [
    {"name": "CAROUSELS", "tier": "S", "pop": 0.06, "drop": "cheat", "images": ["c1.jpg", "c2.jpg", "c3.jpg"]},
    {"name": "REELS", "tier": "B", "pop": "twice", "drop": "reels", "icon": "play", "color": "#7a2fb0"}
  ]
}
```
- **`items`**: each item gets a `name` (keep it short and uppercase), a `tier` (S, A, B, C, D, E or F), and `pop` and `drop` times. Its picture is one of:
  - `images`: 2 or 3 images fan out, or 1 image fills the card.
  - `icon: "play"`: a reel icon.
  - nothing: just the name on a coloured card (`color`).
- Items in the same tier line up left to right in the order they drop.
- **`tiers`** (optional) replaces S to F: `[["GOAT", "#FF7F7F"], ["MID", "#FFDF7F"], ["NO", "#7FBFFF"]]`.

## Taste
- Pop on the name, drop on the verdict. If they are said together, drop 1 s after the pop.
- Title in 2 short lines, 2 to 3 words each.
- Logos and images must be ones the user is allowed to show. A plain name card is always fine.
