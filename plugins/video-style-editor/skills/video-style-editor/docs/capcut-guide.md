# Hoàn thiện trong CapCut (tuỳ chọn)

Skill dựng xong video bằng FFmpeg. Khi người dùng muốn chỉnh tay hoặc dùng thư viện của CapCut Pro (hiệu ứng,
SFX, template chữ), dùng bảng dưới để tìm đúng tên trong CapCut (web/PC, khảo sát 10/2026). Tài nguyên CapCut chỉ
dùng bên trong CapCut - skill không tải chúng về.

## Đưa bản dựng sang CapCut

- Video: dùng `output/<tên>.mp4`; muốn bản không phụ đề để làm chữ trong CapCut thì render plan với
  `"style": {"captions": false}` (xem edit-plan.md).
- Phụ đề: CapCut → **Captions → Upload caption file** nhận `.srt`, `.ass`, `.lrc`. File phụ đề của skill nằm ở
  `work/build/<tên>/captions.ass` - tải lên để giữ đúng mốc thời gian rồi đổi style chữ trong CapCut.

## SFX: tìm gì trong CapCut (Audio → Sound effects)

Thẻ tìm kiếm phổ biến CapCut gợi ý: **vine boom, boom, explosion, woosh, glitch**. Danh mục: Performance, Laugh,
Fight, Transition, Food, Ambience, Animals, Mechanical, Magic, Instrument, Horror, Traffic, BGM.

| Khoảnh khắc | Từ khoá CapCut | Tên tương đương trong skill (Mixkit) |
|---|---|---|
| Câu chốt gây sốc | vine boom, boom meme, dramatic boom | impact_2150, impact_1143 |
| "Khoan đã?!" | record scratch, scratch effect | scratch_704 |
| Cạn lời / im lặng ngượng | crow sound, cricket, awkward | crow_316, cricket_1780 |
| Ngã, hỏng việc | wah wah fail, trombone fail, buzzer fail | trombone_744, failpiano_473, failtone_2876 |
| Phản ứng ngố | boing cartoon, toy squeak, duck quack | boing_2894, squeak_1014 |
| Dỗi dễ thương | cat meow, meow cat cute | meow_91 |
| Cười | crowd laughing, laugh (danh mục Laugh) | laughtrack_424, giggle_2885 |
| Đúng / sai | correct answer, ping pong; wrong buzzer, error windows | correct_2870, wrong_946 |
| Tiền, lương | chaching money, cash sound | bonus_2060 |
| Tin nhắn, điện thoại | message notification, text message, phone ringing | msgpop_2354 |
| Đồng hồ, thử thách | clock tick, tick tock | ticktock_1045 |
| Chuyển cảnh | whoosh sound effect, riser whoosh, swish | whoosh_1489/1490/1492 |
| Đấm, tát | punch sound effect, slap sound effect, bonk on head | impact_2182 |
| Khác hay dùng | bruh sound effect, hehe boy, sus among us, oh my god, camera shutter, sparkle, magic reveal | - |

## Hiệu ứng hình (Effects → Video effects)

Thẻ phổ biến: **blur, Countdown, zoom lens, shake**. Mục Trending lúc khảo sát: Snapshot 3x, Rise In Ember,
Antique Volt, Black Flash 2, Vignette.

| Mục đích | CapCut | Trong skill |
|---|---|---|
| Rung khi hét/sốc | Shake, Camera Shake, Repeated Shake, RGB Shake | `fx: ["shake"]` |
| Zoom nhấn | Zoom Lens, Mini Zoom, Repeat Zoom, Exposure Zoom, Flip Zoom, Diamond Zoom | `zoom` 1.12-1.25 |
| Chớp | White Flash, Black Flash, Vibration Flash, Flash Bounce | `transition: "flash"` |
| Lọc hồng phản ứng (office-sitcom) | Filters → Flash: **Pink Flash**; Pink CCD, Dusky Pink, Magenta Fade | `tint: "pink"` |
| Đứng hình | Freeze Moment, Fault Freeze | (chưa có - kéo dài piece + zoom) |
| Glitch | Glitch, Multicolor Glitch, Pixel Glitch, Bad TV | - |
| Tia tốc độ | (không có tên tương đương rõ) | `fx: ["speedlines"]` |
| Chia màn hình | Split Screen, Dual Screens, Four Screens | - |
| Trái tim, lấp lánh | Floating Hearts, Pink Hearts, Sparkle, Gold Sparkles | - |
| Đếm ngược | Countdown, Countdown 2 | big text "3-2-1" |

## Chuyển cảnh (Transitions)

Trending: Bubble Sparks, **Tear Away** (≈ xé giấy của skill: `transition: "paper"`), Heavy Roll, Firespark Cube,
Flying Photos, Colors Off. Hay dùng cho vlog hài: Whiplash, Fast Zoom, Velocity Zoom, Stutter Cut, Datamosh,
Shake, Flash, White Flash 2, Camera Movement, Old Footage.

## Chữ

Text → Text templates / Text effects là ảnh mẫu (không có tên) - chọn theo mắt. Phụ đề kiểu office-sitcom: chữ in hoa đậm,
viền đen dày, 2 dòng, màu theo người nói. Kiểu story-vlog: 3 chữ, chữ đang nói tô vàng.

Font phải có Việt hoá: font của caption template hay thiếu chữ HOA có dấu → đổi sang **Oswald-Bold** (cuộn danh sách
font để tìm). Phụ đề đặt ~75 % chiều cao, không vào 20 % đáy / 10 % đỉnh / cột nút bên phải (chi tiết:
`editing-craft.md` mục 4). Dán chữ (Ctrl+C/V) bị lệch vị trí mỗi lần dán → đặt lại Biến đổi X/Y.

## Cài đặt và thói quen (từ khoá CapCut PC - xem `editing-craft.md` mục 10)

- Dự án: 1080×1920, **30 fps**, color space **SDR Rec.709**; bật Free layer; Auto snapping **luôn bật**
  (hở 1 khung = chớp đen); preview quality = Performance priority.
- Chuyển cảnh chỉ đặt được giữa 2 clip **liền nhau trên track chính**; vào/ra đầu cuối → chèn clip Transparent.
- Keyframe: luôn đứng đúng trên key (◁ ◇ ▷) rồi mới sửa, nếu không sẽ sinh key mới gây giật.
- Màu: Adjustment → Basic (LUT, Temp/Tint, Highlight/Shadow…) | HSL; xem scope ở menu ☰ của Player → Color
  oscilloscope. Một lớp look phủ cả video, cường độ 70–80 %, không chồng 2 filter.
- Âm thanh: Audio → Basic có Volume, Fade in/out, ☐ Noise reduction; giọng chạm vàng không chạm đỏ.
- Xuất: Ctrl+M; Resolution = nguồn, Bit rate Recommended (1080p ≈ 8–12 Mbps), H.264, MP4, 30 fps; chọn Cover.

## CapCut Smart Insights

CapCut Pro có **Smart Insights** (tóm tắt trend theo hashtag, lên kế hoạch nội dung, chấm video). Có thể tốn
credit - hỏi người dùng trước khi dùng.
