# video-style-editor - Claude plugin

Plugin + skill cho Claude: **tự động dựng video dọc 9:16 từ bản thô**, theo một phong cách học từ video mẫu, và
**học dần khẩu vị dựng của chính bạn** qua từng lần góp ý.

- **Bộ khung chung, ai cũng dùng được ngay**: chép lời tiếng Việt, dựng câu chuyện + teaser, cắt nhảy, phụ đề karaoke,
  chữ lớn, SFX, nhạc nền, lọc ồn, cân màu, zoom có keyframe, xuất MP4 - với các quy tắc rút từ khoá CapCut 16 bài và
  góp ý của editor chuyên nghiệp (`docs/editing-craft.md`).
- **6 bố cục reels thiết kế sẵn** (`vse.py reel`, `docs/reels.md`): trial-reels (3 bản để đăng thử), chữ/đồ hoạ
  phía sau người, explainer trước → sau, chia đôi màn hình, bảng xếp hạng S-F, 3 thẻ hình + tiêu đề - dựa trên bộ
  skill của Artem Novitckii (MIT), chạy trong máy, chữ tiếng Việt có dấu.
- **7 style có sẵn** (`profiles/`): vlog kể chuyện, sitcom văn phòng, review, đường phố, mini drama, thú cưng lồng
  tiếng, video mood - và tự tạo style mới từ video mẫu bạn thích.
- **my-style - phần của riêng bạn**: thông số mặc định, SFX thích / cấm, chính tả phụ đề, luật riêng và nhật ký góp
  ý. Mỗi video bạn góp ý, Claude ghi lại; góp ý lặp lại thành quy tắc (bạn duyệt) → video sau tự đúng
  (`docs/personalize.md`).

> **Mới dùng AI lần đầu?** Đọc [hướng dẫn cho người mới](plugins/video-style-editor/skills/video-style-editor/docs/huong-dan-nguoi-moi.md): cài Claude, cài plugin, prompt mẫu để
> cấu hình nhanh và dựng video đầu tiên - từng bước, không cần biết lập trình.

Máy làm phần lặp lại (chép lời, cắt, ghép, phụ đề, hiệu ứng); Claude làm phần biên tập (câu chuyện, teaser, điểm cắt,
sửa chữ, nhấn mạnh, SFX) và ghi thành **edit plan** JSON.

```
bản thô ─► analyze ─► [Claude viết plan theo style + my-style] ─► tighten ─► lint ─► render ─► check ─► MP4
                                   ▲                                                                   │
                                   └──────────── góp ý của bạn ─► vse.py style note / learn ◄──────────┘
```

## Cài đặt

**Claude desktop (Cowork / Chat):** Customize → Plugins → Add marketplace → nhập `hienngo1712/video-style-editor`
→ cài **video-style-editor**. Bật *auto-update* để luôn có bản mới.

**Không qua GitHub (chỉ skill):** Settings → Capabilities → bật *Code execution and file creation*; rồi Customize →
Skills → **+** → Create skill → Upload a skill → chọn
`dist/video-style-editor-skill.zip` (tạo bằng `python tools/build_skill_zip.py`).

**Claude Code:**
```
/plugin marketplace add hienngo1712/video-style-editor
/plugin install video-style-editor@hien-video-tools
```

**Nên dùng trong Cowork** (Claude desktop): bấm *Add folder* chọn thư mục làm việc (ví dụ `Downloads`). Claude chạy
script trong máy ảo Linux của Cowork trên chính máy bạn - không cần tự cài Python / FFmpeg, không phải upload video.
Lần đầu Claude chạy `vse.py doctor --fix` (cài thư viện, tải model / font / SFX ~300 MB), `vse.py style init`, rồi
**hỏi bạn vài vòng câu hỏi** về thói quen và phong cách dựng (`docs/onboarding.md`) và dựng thử 15 giây đầu để chỉnh
- để video đầu tiên đã đúng ý.

