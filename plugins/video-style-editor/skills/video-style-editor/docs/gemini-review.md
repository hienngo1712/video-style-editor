# Optional: let Gemini "listen" to the cut

Claude cannot hear audio. A multimodal model that takes video (Gemini web, model Argon or newer) can,
and its notes are good at: SFX too loud / masking a word, clipped word heads/tails, level jumps between
scenes, wind/room noise, captions that do not match the speech.

## Workflow (Claude in Chrome, user already signed in to gemini.google.com)
1. `vse.py render` already made `output/review/NAME-review.mp4` (540p, ~6 MB for 1 min; the browser
   upload tool takes up to 10 MB). Redo it alone with `vse.py render PROJECT plans/NAME.json review`.
   In Cowork, stage that file to the cloud workspace first - the upload tool reads from there.
2. Upload it: add a hidden `<input type=file>` to the page whose `change` handler pastes the file into the
   prompt box (`ClipboardEvent('paste')` with a `DataTransfer` on `.ql-editor`), then use the browser
   file-upload tool on that input. Type the prompt with `document.execCommand('insertText', ...)`.
3. Ask for a fixed structure so answers are comparable between versions:
   1. every SFX: time, clear?, masks speech?, fits?, keep/fix/drop (+ dB / s);
   2. voice & cut problems (clipped words, level jumps, noise);
   3. SFX to add; 4. captions that are *wrong* (not "missing" - captions show 3 words at a time and Gemini
   samples ~1 frame/s); 5. score /10 + top 3 fixes.
4. Map Gemini's timestamps to pieces with the timeline printed by `vse.py lint`, verify each claim against `work/transcript.json`
   and `vse.py inspect` before changing the plan - Gemini's times can be ~0.5 s off and some
   "missing caption" notes are sampling artefacts.
5. Apply fixes in a new plan (`NAME-v2.json`), render, run check.py, send the new review copy with a
   short list of what changed and ask what is still wrong.

Typical fixes: `vol` +3..+5 for quiet takes, `denoise` for wind/rustle, SFX gain -2..-5 dB, move an SFX
0.1 s earlier or into the pause after the line, trim a stray word at a cut, merge two pieces when the
cut between them sounds choppy.

The Gemini API (`generativelanguage.googleapis.com`) does the same headlessly but needs the user's own
API key and network access; never type a key for the user.

## What it achieved (van-phong project, Oct 2026)
Part 1: 6.5 -> 8.5 -> 9.5 / 10. Part 2: 6.0 -> 8.8 / 10 after one round. The fixes it found that the
scripts could not: a restart word left at a cut, reaction SFX masking the punchline, a quiet far-mic take,
wind on a rooftop, an ASR error ("căn cứ" was "khách khứa"), a stray "ok" before a line.
