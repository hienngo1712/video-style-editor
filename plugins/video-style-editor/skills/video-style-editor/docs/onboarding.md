# Phỏng vấn lần đầu (onboarding) - để video đầu tiên đã đúng ý

Chạy khi người dùng chưa có my-style hoặc `vse.py style show` báo **NOT ONBOARDED**, *trước* khi viết plan cho video
đầu tiên (phân tích bản thô có thể chạy song song). Mục tiêu: hiểu đủ sâu khẩu vị dựng của người dùng để không phải
đoán. Kết quả ghi vào `my-style/preferences.yaml` (thông số) và `my-style/brief.md` (chân dung bằng lời).

## Cách hỏi

- Hỏi theo **vòng**, mỗi vòng tối đa 4 câu (công cụ hỏi trắc nghiệm nếu có, luôn có lựa chọn "khác" để trả lời tự do).
  Không dồn cả 30 câu một lúc. Bỏ câu đã biết câu trả lời (từ lời người dùng, video mẫu họ gửi, hoặc bản thô).
- Ưu tiên: vòng 1-4 luôn hỏi; vòng 5-7 hỏi khi người dùng còn kiên nhẫn hoặc trả lời "tôi kỹ tính". Người dùng muốn
  nhanh → dùng mặc định của style gần nhất và ghi rõ "chưa hỏi" trong brief.
- Mỗi lựa chọn nêu ngắn hệ quả ("phụ đề hiện từng chữ - hợp video nói nhanh"). Đưa ví dụ cụ thể, không dùng thuật ngữ.
- **Câu hỏi mở quan trọng nhất** (luôn hỏi ở cuối): *"Điều gì làm bạn khó chịu nhất khi người khác dựng video cho bạn?"*
  và *"Có video nào (của bạn hoặc người khác) mà bạn muốn video của mình giống y như thế không?"*
- Sau khi hỏi: đọc lại tóm tắt 5-8 dòng, người dùng xác nhận → ghi file → `vse.py style set onboarded <ngày>`.

## Bộ câu hỏi và nơi ghi câu trả lời

### Vòng 1 - Video để làm gì
| Câu hỏi | Lựa chọn gợi ý | Ghi vào |
|---|---|---|
| Đăng ở đâu là chính? | TikTok · Reels/Facebook · YouTube Shorts · YouTube dài · nhiều nơi | brief; nhạc bản quyền (FB/YouTube có kiếm tiền → không dùng nhạc CapCut/TikTok) |
| Loại nội dung? | vlog kể chuyện · review/giới thiệu sản phẩm · hướng dẫn · bán hàng · hài/tình huống diễn · phỏng vấn/podcast · mood/không lời | `default_profile` (story-vlog / review-xam / office-sitcom / trend-aesthetic …) |
| Mục tiêu số 1? | nhiều view/viral · ra đơn hàng · xây thương hiệu cá nhân · kể lại kỷ niệm | brief; hook mạnh hơn khi viral, CTA khi bán hàng |
| Người xem là ai? | tuổi, nghề, vì sao họ xem | brief (giọng văn phụ đề, mức "meme") |

### Vòng 2 - Nhịp, độ dài, mở và kết
| Câu hỏi | Lựa chọn | Ghi vào |
|---|---|---|
| Độ dài thường muốn? | < 30 s · 30-60 s · 60-90 s · 1,5-3 phút · dài hơn | `pacing.target_length_s` |
| Nhịp cắt? | rất nhanh, gần như không có khoảng lặng · vừa · thong thả, giữ cảm xúc | `pacing.tighten_gap` (0,25 / 0,45 / 0,8), `cut_fillers` |
| Mở đầu (3 giây đầu)? | teaser câu hay nhất · câu hỏi gây tò mò · khoe kết quả trước · vào thẳng chuyện · tiêu đề chữ to | `rules`, profile.structure |
| Kết thúc? | câu chốt/twist · kêu gọi follow/mua · hẹn tập sau · không gì cả | `rules` ("Không thêm thẻ tập sau…") |