**Claude Code trên máy riêng:** cần Python 3.10+ và [FFmpeg](https://ffmpeg.org/download.html).

## Thư mục làm việc của bạn (VSE_HOME)

Mọi thứ của riêng bạn nằm **ngoài** plugin, trong một thư mục (biến `VSE_HOME`; trong Cowork:
`<thư mục đã cấp quyền>/vse-workspace`, trên máy riêng mặc định `~/.video-style-editor`). Cập nhật plugin không đụng tới.

```
vse-workspace/
├── my-style/            khẩu vị của bạn: preferences.yaml, journal.md, feedback.jsonl
├── projects/<video>/    raw/ (bản thô) · plans/ · work/ (tạm) · output/ (thành phẩm + review/)
├── references/<style>/  video mẫu để học style mới (không chia sẻ, không đưa lên git)
└── models/ fonts/ sfx/ overlays/    tải về tự động
```

## Dùng hằng ngày

Bỏ bản thô vào `vse-workspace/projects/video-1/raw/`, rồi nói với Claude: *"Dựng video-1 theo style story-vlog"*.
Claude sẽ: đọc my-style → phân tích → viết plan → cắt tiếng đệm → dựng → kiểm tra → báo cáo → **hỏi bạn góp ý và ghi
lại**. Góp ý càng cụ thể (giây thứ mấy, muốn thế nào) thì lần sau càng đúng.

Chạy tay (không cần Claude) - `V="python3 plugins/video-style-editor/skills/video-style-editor/scripts/vse.py"`:
```bash
$V doctor --fix                                   # lần đầu: thư viện, model, font, SFX
$V style init | show | stats | brief              # my-style của bạn
$V style set style.caption_size 88                # chỉnh một thông số · style rule "..." · style word "asr" "Đúng"
$V style note "chữ hiện sớm" --at 0:12 --tag captions   # ghi một góp ý
$V style learn  video-1 plans/a.json plans/b.json # học từ chỗ bạn sửa plan
$V analyze  video-1                               # chép lời, ảnh ghép, sự kiện âm thanh
$V inspect  video-1 IMG_1234 0 10                 # chữ + độ to + khoảng lặng của 1 clip
$V tighten  video-1 plans/v1.json plans/v1-t.json # cắt ờ/à/ừ + khoảng lặng thừa
$V lint     video-1 plans/v1-t.json               # dòng thời gian + lỗi plan
$V render   video-1 plans/v1-t.json               # dựng (chỉ dựng lại đoạn thay đổi)
$V check    video-1 plans/v1-t.json               # ảnh kiểm tra, độ to, độ sáng, phụ đề chồng
$V reel build explainer projects/video-1/plans/IMG_1.explainer.json   # bố cục reels (docs/reels.md)
```
Người mới: `docs/huong-dan-nguoi-moi.md` · quy trình chi tiết: `docs/workflow.md` · định dạng plan: `docs/edit-plan.md` · tuỳ chỉnh: `docs/personalize.md` ·
phỏng vấn lần đầu: `docs/onboarding.md`.

## Cấu trúc repo

```
.claude-plugin/marketplace.json            danh mục plugin (marketplace "hien-video-tools")
plugins/video-style-editor/
├── .claude-plugin/plugin.json
├── skills/<6 kiểu reels>/SKILL.md         lối tắt /trial-reels, /explainer... (trỏ về skill chính)
└── skills/video-style-editor/             = nội dung file zip skill
    ├── SKILL.md                           hướng dẫn cho Claude
    ├── scripts/                           vse.py (1 lệnh cho mọi bước) + các bước: prepare, transcribe, audio_events,
    │                                      tighten, planlint, render, faces, check, mystyle, doctor, setup_assets…
    ├── reels/                             6 bố cục reels (kit HyperFrames + từng bố cục: build.py, GUIDE.md)
    ├── profiles/                          7 style - thêm style = thêm 1 file
    ├── templates/my-style/                mẫu preferences.yaml + journal.md cho người dùng mới
    ├── docs/                              huong-dan-nguoi-moi (cho người dùng), workflow, edit-plan, personalize,
    │                                      onboarding, editing-craft, styles, viral-formula, capcut-guide, gemini-review
    ├── examples/                          plan mẫu
    └── assets/sfx/manifest.json           danh sách SFX (tải về khi setup)
tools/build_skill_zip.py                   đóng gói dist/video-style-editor-skill.zip
CHANGELOG.md
```

## Cập nhật & phát triển

- Plugin không ghi `version` → mỗi lần push lên `main` là một bản mới. Người dùng nhận bản mới:
  - **Cowork / Claude desktop:** bật **Sync automatically** cho marketplace một lần (Customize → Plugins → marketplace)
    → tự cập nhật; mở cuộc trò chuyện mới là dùng bản mới. Lấy ngay: **Check for updates**.
  - **Claude Code:** marketplace bên thứ ba mặc định **tắt** tự cập nhật. Bật một lần: `/plugin` → tab
    **Marketplaces** → `hien-video-tools` → **Enable auto-update**. Lấy ngay: cùng chỗ đó chọn **Update marketplace**
    (hoặc `claude plugin update video-style-editor@hien-video-tools`), rồi `/reload-plugins` hoặc mở phiên mới.
- Sửa code trong `plugins/video-style-editor/skills/video-style-editor/`, ghi vào `CHANGELOG.md`,
  chạy `python tools/build_skill_zip.py`, push.
- Quy tắc đúng cho **mọi** người → `SKILL.md` mục 3 / `docs/editing-craft.md`. Khẩu vị **của một người** → my-style
  của người đó, không đưa vào repo.
- Thêm style: video mẫu vào `<VSE_HOME>/references/<style>/videos/` tên `<style>__<format>__<nội-dung>__<view>.mp4`
  (không tên người), `vse.py reference`, `vse.py library`, viết `profiles/<style>.yaml` (`docs/styles.md`).

## Bản quyền & lưu ý

- Thư mục `reels/` dựa trên [claude-editing-skills](https://github.com/artemnovitckii/claude-editing-skills)
  của Artem Novitckii (MIT) - chi tiết `reels/NOTICE.md`; model tách người RobustVideoMatting (GPL-3.0) tải khi dùng.
- Code: MIT. Nhận dạng giọng nói / âm thanh: [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) (Apache-2.0).
  Lọc ồn: model RNNoise "leavened-quisling" từ [rnnoise-models](https://github.com/GregorR/rnnoise-models)
  (README: dữ liệu model không thuộc bản quyền). Dò mặt: YuNet từ [opencv_zoo](https://github.com/opencv/opencv_zoo)
  (MIT), thư viện `opencv-python-headless` (Apache-2.0). Font Be Vietnam Pro: SIL OFL 1.1. Tất cả tải về khi chạy
  `doctor --fix`, không nằm trong repo.
- Sound effect [Mixkit](https://mixkit.co/license/#sfxFree): miễn phí dùng trong video nhưng **không được phát hành lại
  kèm công cụ** → repo chỉ chứa danh sách, mỗi người tự tải.
- Không commit video, bản thô, my-style hay video mẫu của người khác (`.gitignore` chặn file media / model).
- Phụ đề lấy từ nhận dạng giọng nói tự động - luôn xem lại trước khi đăng.
