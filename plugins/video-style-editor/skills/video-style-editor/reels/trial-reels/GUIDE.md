<!-- From claude-editing-skills by Artem Novitckii (MIT) - adapted for video-style-editor; see reels/NOTICE.md -->
> **When:** Turns one talking-head clip into 3 visually distinct reels to post as Instagram trial reels, so you can see which look wins. Version 1 has a big yellow title and karaoke captions, version 2 a white post-card header with punch-in zooms and bold uppercase captions, and version 3 a dark grid backdrop with a pixel-font stat and the clip in an orange frame. Use when the user runs /trial-reels or asks for trial reel versions, variations or A/B looks of a 9:16 clip.

# Layout: trial-reels

```
 1 TITLE + KARAOKE      2 POST HEADER           3 PIXEL FRAME
┌──────────────┐      ┌──────────────┐       ┌──────────────┐
│ CAROUSELS ARE│      │(o) Name      │       │      2×      │
│  INSTAGRAM   │      │ The hook as a│       │ the views of │
│  CHEAT CODE  │      │ headline     │       │ ┌──────────┐ │
│    (face)    │      │  (face, zooms│       │ │● REC face│ │
│ grey→white   │      │  CHEAT CODE  │       │ │ pixel cap│ │
└──────────────┘      └──────────────┘       └──────────────┘
```

## Before you start (video-style-editor)
This layout lives in the video-style-editor skill (`reels/trial-reels/`). Run everything through `$V` (SKILL.md section 0:
`VSE_HOME=... VSE_BUDGET=150 PYTHONDONTWRITEBYTECODE=1 python3 SKILL_DIR/scripts/vse.py`).
- Once per computer: `$V reel setup` (HyperFrames + GSAP + Chromium from npm into `$VSE_HOME/reels-runtime`; the
  cutout model downloads on first use). No API key: words come from the local Vietnamese speech model.
- Work on a project clip: `$VSE_HOME/projects/<job>/raw/<clip>`; write the spec to `<job>/plans/<clip>.trial-reels.json`.
  The reel goes to `<job>/output/`, cache to `<job>/work/reels/`.
- The speech model writes no punctuation: `reel words` ends a line at every pause (`[ends …]`), use those as
  sentence edges. Captions are lower case; spellings come from my-style `words` plus the spec's `"fix": {"asr": "Right"}`.
- Titles / labels are typed by you: write proper Vietnamese with capitals and diacritics. Fonts with Vietnamese
  glyphs stand in for the originals (Montserrat Black for Archivo Black, Playfair / Noto Serif Display for the
  serifs, VT323 for the pixel font).
- Exit code 3 / `CONTINUE` = time budget reached (cutout or render), run the same command again.
- Apply my-style (`$V style show`) where it does not fight the layout: rules, banned words, caption spellings.

## Steps
1. **Clip.** The user's finished reel or its hook. Whole clips work. The hook (first 5 to 10 s) is the usual test.
2. **Words.** Run `$V reel words <video>` and read the hook. Each sentence ends with `[ends …]`: use the last one you keep as `end`.
3. **Write three different packagings of the same idea.** Each version is a different promise, not just a different font:
   - **v1 title**: the claim, 3 lines, with the 1 or 2 key lines bigger (`*line*`).
   - **v2 headline**: the hook rewritten as a post headline ("The Instagram cheat code not many people know about"), plus the speaker's avatar and name. `keys` are the caption words to turn yellow (the punch-ins land on them).
   - **v3 stat**: the single number or comparison in the clip ("2×", "10K", "$0") plus a 3 to 5 word line.
4. **Spec.** Write `<clip>.trial-reels.json` (below). Paths in a spec are relative to the spec file.
5. **Build.** Run `$V reel build trial-reels <spec.json>`. It writes `<out>-1.mp4`, `<out>-2.mp4` and `<out>-3.mp4`, each with a sheet.
6. **Check.** Look at all three sheets:
   - The titles clear the top 220 px.
   - The captions sit under the face, not on it.
   - The three versions look clearly different at a glance.
7. **Hand over** the three paths with one line each on what the version tests.

## Spec
```json
{
  "video": "my-reel.mp4", "start": 0, "end": 6.95,
  "v1": {"title": ["carousels are an", "*instagram*", "*cheat code*"]},
  "v2": {"avatar": "me.jpg", "name": "Your Name", "sub": "Instagram growth",
         "headline": "The Instagram cheat code not many people know about",
         "keys": ["cheat", "code", "twice", "views"], "punches": ["cheat", "twice"]},
  "v3": {"stat": "2×", "line": "the views of reels", "pulse_at": "twice"}
}
```
Optional fields:
- **`caption_top`** per version: 1400 for v1, 1260 for v2, 1330 for v3 by default.
- **`punches`**: defaults to the key words, at least 1.5 s apart.

## Taste
- Same clip, same words, three different first impressions. Change the promise, not just the paint.
- No invented numbers. The v3 stat must be something said in the clip.
- Post all three as trial reels on the same day and keep the one with the best 3-second hold.
