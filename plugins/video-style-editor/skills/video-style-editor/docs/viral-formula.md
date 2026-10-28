# Công thức viral (rút ra từ thư viện mẫu, 10/2026)

Thư viện: 39 video mẫu của 8 kênh, xếp theo style, tên file dạng `<style>__<format>__<nội-dung>__<view>`
(xem `INDEX.md` của thư mục mẫu). Kênh nguồn được ghi bằng mã (`office-sitcom/k1`...), không ghi tên người.
Số đo bằng `vse.py reference` (cắt cảnh, nhịp, độ to) + lời thoại (`transcribe`) + nhãn âm thanh (`events`) +
ảnh ghép khung hình.

## office-sitcom (k1: 1,1M follow, trung vị ~665K view/video; k2: 1M follow, trung vị ~694K)

| Mẫu | View | Dài | Shot TB | Cắt/phút | Cắt trong 5 s đầu | Câu mở đầu |
|---|---|---|---|---|---|---|
| k1 `brand-skit__doi-sep-bao-com-trua` | 56,9M | 107 s | 1,8 s | 32 | 2 | đòi sếp bao suất cơm 39K |
| k2 `brand-skit__tro-ly-ai-cho-dan-van-phong` | 53,3M | 122 s | 1,8 s | 33 | 3 | sếp mắng vì sáng giờ chưa làm việc |
| k2 `skit__xin-ve-som` | 10,5M | 38 s | 2,1 s | 27 | 2 | "Em xin về sớm nhá" |
| k1 `brand-skit__xin-vao-phong-sep-moi-banh` | 8M | 117 s | 1,9 s | 31 | 2 | đòi vào phòng sếp |
| k2 `skit__bat-ngu-lai-cong-ty` | 6,3M | 33 s | 1,9 s | 29 | 2 | "Cho chúng mày ngủ lại công ty" |
| k1 `challenge__lam-viec-den-khi-tra-sua-tan` | 6,1M | 161 s | 2,6 s | 23 | 2 | "Thử thách làm việc đến khi cốc trà sữa tan" |
| k1 `skit__tron-sep-di-an-khi-lam-toc` | 5,7M | 101 s | 2,2 s | 27 | 2 | xin 15 phút ra ngoài ăn |
| k2 `greenscreen__qua-nhieu-cuoc-goi` | 5,7M | 49 s | 7,0 s | 7 | 0 | "Phải tuyển bao nhiêu nhân viên để trả lời hết cuộc gọi" |
| k1 `skit__luong-3-trieu-bieu-bo` | 3,9M | 134 s | 2,2 s | 26 | 3 | "Lương 3 triệu nhưng không dám biếu bố 2 triệu" |
| k2 `skit__kiem-ke-do-tra-no` | 3,8M | 229 s | 2,2 s | 27 | 3 | "Sao mày lại cắn nội thất?" |
| k1 `diary__nhat-ky-di-lam-mot-ngay` | 1,2M | 127 s | 2,3 s | 26 | 3 | "Nhật ký đi làm…" |
| k2 `skit__di-lam-mung-2-tet` | 1,1M | 131 s | 3,2 s | 18 | 1 | "Biết nhân viên yêu công ty là như nào không?" |
| k1 `event-vlog__sinh-nhat-dong-nghiep` | 220K | 170 s | 2,8 s | 21 | 1 | không có tiền đề, nhạc + ồn |
| k2 `brand-skit__quang-cao-phim-mat-tri-nho` | 140K* | 116 s | 2,6 s | 22 | 2 | "Mày xem phim … chưa?" |
| k1 `skit__bi-bo-lai-cong-ty-buoi-toi` | 142K | 29 s | 1,7 s | 33 | 2 | "Công ty về hết rồi anh nỡ để em ở lại" |
| k2 `skit__phong-van-co-laptop-ca-nhan` | 159K* | 26 s | 2,0 s | 28 | 2 | "Điểm mạnh của mày sao lại là có laptop cá nhân?" |

\* đăng trong vài tuần gần nhất, view còn tăng - không coi là "thấp" chắc chắn.

### Điều số liệu cho thấy

1. **Nhịp cắt là sàn, không phải lý do viral.** Gần như mọi video cắt mỗi ~2 s (22-33 cắt/phút), kể cả video
   view thấp. Không đạt nhịp này thì thua; đạt rồi thì nội dung quyết định.
2. **Độ dài không quyết định.** Hit có cả 33 s lẫn 229 s; video thấp có cả 26 s lẫn 170 s.
3. **Câu đầu tiên = mâu thuẫn hoặc luật chơi** về tiền, giờ làm, sếp - nói ngay giây 0, có chữ trên màn hình.
   Vlog sự kiện không có tiền đề là mẫu thấp nhất.
4. **Nỗi đau văn phòng ai cũng có:** lương, xin về sớm, tăng ca, bao cơm, trốn việc. Đổi bối cảnh sang gia đình
   (lương - biếu bố) vẫn chạy vì cùng là chuyện tiền.
5. **Dàn nhân vật cố định = sitcom.** Cùng một nhóm nhân vật xuất hiện chéo ở cả hai kênh k1, k2; khán giả quay lại
   vì nhân vật.
6. **Mỗi 8-15 s có một nhịp mới**, đánh dấu bằng cận mặt người nghe + lọc hồng + SFX hài (boing, kêu vịt, mèo,
   quạ/dế cho im lặng ngượng). Kết bằng cú lật hoặc punchline, không outro, CTA nằm trong lời thoại.
7. **Video lồng nhãn hàng là video lớn nhất của cả hai kênh** (56,9M, 53,3M, 8M): sản phẩm giải quyết mâu thuẫn ở
   khoảng 35-45 % thời lượng, có ảnh chụp app chèn lên hình, kết vẫn là câu đùa. Lưu ý: video hợp tác có trả phí
   thường được chạy quảng cáo, nên view không chỉ do cách dựng.
