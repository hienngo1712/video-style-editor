# Quy trình chi tiết (bản tối ưu sau 4 vòng sửa, 10/2026)

Mọi bước chạy qua một lệnh: `python3 scripts/vse.py <bước> ...`
Trong Cowork thêm `VSE_HOME=<thư mục đã cấp quyền>/.vse-data VSE_BUDGET=150` trước mỗi lệnh.
Nếu lệnh in `CONTINUE` (mã thoát 3) → chạy lại đúng lệnh đó, tiến độ đã được lưu.

## A. Edit một video

| # | Bước | Lệnh | Ai làm | Đầu ra |
|---|---|---|---|---|
| 0 | Cài/kiểm tra máy | `doctor --fix` | máy | model, font, SFX trong `VSE_HOME` |
| 0b | Đọc khẩu vị người dùng: thông số, SFX thích/cấm, chính tả, luật, góp ý gần đây | `style show` (lần đầu `style init`) | máy → Claude | áp dụng khi viết plan |
| 1 | Kiểm kê, tách audio, ảnh ghép; chép lời từng chữ; tiếng cười/va đập | `analyze PROJECT` | máy | `work/clips.json`, `thumbs/`, `transcript.json`, `audio_events.json` |
| 2 | Dựng câu chuyện: kết, teaser, mở, thân | – | Claude | dàn ý |
| 3 | Chọn điểm cắt trong khoảng lặng | `inspect PROJECT CLIP S E` | Claude | mốc a/b |
| 4 | Viết edit plan: cắt, zoom, sửa chữ, chữ to, chuyển cảnh, SFX, âm lượng | – | Claude | `plans/<tên>.json` |
| 4b | Cắt tiếng đệm (ờ, ừm, à/ừ đứng riêng) + khoảng lặng > 0,45 s; xem danh sách "có tiếng mà không có chữ" | `tighten PROJECT plans/<tên>.json plans/<tên>-t.json` | máy → Claude | plan `-t` liền mạch |
| 5 | Soát plan: dòng thời gian, lỗi, cảnh báo | `lint PROJECT plans/<tên>.json` | máy → Claude | 0 lỗi |
| 6 | Dựng: từng đoạn (cache) → ghép → phụ đề → SFX → −12 LUFS (tự động: lọc ồn, cân sáng, màu chung, zoom mềm có keyframe, chữ né mặt, phụ đề hiện sau tiếng nói 0,2 s từng chữ) → bản nghe thử 540p | `render PROJECT plans/<tên>.json` | máy | `output/<tên>.mp4`, `output/review/` |
| 7 | Kiểm tra hình + độ to | `check PROJECT plans/<tên>.json` | máy → Claude | `work/check/<tên>_sheet.jpg` |
| 8 | Nghe duyệt: Gemini (qua Chrome) hoặc người nghe | `docs/gemini-review.md` | Gemini/người → Claude | `plans/<tên>-v2.json` |
| 9 | Báo cáo | – | Claude | đường dẫn, độ dài, chỗ cần người xem lại |
| 10 | Hỏi góp ý, ghi lại; góp ý lặp lại → đề xuất sửa my-style (người dùng duyệt) | `style note` / `style learn` | người dùng → Claude | `my-style/journal.md`, `preferences.yaml` |

Vòng 6 → 8 lặp đến khi người nghe không còn lỗi bắt buộc (mục tiêu ≥ 8,5/10). Sửa plan rồi render lại
chỉ dựng lại các đoạn thay đổi.

## B. Những gì đã học qua 4 vòng sửa (đã đưa vào profile + lint)

| Lỗi người nghe bắt được | Cách xử lý giờ đã thành quy tắc |
|---|---|
| Câu teaser cụt đầu, khó hiểu | teaser phải có chủ ngữ, 5–15 s |
| Cuối phần 1 hiện đầu phần 2 | không thêm "tập sau" nếu không được yêu cầu |
| SFX nhỏ không nghe thấy / to đè chữ | chuẩn hoá đỉnh SFX + bảng gain trong profile; lint cảnh báo SFX rơi vào chữ |
| Đoạn khử ồn bị hụt tiếng, mất đầu chữ | khử ồn có 0,5 s đệm trước |
| Thoại nhỏ ở cảnh xa máy | `vol` +3..+5 (+ `denoise` nếu ồn); lint so độ to giữa các đoạn |
| Chữ thừa "Đây, phòng…" ở điểm cắt | `inspect` → cắt trong khoảng lặng, bỏ câu nói lại |
| Câu bị băm vụn nhiều vết cắt | gộp thành 1 đoạn |
| Hụt tiếng giữa câu khi đổi zoom | đoạn liền nhau chỉ fade 10 ms |
| Gió ngoài trời | `denoise` + `vol` −2 |
| Nhận dạng sai chữ ("căn cứ" → "khách khứa") | sửa `fix` theo ngữ cảnh, người nghe xác nhận |

## B2. Góp ý của 3 editor chuyên (10/2026, xem cả 8 video)
Lọc ồn chưa có · SFX đơn điệu/chói · chưa cân sáng, chưa có màu chung · chữ lòi khỏi vùng an toàn TikTok, phụ đề che
giữa hình · từ khoá nên 1–2 kiểu hiệu ứng cố định · cần heading sẵn · chuyển cảnh chỉ ở đầu.
Cách xử lý + bài học khoá CapCut 16 bài: `docs/editing-craft.md` (mục 11 = bảng góp ý → trạng thái, mục 12 = backlog
cho `render.py`).

## C. Học style mới từ video mẫu (1 lần / style)
1. Chọn 5–8 video tiêu biểu (cả nhiều view và ít view), file hợp lệ, vào `<thư-viện>/<style>/videos/`, tên
   `<style>__<format>__<nội-dung>__<view>.mp4` - không chứa tên người (kênh ghi mã k1, k2 trong INDEX).
2. `vse.py reference <thư-viện>/<style>` → điểm cắt, độ dài cảnh, khoảng lặng, LUFS, ảnh ghép, 3 giây đầu;
   `vse.py transcribe …` → lời thoại; `vse.py library <thư-viện>` → cập nhật `INDEX.md`.
3. Claude xem ảnh ghép + số đo + lời thoại, viết `profiles/<style>.yaml` theo mẫu `story-vlog.yaml`.

## Thời gian tham khảo
Laptop 2 nhân (máy ảo Cowork), 31 clip iPhone ~11 phút → 2 video ~55 s:
analyze ~2 phút, viết plan 10–20 phút (Claude), render ~2,5 phút/video, một vòng Gemini ~3 phút.

## Giới hạn
- Claude không nghe trực tiếp: dựa vào lời thoại, độ to, sự kiện âm thanh, hình — và Gemini/người để nghe.
- Mức độ to giữa các đoạn do máy đo chỉ là gợi ý; tai người nghe quyết định.
- Làm mờ mặt, sticker bám vật thể: chưa tự động.
