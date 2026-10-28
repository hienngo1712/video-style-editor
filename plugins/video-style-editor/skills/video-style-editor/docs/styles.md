# Danh mục style (chọn khi giao việc)

Mỗi style = 1 file `profiles/<tên>.yaml`. Nói với Claude: *"edit theo style <tên>, dạng <format>"*. Nếu không nói,
Claude chọn theo bản thô: một người kể chuyện → `story-vlog`; nhiều người đối thoại / diễn tình huống →
`office-sitcom`; một người review/thử → `review-xam`; người bán, khách hàng → `street-kindness`; có kịch bản,
diễn viên → `mini-drama`; thú cưng → `pet-dub`; clip đẹp không lời → `trend-aesthetic`.

| Style | Hợp với bản thô | Dài | Mở đầu | Phụ đề | Âm thanh | Hiệu ứng đặc trưng |
|---|---|---|---|---|---|---|
| `story-vlog` | 1 người cầm máy kể, sự kiện, tham quan, chuyển văn phòng | 45 s - 10 phút | teaser 5-15 s lấy câu đắt nhất | 3 chữ, chữ đang nói tô vàng | không nhạc nền, SFX điểm nhấn | chữ vàng khổng lồ, xé giấy, rung + tia tốc độ |
| `office-sitcom` · `skit` | 2-4 người diễn 1 tình huống văn phòng | 25-50 s | câu mâu thuẫn ngay giây 0 | cả dòng, màu theo người nói, từ khoá vàng | nhạc nền nhẹ + SFX hài (boing, vịt, quạ, dế) | cận mặt + lọc hồng khi phản ứng |
| `office-sitcom` · `challenge_or_diary` | 1 nhân vật làm thử thách / nhật ký có mốc giờ | 90-170 s | nói luật chơi ngay câu đầu | như trên | + tiếng tích tắc dưới mốc giờ | chữ to "9H - 10H", "2 TIẾNG SAU" |
| `office-sitcom` · `brand_skit` | skit có nhãn hàng / app | 100-130 s | mâu thuẫn văn phòng | như trên | + tiếng pop khi chèn ảnh app | ảnh chụp app chèn lên hình (piece.image) |

| `review-xam` | 1 người review quán, món, sản phẩm, dịch vụ | 90-250 s | tự nhận + câu hỏi so sánh ("KFC Mỹ có ngon hơn VN?") | ít chữ, tiêu đề cố định trên đầu | giọng + nhạc nhẹ | khung facecam nhỏ góc trên (video PiP) |
| `pet-dub` | thú cưng văn phòng/quán, linh vật | 20-40 s | hình lạ ngay khung đầu | phụ đề cho lời lồng tiếng | nhạc trend hoặc lồng tiếng (piece.audio) | lồng tiếng như talk show / phỏng vấn |
| `street-kindness` | chuyện người bán, khách hàng, cửa hàng nhỏ; series | 150-300 s | tên series to + đồ vật ("GIỎ XÁCH BÁNH CAM") | karaoke, giá/tuổi tô vàng | giọng ngoài đường (khử ồn) + piano nhẹ | tập nối tiếp, quay lại thăm |
| `mini-drama` | kịch bản có diễn viên, parody, tình huống CSKH | 90-120 s | câu thoại vào vai, tình huống phi lý | phụ đề kiểu phim, nhỏ, dưới | thoại + nhạc phim | màu điện ảnh, "Tập 1, 2…" |
| `trend-aesthetic` | ra mắt món/cửa hàng, hậu trường đẹp | 15-22 s | khung đẹp nhất + âm thanh trend | không chữ | âm trend (thêm khi đăng TikTok) | lọc màu mạnh, cắt theo nhịp |

## Trộn style

Có thể mượn từng phần: ví dụ vlog chuyển văn phòng (story-vlog) nhưng phụ đề màu theo người nói và nhạc nền nhẹ của
sitcom - ghi rõ trong plan (`style.caption_mode`, `speakers`, `music`).

## Thêm style mới

1. 6-8 video mẫu (cả view cao và thấp) vào `<thư-viện>/<style>/videos/`, đặt tên
   `<style>__<format>__<nội-dung>__<view>.mp4` (không tên người; kênh nguồn ghi mã k1, k2 trong INDEX).
2. `vse.py reference <thư-viện>/<style>`, `vse.py transcribe …`, `vse.py events …`, rồi `vse.py library <thư-viện>`.
3. Claude đọc `analysis/*/hook.jpg` (3 giây đầu), `sheet_*.jpg`, `summary.json`, lời thoại → viết profile mới theo mẫu
   `office-sitcom.yaml` và thêm 1 dòng vào bảng trên + bằng chứng vào `viral-formula.md`.
