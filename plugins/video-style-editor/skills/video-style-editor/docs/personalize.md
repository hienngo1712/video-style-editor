# Dạy skill theo phong cách của bạn (my-style)

Skill này là **bộ khung chung**: ai cũng dùng được ngay với các style có sẵn (`profiles/`). Phần làm nó thành *của
bạn* nằm trong thư mục **my-style** — ghi lại sở thích, góp ý và thói quen dựng của bạn để mỗi video sau Claude dựng
đúng ý hơn video trước. Mỗi ngày bạn dùng là một lần "huấn luyện".

## 1. Ba lớp, từ chung đến riêng

| Lớp | Nằm ở | Ai sửa | Dùng để |
|---|---|---|---|
| **Mặc định của skill** | `scripts/`, `docs/` trong plugin | người phát triển skill | quy tắc chung: vùng an toàn TikTok, lọc ồn, cân màu, phụ đề sau tiếng nói 0,2 s… |
| **Style (profile)** | `profiles/<style>.yaml` trong plugin, hoặc tự tạo từ video mẫu | bạn / Claude | thể loại video: vlog kể chuyện, sitcom văn phòng, review… (cấu trúc, nhịp, kiểu chữ, SFX) |
| **my-style** | `<VSE_HOME>/my-style/` - thư mục dữ liệu của bạn | Claude ghi, **bạn duyệt** | khẩu vị riêng: thông số mặc định, SFX thích/ghét, chính tả, luật riêng, nhật ký góp ý |

Khi dựng: mặc định của skill < `my-style/preferences.yaml` < khối `style` của từng plan. my-style nằm **ngoài** plugin
nên cập nhật plugin không làm mất.

## 2. Các file trong my-style

- **`preferences.yaml`** - thông số mặc định cho mọi video (`style:` cỡ chữ, độ trễ phụ đề, look màu, độ to,
  chuyển động…), `sfx:` (thích / cấm / lặp tối đa), `pacing:` (cắt tiếng đệm, khoảng lặng), `words:` (chính tả phụ đề
  bạn luôn muốn sửa, ví dụ tên riêng ASR hay nghe sai), `rules:` (luật bằng lời, Claude phải theo).
- **`journal.md`** - nhật ký góp ý, dễ đọc. **`feedback.jsonl`** - cùng nội dung, để thống kê.

- **`brief.md`** - chân dung người dùng bằng lời: kênh, người xem, mục tiêu, giọng điệu, thích / ghét, video mẫu.

Tạo lần đầu: `vse.py style init` (chép từ `templates/my-style/`). Ngay sau đó Claude **phỏng vấn** người dùng theo
`docs/onboarding.md` (7 vòng câu hỏi ngắn về mục tiêu, nhịp, chữ, âm thanh, hình, thương hiệu, video mẫu) và dựng
thử 15 giây đầu để chỉnh trước - nhờ vậy video đầu tiên đã gần đúng ý. Sửa nhanh: `vse.py style set KEY VALUE`,
`style rule "..."`, `style word "asr" "Đúng"`.

## 3. Vòng học mỗi ngày

1. **Trước khi dựng** - Claude chạy `vse.py style show`: đọc thông số, luật, 12 góp ý gần nhất và chủ đề hay bị góp ý
   nhất → áp dụng ngay khi viết plan.
2. **Sau khi dựng** - Claude hỏi bạn (hoặc người duyệt / Gemini) góp ý cụ thể: *chỗ nào, giây thứ mấy, muốn thế nào*.
3. **Ghi lại** - mỗi góp ý: `vse.py style note "chữ hiện sớm quá" --at 0:12 --tag captions --by editor --fix "lag 0.2"`.
   Chủ đề: captions, text, audio, sfx, music, cut, pacing, motion, color, story, teaser, other.
4. **Học từ chỗ bạn tự sửa** - nếu bạn (hoặc Claude theo lời bạn) sửa plan thành bản mới:
   `vse.py style learn PROJECT plans/A.json plans/B.json` → liệt kê thay đổi (cắt sát hơn, SFX nhỏ hơn bao nhiêu dB,
   chữ nào bị sửa chính tả, zoom/chuyển cảnh thêm bớt) và **đề xuất** dòng cần thêm vào `preferences.yaml`.
5. **Biến góp ý thành quy tắc** - khi một góp ý lặp lại 2 lần, hoặc bạn nói "lần sau cứ thế", Claude đề xuất sửa
   `preferences.yaml` (thông số) hoặc thêm một dòng `rules:` - **bạn đồng ý thì mới ghi**. Từ video sau, việc đó tự đúng.
6. **Xem mình hay bị góp ý gì** - `vse.py style stats`: chủ đề nhiều góp ý nhất là chỗ nên cải thiện trước.

Góp ý bằng video (quay màn hình nói): Claude chuyển lời thành chữ bằng model nhận giọng của skill, xem khung hình,
rồi ghi từng ý bằng `style note`.

## 4. Tuỳ chỉnh sâu hơn

- **Style riêng từ video mẫu bạn thích**: bỏ 5-8 video vào `<VSE_HOME>/references/<style>/videos/` → `vse.py reference`,
  `vse.py library` → Claude viết `profiles/<style>.yaml` (xem `docs/styles.md`). Đặt `default_profile` trong
  `preferences.yaml` để mặc định dùng style đó.
- **Màu riêng**: đặt file `.cube` của bạn vào `style.look` (ví dụ `look: luts/am-ap.cube`, đường dẫn tính từ thư mục dự án).
- **Bộ SFX riêng**: thêm file vào `<VSE_HOME>/sfx/` tên `sfx_<tên>.mp3`, ghi tên vào `sfx.favourite`.
- **Chia sẻ phong cách cho cả team**: chép thư mục `my-style/` (và profile, LUT) cho đồng nghiệp - họ dựng ra cùng
  một kiểu. Muốn gộp góp ý của nhiều người, mỗi người ghi `--by <tên>`.

## 5. Nguyên tắc

- Claude **không tự đổi** `preferences.yaml` khi chưa hỏi: chỉ đề xuất, bạn duyệt.
- Mỗi luật một dòng, cụ thể, kiểm chứng được ("SFX không quá -10 dB", không phải "SFX vừa phải").
- Góp ý mâu thuẫn nhau → luật mới nhất thắng, Claude hỏi lại khi không chắc.
- Không ghi thông tin cá nhân của người trong video vào my-style (chỉ ghi khẩu vị dựng).
