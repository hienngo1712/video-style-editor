---
name: storytelling
description: "3 thẻ hình phía trên + tiêu đề nền đen + phụ đề nhỏ, hiện cùng lúc trên một đoạn quay liền, phụ đề kiểu TikTok. Shortcut of the video-style-editor plugin: use when the user runs /storytelling or asks for story / proof reel, '3 ảnh + tiêu đề', lead-magnet style on a 9:16 talking-head clip."
---

# /storytelling - lối tắt của video-style-editor

3 thẻ hình phía trên + tiêu đề nền đen + phụ đề nhỏ, hiện cùng lúc trên một đoạn quay liền, phụ đề kiểu TikTok.

This skill is only a shortcut. Everything lives in the main skill next to it:
`MAIN = <this skill's base directory>/../video-style-editor` (the plugin's `skills/video-style-editor/`).

1. Read `MAIN/SKILL.md` section 0 (setup: run on the user's linked computer, `VSE_HOME=<connected folder>/vse-workspace`,
   `V="python3 MAIN/scripts/vse.py"`) and section 1b (reel layouts), then `MAIN/reels/storytelling/GUIDE.md` - follow it.
2. The text after `/storytelling` is the clip and any wishes ("IMG_1234 trong projects/quan-moi, chọn đoạn hay nhất").
   No clip given: list `$VSE_HOME/projects/*/raw/` and ask which one (one short question).
3. Apply the user's my-style (`$V style show`): rules, caption spellings, things they dislike.
4. Build with `$V reel build storytelling <spec>` (exit 3 / CONTINUE = run it again), check the sheet, hand over the mp4 from
   `<job>/output/`, then ask for feedback and record it (`$V style note ... --tag reels`).

Based on claude-editing-skills by Artem Novitckii (MIT) - see `MAIN/reels/NOTICE.md`.
