# Reel layouts - nguồn gốc và giấy phép

Thư mục `reels/` dựa trên **claude-editing-skills** của **Artem Novitckii**
(https://github.com/artemnovitckii/claude-editing-skills · https://novitckii.com/resources/editing-skills/),
phát hành theo giấy phép MIT - toàn văn trong `LICENSE-artem-novitckii.txt` (giữ nguyên, bắt buộc khi phân phối lại).
Lấy 6 bố cục gốc ở commit `beff6b8`: trial-reels, behind-the-person, explainer, split-screen, ranking-list, storytelling.

## Đã thay đổi so với bản gốc
- `kit/transcribe.py`: viết lại - chép lời tiếng Việt chạy trong máy (sherpa-onnx Zipformer + Silero VAD, cùng model
  với `vse.py analyze`) thay cho Groq Whisper; không cần API key, âm thanh không rời máy. Mỗi khoảng lặng kết thúc
  một "câu" (ASR không có dấu câu).
- `kit/reel.py`: đường dẫn theo project (`<job>/work/reels`, `<job>/output`), chính tả phụ đề từ my-style `words` +
  `fix` trong spec, tone map HDR iPhone sang SDR, render có cache và giới hạn thời gian (VSE_BUDGET / CONTINUE),
  không xoá file (thư mục Cowork có thể chặn xoá), font có dấu tiếng Việt.
- `kit/runtime.py`: mới - cài HyperFrames, GSAP và Chromium (@sparticuz/chromium) từ npm vào `$VSE_HOME/reels-runtime`
  (mạng Cowork thường chặn GitHub release / Google storage / cdnjs nhưng cho npm).
- `kit/cutout.py`: tách người theo từng đoạn, lưu trạng thái để chạy tiếp được; model tải vào `$VSE_HOME/models`.
- `kit/fonts/`: thay font không có dấu tiếng Việt bằng font tương đương có dấu (đều SIL OFL 1.1, lấy từ Fontsource):
  Inter (thêm bộ chữ Việt), Montserrat 900 thay Archivo Black, Playfair Display 600 italic thay DM Serif Display,
  Noto Serif Display thay Instrument Serif, VT323 thay Pixelify Sans. TikTok Sans giữ nguyên (đổi sang woff2). Giấy phép: `OFL-*.txt`.
- `<layout>/build.py`: chỉ đổi đường dẫn tới kit. `<layout>/GUIDE.md`: từ SKILL.md gốc, thay phần cài đặt và lệnh
  bằng `vse.py reel ...`.

## Thành phần bên thứ ba (tải về khi chạy, không nằm trong repo)
- HyperFrames (HeyGen) - dựng HTML + GSAP thành MP4. GSAP (GreenSock) - hiệu ứng chuyển động.
- @sparticuz/chromium - bản Chromium chạy không giao diện cho Linux.
- RobustVideoMatting (Shanchuan Lin và cộng sự, **GPL-3.0**) - model tách người, tải từ GitHub release của tác giả
  vào `$VSE_HOME/models` khi dùng lần đầu; không phân phối kèm repo này.
- Ảnh, video mẫu và 5 kiểu "photographic styles" của repo gốc **không** được đưa vào đây.
