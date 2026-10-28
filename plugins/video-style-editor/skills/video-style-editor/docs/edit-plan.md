# Edit plan format

An edit plan is a JSON file in `<project>/plans/`. Its `style` block overrides the user's defaults in
`<VSE_HOME>/my-style/preferences.yaml` (`style:` section), which override the built-in defaults below. Claude writes it; `vse.py lint` checks it, `vse.py render` executes it.
Pieces are cached by content, so a new version of a plan (`<name>-v2.json`) only re-renders what changed.

```json
{
  "name": "phan2-van-phong-moi",        // output file name (output/<name>.mp4)
  "profile": "story-vlog",
  "style": {"caption_size": 76,          // optional overrides
            "caption_mode": "karaoke",   // karaoke (3 words, active word yellow) | static (whole line, sitcom)
            "captions": true,            // false = no subtitles (e.g. finish captions in CapCut)
            "look": "clean",             // one colour look for the whole video: clean | warm | cool | film | none | x.cube
            "look_mix": 0.8,             // .cube only: strength 0-1 (CapCut course: 70-80 %)
            "color_match": true,         // per-clip exposure match (measured once per clip, cached in work/build/color.json)
            "exposure_target": 0.45,     // mean luma target (0-1 of 16-235); "exposure_strength": 0.7 = 70 % of the way
            "denoise": "light",          // default speech denoise for pieces with captions: light | strong | false
            "caption_margin_v": 470,     // px from the bottom to the caption baseline (TikTok safe zone 380-700)
            "teaser_margin_v": 520, "title_margin_v": 230,
            "caption_lag": 0.2,          // captions appear this long AFTER the word is heard (pro editor: ~0.2 s)
            "caption_reveal": true,      // words fill in as they are said (false = the 3-word chunk at once)
            "motion": "auto",            // eased push-in/pull-out on every piece >= 1.5 s + punch-in at big text; "off"
            "avoid_faces": true,         // move captions/teaser/big text off detected faces; "aim_faces": zooms aim at the face
            "lufs": -12,                 // final loudness
            "compress": false},          // voice compressor before loudness (off: it lifted room noise in tests)
  "speakers": {"NV1": "#7CFF4F", "Sếp": "#FF3B3B"},   // caption colour per speaker (piece.speaker)
  "music": {"file": "raw/bgm.mp3", "gain": -26, "duck": true},  // optional bed under the dialogue, ducked by speech
  "title": {"text": "KFC MỸ vs VIỆT NAM", "from": 0, "to": 6},  // optional headline / series name at the top
  "pieces": [ { ... }, { ... } ]         // in timeline order
}
```

## Piece fields

| Field | Required | Meaning |
|---|---|---|
| `clip` | yes | path relative to `raw/`, e.g. `"Văn phòng mới/IMG_9682.MOV"` |
| `a`, `b` | yes | audio in/out in seconds (clip time). Cut on word boundaries from `work/transcript.json` |
| `va` | no | video in-point if different from `a` (J/L cut: hear one moment, see another) |
| `zoom` | no | 1.0 / 1.06 / 1.12 ... alternate between consecutive pieces of the same take (lint warns) |
| `style` | no | `normal` (default, 3-word karaoke captions), `teaser` (big yellow), `none` (no captions) |
| `fix` | no | corrected caption words, **same count as ASR words inside [a, b]**; `_` hides a word ("ờ", "nhá"); `+` glues two words onto one ASR word (`TEAM+MARKETING`); `*WORD` = keyword, always yellow |
| `caption_pos` | no | `top` when action happens in the lower half |
| `big` | no | giant yellow text, `\\N` for a line break, e.g. `"TỰ CHỦ\\NTỰ DO\\NTỰ LO"`: each line appears when its first word is said (+ caption_lag); a line whose words are not spoken (a title) appears at the piece start. `big_at` = fixed delay in s |
| `move` | no | camera move with easing: `in` / `out` (slow push, `move_amt` 0.06), `punch` (fast zoom +15 % at `move_at` s, then hold), `none`. Default from `style.motion` auto. Aims at the largest face |
| `transition` | no | `paper` (torn-paper wipe), `flash` (white flash) or `zoom` (1.3x -> 1.0x punch-in, 0.35 s) at the start of the piece. Use 1-3 per video at topic/section changes, one kind - not only at the start (lint warns) |
| `vol` | no | audio gain in dB for this piece (+5 quiet second speaker, -6 noisy b-roll) |
| `denoise` | no | default `light` on every piece with captions (RNNoise mixed 60 %; `true` = light), `strong` = full RNNoise for very noisy takes (can muffle voices), `false` = keep the room sound (b-roll without captions is never denoised unless asked) |
| `fit` | no | `blur` = a landscape clip shown whole over a blurred copy of itself instead of being cropped |
| `grade` | no | manual exposure for this piece: gamma (1.1 brighter, 0.9 darker) or `null` = as shot; overrides `color_match` |
| `fx` | no | list: `shake` (0.6 s shake), `speedlines` (0.9 s radial lines) |
| `speaker` | no | who talks in this piece - caption colour from `speakers` |
| `tint` | no | colour look: `pink` (reaction punch-in), `warm`, `cool`, `bw`, or an ffmpeg filter string |
| `image` | no | picture-in-picture `{"file": "raw/app.png", "x": 0.5, "y": 0.3, "w": 0.6, "at": 0.2, "dur": 2}` (x, y = centre, fractions of the frame); a video file works too (`"ss"` = its start) - facecam reaction box |
| `audio` | no | voice-over: picture from `clip`, sound from `{"file": "Thêm/narration.m4a", "a": 12.3}` (path under raw/); captions come from that file's transcript |
| `sfx` | no | list of `{"name": "whoosh_1492", "at": 0.0, "gain": -12}`. `at` = moment (s from piece start) where the SFX **peak** lands; every file is normalised to 0 dBFS peak first, so `gain` is comparable across files: -8 loud hit, -12 normal, -16 subtle |

## Rules Claude follows when writing a plan

1. Cut points: `vse.py inspect PROJECT CLIP S E` shows words, a loudness strip and the pauses - cut inside pauses.
   `vse.py lint` flags cuts where the audio just outside the piece is loud (a clipped word).
2. A teaser line must be understandable alone — include the subject ("tầng hai này là phòng của các sếp,
   có cả giường") rather than starting mid-sentence.
3. `fix` must keep the ASR word count; render.py warns and falls back to even timing otherwise.
4. SFX: never the same file more than twice per video (lint warns) - rotate variants (whoosh_1489/1490/1492,
   pop_2358/2364/3005); gain -12 normal, -16 subtle, -10 for a hit, -8 only for the single biggest moment.
   Place them on the transition, on big text, on the dramatic word's onset, or in a gap — never masking speech.
   Use `work/audio_events.json` (laughter, thumps, peaks) + the picture to justify funny SFX.
5. No "next part" teaser at the end unless the user asks.
6. Levels: `lint` compares the loudness of every piece; treat its `vol` suggestions as hints and confirm by listening.
7. Keep the plan readable: one piece per line of thought; a v2 plan is a copy with the reviewer's fixes.