### Vòng 3 - Chữ trên màn hình
| Câu hỏi | Lựa chọn | Ghi vào |
|---|---|---|
| Kiểu phụ đề? | 3 chữ tô vàng chữ đang nói (karaoke) · cả câu một lúc · chỉ chữ khoá · không phụ đề | `style.caption_mode` (karaoke / static), `style.captions: false` |
| Chữ hiện thế nào? | hiện dần theo lời (sau tiếng nói ~0,2 s) · cả cụm cùng lúc | `style.caption_reveal`, `style.caption_lag` |
| Cỡ & kiểu chữ? | to đậm IN HOA · vừa, chữ thường · nhỏ gọn | `style.caption_size` (88 / 76 / 64), `rules` (in hoa/thường) |
| Chữ to nhấn mạnh (số tiền, câu chốt)? | nhiều · vừa, chỉ chỗ quan trọng · không dùng | `rules` ("big text ≤ 1 lần/10 s"…) |
| Màu nhấn / màu thương hiệu? | vàng · trắng · màu riêng (mã màu) | `style.caption_highlight` (ASS BGR, ví dụ `&H0000D4FF&` = vàng #FFD400) |
| Tên riêng, thương hiệu hay bị nghe sai? | liệt kê | `words` ("phong bvb": "Phong BVB") |

### Vòng 4 - Âm thanh
| Câu hỏi | Lựa chọn | Ghi vào |
|---|---|---|
| Nhạc nền? | không · nhẹ dưới giọng nói · nhạc trend nổi bật | plan.music, `rules` |
| Sound effect? | nhiều kiểu meme · vừa, ở chỗ chuyển và chữ to · rất ít · không | `sfx.default_gain`, `sfx.max_repeat`, `rules` |
| Tiếng nào thích / ghét? | vine boom, whoosh, pop, ding, tiếng cười, tiếng tiền… | `sfx.favourite`, `sfx.banned` |
| Giọng nói? | lọc sạch tạp âm · giữ tự nhiên (tiếng không gian) | `style.denoise` (light / false) |

### Vòng 5 - Hình ảnh
| Câu hỏi | Lựa chọn | Ghi vào |
|---|---|---|
| Màu sắc? | tự nhiên sạch · ấm · lạnh · film cũ · LUT riêng (gửi file .cube) | `style.look` |
| Chuyển động khung hình? | zoom mềm thường xuyên · chỉ zoom ở câu chốt · gần như tĩnh · zoom giật mạnh kiểu meme | `style.motion` (auto/off), `rules` (punch mạnh hơn: `move_amt`) |
| Chuyển cảnh? | cắt thẳng là chính · vài cái ở chỗ đổi ý · nhiều hiệu ứng | `rules` |
| Mặt người? | giữ thật · làm mịn nhẹ · che mặt người lạ | `rules` |

### Vòng 6 - Thương hiệu & điều cấm
| Câu hỏi | Ghi vào |
|---|---|
| Logo, tên kênh, slogan, intro/outro cố định? (gửi file) | brief, plan.title / image |
| Từ ngữ cần che hoặc tránh (chửi thề, tên đối thủ…)? | `rules` |
| Điều tuyệt đối không được làm? | `rules` (một dòng một điều) |

### Vòng 7 - Mẫu và cách làm việc
| Câu hỏi | Ghi vào |
|---|---|
| 1-3 video/kênh bạn muốn giống (link hoặc file)? | `references/` → `vse.py reference` → profile riêng; brief |
| Video của chính bạn bạn thích nhất / không thích nhất, vì sao? | brief, `rules` |
| Bạn muốn duyệt ở bước nào? (kịch bản + teaser trước khi dựng · chỉ xem bản cuối) | brief, `rules` |
| Ai duyệt? (tự duyệt · gửi editor · nhờ Gemini nghe) · có hoàn thiện thêm trong CapCut không? | brief |

## Ghi kết quả

```
V style init                                    # nếu chưa có
V style set default_profile story-vlog
V style set style.caption_size 88
V style set style.look warm
V style set sfx.banned '["laughtrack_424"]'
V style set pacing.target_length_s '[30, 60]'
V style word "phong bvb" "Phong BVB"
V style rule "Mở đầu bằng câu gây tò mò, không chào hỏi."
V style brief                                   # mở đường dẫn brief.md để Claude viết chân dung bằng lời
V style set onboarded 2026-10-28
```

`brief.md` - 10-20 dòng: kênh, người xem, mục tiêu, giọng điệu, nhịp, những gì người dùng thích / ghét (dùng lời của
họ), video mẫu, cách duyệt. Claude đọc lại brief ở mỗi job (`style show` in ra).

## Hiệu chỉnh nhanh trước video đầu tiên (khuyên dùng)

Khi đã có bản thô: dựng **15 giây đầu** (teaser + vài câu) theo my-style vừa ghi, gửi người dùng xem, hỏi 3 câu:
chữ (cỡ, vị trí, lúc hiện) · nhịp cắt · âm thanh (nhạc, SFX, độ to). Sửa my-style theo câu trả lời rồi mới dựng cả
video - rẻ hơn nhiều so với sửa cả video sau.
