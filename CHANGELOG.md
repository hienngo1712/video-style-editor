# Changelog

## 2026-10-31
- Học từ "editing studio" của Artem Novitckii: storyboard duyệt trước khi dựng cả video; `lint` cảnh báo một câu bị
  giữ hai lần (hai lần nói); mỗi bản sửa là `-v2`, `-v3` (không ghi đè); `style rule --why` ghi kèm ngày + lý do;
  `style approve` lưu bản được duyệt (ảnh tóm tắt + lý do) làm chuẩn, `style show` liệt kê; học style kỹ hơn:
  `notes.txt` của người dùng, `first10.jpg`, `first_cut_s`, `hook_motion`, tiếng hiệu ứng trùng điểm cắt
  (`onsets.txt`, `cuts_with_hit`), xem 3 ảnh trước khi viết style, đặt tên theo kiểu nhìn.
- Lệnh gọi nhanh `/trial-reels`, `/behind-the-person`, `/explainer`, `/split-screen`, `/ranking-list`, `/storytelling`:
  6 skill lối tắt trong plugin (`plugins/video-style-editor/skills/<tên>/SKILL.md`) trỏ về skill chính.
  Hướng dẫn người mới thêm phần dùng nâng cao (lệnh `/`, 6 kiểu reels, my-style, Gemini, cập nhật).
- **6 bố cục reels** (`vse.py reel`, `reels/`, `docs/reels.md`) từ claude-editing-skills của Artem Novitckii (MIT):
  trial-reels, behind-the-person, explainer, split-screen, ranking-list, storytelling. Chuyển sang chạy trong máy và
  tiếng Việt: chép lời bằng model tiếng Việt cục bộ thay Groq (không cần key), font có dấu, nhãn mặc định tiếng Việt,
  HDR iPhone → SDR, bộ dựng HyperFrames + Chromium cài từ npm (mạng Cowork chặn GitHub/Google storage), render chia
  đoạn 2 s và tách người theo đoạn để chạy tiếp được sau giới hạn 3 phút, không xoá file trong thư mục chia sẻ.
  Đã dựng thử cả 6 kiểu trên clip tiếng Việt.

## 2026-10-28
- **Beginner guide** (`docs/huong-dan-nguoi-moi.md`, Vietnamese): install the Claude desktop app on a Pro plan, enable
  code execution, add the plugin (marketplace or skill zip), connect a folder, then copy-paste prompts for setup, the
  style interview, the first edit and feedback; daily prompt table, saving usage, troubleshooting.
- **First-use interview** (`docs/onboarding.md`): 7 short rounds about goals, pacing, text, audio, picture, brand and
  reference videos, recorded with `vse.py style set / rule / word` and a `brief.md` portrait; 15 s preview before the
  first full render.
- **my-style - the skill learns your taste**: `vse.py style init|show|note|learn|stats`, `<VSE_HOME>/my-style/`
  (`preferences.yaml` defaults for every render, SFX likes/bans, caption spellings, rules; `journal.md` feedback log).
  Render, lint and tighten read it. Guide: `docs/personalize.md`.
- Workspace layout: everything personal lives in `VSE_HOME` (`models/ fonts/ sfx/ my-style/ projects/ references/`),
  nothing personal in the plugin / repo.
- Captions land ~0.2 s after the word is heard and fill in word by word; big text follows the voice; no stacked
  duplicate caption lines (`check` counts overlaps).
- Picture/sound no longer drift apart over many pieces (frame-exact pieces, PCM between steps).
- `vse.py tighten`: cuts fillers (ờ, ừm, lone à/ừ) and long pauses; lists voiced gaps the ASR did not transcribe.
- Motion: eased push-in / pull-out, punch-in on big text aimed at the face, `transition: zoom`.
- Text avoids faces (YuNet face detector), TikTok safe-zone guides in `check`.
- Audio: RNNoise speech denoise (60 % by default), -12 LUFS, SFX repeat limit in lint.
- Colour: per-clip exposure match, one shared look (`clean` / `warm` / `cool` / `film` / `.cube`), HDR -> SDR.
- Final render in resumable 12 s chunks (fits Cowork's per-command time limit).
- Fixes: silent clips, paths with special characters, opencv slowing ffmpeg 20x, empty face cache, tighten copying
  image / move to every sub-piece.

## 2026-10-25
- First public version: analyse, plan, lint, render, check, Gemini listening review, 7 style profiles, CapCut guide.