8. **Âm thanh:** cả 16 mẫu có nhạc nền nhẹ dưới lời thoại (khác story-vlog - không nhạc). Phụ đề 2 dòng, in hoa,
   màu theo người nói, từ khoá vàng.

### Công thức gợi ý (dùng khi viết plan)

```
[0-2 s]   Câu mâu thuẫn / luật chơi + chữ trên màn hình (không chào, không logo)
[2-15 s]  Lý do / phản đòn đầu tiên → cận mặt phản ứng (zoom 1.25, lọc hồng) + 1 SFX
[mỗi 8-15 s] Leo thang: thêm người, thêm điều kiện, thêm bằng chứng (ảnh app/hoá đơn)
[35-45 %] (nếu có nhãn hàng) sản phẩm giải quyết mâu thuẫn, kể bằng thoại
[cuối]    Lật thế / punchline / callback → cắt ngay
```

Kiểm tra trước khi đăng: câu đầu có hiểu được nếu chỉ nghe 2 giây? Có ít nhất 1 nhịp mới mỗi 15 s? Kết có cú
lật? Phụ đề đúng người nói? (lint + check của skill kiểm tra phần kỹ thuật, còn mấy câu này do người/Claude trả lời.)

## 5 style đang hút view (10/2026)

Chọn kênh từ danh sách đề cử TikTok Awards Việt Nam 2026 và các kênh lớn, xếp theo **view trung vị** của ~30-50
video gần nhất (không tính video ghim), lấy 3 mẫu/kênh: 2 video cao nhất gần đây + 1 video trung vị.

| Style (nguồn) | Follow | Trung vị | Mẫu (view, dài, cắt/phút) |
|---|---|---|---|
| `review-xam` (k1) | 8,3M | ~1,2M | `comparison-review__kfc-my-vs-viet-nam` 6,9M (249 s, 24); `brand-skit__vo-dung-dien-thoai-moi` 6,6M (122 s, 10); `explainer__luat-xac-thuc-tai-khoan-mxh` 1,2M (104 s, 20) |
| `pet-dub` (k1) | 2,7M | ~830K | `trend-song__meo-nhuom-duoi-do` 12,5M (26 s); `dub__talk-show-buoi-toi` 5,4M (37 s); `dub__phong-van-meo` 923K (36 s) |
| `street-kindness` (k1) | 4,7M | ~784K | `kindness__gio-xach-banh-cam` 4,8M (278 s); `kindness-followup__gio-xach-ca-vien-chien` 3,8M (252 s); `challenge__goi-mon-lau-bang-chatgpt` 772K (181 s) |
| `trend-aesthetic` (k1) | 15,9M | ~1,1M | `trend__di-pho-den-trang` 13,4M (18 s, 2 cắt); `trend__ve-tranh-ngoai-troi` 4,8M (20 s); `trend__selfie-trong-xe` 673K (20 s, 0 cắt) |
| `mini-drama` (k1) | 1,2M | ~249K | `brand-drama__co-tich-10k-the-metro` 3,5M (101 s, 37); `drama__co-gai-den-tu-hu-vo` 3,5M (103 s, 28); `parody-mv__parody-mv-khong-thoai` 248K (174 s, 11) |

Đã xem 6 kênh khác nhưng không chọn (trung vị thấp hơn ~19K-622K, hoặc tắt tải video).

### Điểm chung của cả 8 kênh

1. **2 giây đầu nói rõ "video này về cái gì và vì sao phải xem"**: câu hỏi so sánh, mâu thuẫn, luật thử thách,
   tên series + đồ vật, hoặc một hình ảnh lạ. Không chào, không logo.
2. **Lời hứa được trả ở cuối** (kết luận, cú lật, phản ứng cảm động) - người xem ở lại để biết.
3. **Series / nhân vật lặp lại** thắng video đơn lẻ: office-sitcom (dàn nhân viên), street-kindness (giỏ xách),
   mini-drama (tập 1, 2), story-vlog (hành trình mở quán).
4. **Nhãn hàng nằm trong câu chuyện**, là lời giải của mâu thuẫn - không đọc quảng cáo. Nhiều video lớn nhất là
   video hợp tác (có thể được chạy quảng cáo).
5. **Trong cùng một kênh, video ít view thường thiếu tiền đề**: vlog sự kiện, parody nhạc không thoại, thử thách
   gượng, tin tức không có câu hỏi - dù nhịp cắt giống hệt.
6. **Nhịp cắt tuỳ style** (0-37 cắt/phút); không có con số chung - chỉ cần đúng chuẩn của style đó.

## story-vlog (k1) - để so sánh

Chủ quán ăn kể chuyện kinh doanh: sự kiện, bếp, nguồn hàng, mở rộng (8 mẫu, 162-592 s, 10-31 cắt/phút).
7/8 mẫu mở bằng teaser 5-17 s lấy câu đắt nhất từ giữa video; mẫu không có teaser view thấp nhất. Một người kể,
không nhạc nền, chữ vàng khổng lồ, xé giấy chuyển cảnh. Hợp với: sự kiện, chuyển văn phòng, vận hành quán,
hành trình.

## Giới hạn

- 39 mẫu là mẫu nhỏ; đây là giả thuyết có căn cứ, không phải định luật.
- View phụ thuộc thời điểm đăng, tuổi video, quảng cáo trả phí, thuật toán - không đo được từ video.
- Nhãn âm thanh tự động chỉ là gợi ý (ví dụ tiếng Việt đôi khi bị gắn nhãn sai).
