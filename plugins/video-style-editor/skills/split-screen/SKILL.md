---
name: split-screen
description: "Chia đôi màn hình: trên là nhãn bước + tiêu đề + cửa sổ minh hoạ (lưới ảnh có con trỏ, ảnh chụp màn hình, danh sách tích dần), dưới là người nói. Shortcut of the video-style-editor plugin: use when the user runs /split-screen or asks for split screen, half and half, tutorial step reel, 'chia đôi màn hình', 'bước 1' on a 9:16 talking-head clip."
---

# /split-screen - lối tắt của video-style-editor

Chia đôi màn hình: trên là nhãn bước + tiêu đề + cửa sổ minh hoạ (lưới ảnh có con trỏ, ảnh chụp màn hình, danh sách tích dần), dưới là người nói.

This skill is only a shortcut. Everything lives in the main skill next to it:
`MAIN = <this skill's base directory>/../video-style-editor` (the plugin's `skills/video-style-editor/`).

1. Read `MAIN/SKILL.md` section 0 (setup: run on the user's linked computer, `VSE_HOME=<connected folder>/vse-workspace`,
   `V="python3 MAIN/scripts/vse.py"`) and section 1b (reel layouts), then `MAIN/reels/split-screen/GUIDE.md` - follow it.
2. The text after `/split-screen` is the clip and any wishes ("IMG_1234 trong projects/quan-moi, chọn đoạn hay nhất").
   No clip given: list `$VSE_HOME/projects/*/raw/` and ask which one (one short question).
3. Apply the user's my-style (`$V style show`): rules, caption spellings, things they dislike.
4. Build with `$V reel build split-screen <spec>` (exit 3 / CONTINUE = run it again), check the sheet, hand over the mp4 from
   `<job>/output/`, then ask for feedback and record it (`$V style note ... --tag reels`).

Based on claude-editing-skills by Artem Novitckii (MIT) - see `MAIN/reels/NOTICE.md`.
