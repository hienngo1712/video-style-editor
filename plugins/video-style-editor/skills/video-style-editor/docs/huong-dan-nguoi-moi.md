# Hướng dẫn cho người mới: từ cài Claude đến video đầu tiên

Tài liệu này dành cho người **chưa dùng AI bao giờ**. Bạn chỉ cần biết cài phần mềm trên máy tính và đã có tài khoản
**Claude Pro** (hoặc gói cao hơn). Làm lần lượt từ bước 1 đến bước 9, khoảng **30-45 phút** cho lần đầu (phần lớn là
chờ tải). Từ video thứ hai trở đi chỉ cần bước 7-9.

> Giao diện Claude chủ yếu bằng tiếng Anh. Trong tài liệu, tên nút được giữ nguyên tiếng Anh và **in đậm**, kèm giải
> thích tiếng Việt. Giao diện có thể thay đổi một chút theo phiên bản - nếu không thấy đúng tên nút, tìm nút gần giống.

---

## Hiểu nhanh 5 khái niệm

| Từ | Nghĩa |
|---|---|
| **Claude** | Trợ lý AI của Anthropic. Bạn nói chuyện với nó bằng tiếng Việt bình thường, như nhắn tin. |
| **Cowork** | Chế độ làm việc của ứng dụng Claude trên máy tính: Claude được phép mở thư mục bạn chọn, chạy công cụ và lưu file vào đó. Skill dựng video cần chế độ này. |
| **Plugin / skill** | Gói "kỹ năng" cài thêm cho Claude. Plugin **video-style-editor** dạy Claude cách dựng video dọc 9:16 từ bản thô. |
| **Prompt** | Câu bạn gõ cho Claude. Tài liệu này có sẵn các prompt mẫu - chỉ việc sao chép và dán. |
| **Bản thô** | Các clip quay bằng điện thoại, chưa cắt ghép. Đầu ra là **video thành phẩm** (MP4) có phụ đề, hiệu ứng, âm thanh. |

**Video của bạn ở đâu?** Clip gốc nằm trên máy bạn và được xử lý ngay trên máy bạn (trong một máy ảo nhỏ của Claude),
không phải tải lên. Claude chỉ đọc lời thoại đã được chép ra chữ và vài ảnh chụp nhỏ từ video để quyết định cắt ghép.

---

## Bước 1 - Chuẩn bị

- Máy tính **Windows** hoặc **macOS**, mạng ổn định.
- Ổ đĩa còn trống ít nhất **3 GB** (công cụ ~300 MB + chỗ cho video tạm), cộng thêm dung lượng bản thô.
- Tài khoản Claude **Pro** trở lên. Kiểm tra: vào [claude.ai](https://claude.ai) → góc dưới trái bấm vào tên bạn →
  **Settings** → **Billing** phải ghi Pro / Max / Team. (Cowork chỉ có ở gói trả phí.)

## Bước 2 - Cài ứng dụng Claude trên máy tính

1. Mở trình duyệt, vào **[claude.com/download](https://claude.com/download)**, tải bản cho Windows hoặc macOS.
2. Chạy file vừa tải để cài (bấm Next / kéo vào Applications như mọi phần mềm khác).
3. Mở ứng dụng **Claude**, bấm **Log in** và đăng nhập đúng tài khoản Pro.

> Phải dùng **ứng dụng trên máy tính**, không dùng bản web hay điện thoại: chỉ ứng dụng máy tính mới mở được thư mục
> video trên máy bạn.

## Bước 3 - Bật quyền chạy công cụ (làm 1 lần)

1. Trong ứng dụng Claude: bấm vào tên bạn (góc dưới trái) → **Settings** → **Capabilities**.
2. Bật **Code execution and file creation** (có bản ghi là **Create and edit files**).

Không bật thì Claude không chạy được công cụ dựng video.

## Bước 4 - Cài plugin video-style-editor

Chọn **một** trong hai cách. Cách A tốt hơn vì plugin tự cập nhật khi có bản mới.

**Cách A - cài từ GitHub (khuyên dùng)**

1. Trong ứng dụng Claude, thanh bên trái bấm **Customize** → **Plugins**.
2. Bấm **Add marketplace**, dán: `hienngo1712/video-style-editor` (hoặc https://github.com/hienngo1712/video-style-editor),
   bấm thêm.
3. Trong danh sách plugin hiện ra, tìm **video-style-editor** → bấm **Install**.
4. Bấm vào marketplace vừa thêm, bật **Sync automatically** để luôn nhận bản mới.

**Cách B - cài từ file zip (khi được gửi file `video-style-editor-skill.zip`)**

1. **Customize** → **Skills** → bấm dấu **+** → **Create skill** → **Upload a skill**.
2. Chọn file `video-style-editor-skill.zip` (không cần giải nén).
3. Skill hiện trong danh sách - kiểm tra công tắc đang **bật**.

Cách B không tự cập nhật: có bản mới thì xoá skill cũ và tải file zip mới lên.

## Bước 5 - Tạo thư mục làm việc và cho Claude truy cập

1. Trên máy, tạo một thư mục riêng cho việc dựng video, ví dụ `Documents\Video-AI` (Windows) hoặc
   `Documents/Video-AI` (Mac). Nên dùng thư mục riêng, đừng chọn cả ổ đĩa hay cả thư mục Downloads lộn xộn.
2. Trong ứng dụng Claude, bắt đầu cuộc trò chuyện mới. Ở ô nhập tin nhắn, chọn chế độ **Cowork** (nếu thấy hai
   lựa chọn Chat / Cowork; bản mới không có lựa chọn này thì bỏ qua).
3. Bấm **Work in a project or folder** (hoặc biểu tượng thư mục / **Add folder**) ở ô nhập → chọn thư mục `Video-AI`.
4. Nếu Claude hỏi xin quyền truy cập thư mục, bấm **Allow** (Cho phép).

Claude sẽ tự tạo bên trong thư mục này một thư mục con **`vse-workspace`** chứa mọi thứ của bạn:

```
Video-AI/
└── vse-workspace/
    ├── my-style/        "khẩu vị" dựng của bạn - Claude học dần qua từng góp ý
    ├── projects/        mỗi video một thư mục: raw/ (bản thô) · output/ (thành phẩm)
    ├── references/      video mẫu bạn muốn học theo (không bắt buộc)
    └── models/ fonts/ sfx/ overlays/   công cụ tải về tự động, đừng sửa
```

## Bước 6 - Prompt cài đặt (làm 1 lần, ~10-20 phút)

Trong cuộc trò chuyện Cowork vừa mở (đã chọn thư mục), dán prompt sau và gửi:

```text
Dùng skill video-style-editor. Đây là lần đầu tôi dùng, hãy cài đặt giúp tôi:
- Lấy thư mục tôi vừa chọn làm nơi làm việc, tạo vse-workspace bên trong.
- Chạy kiểm tra và cài mọi thứ còn thiếu (doctor --fix), tạo my-style cho tôi (style init).
- Tên tôi là <tên bạn>, tôi làm video cho <kênh/thương hiệu>, đăng chủ yếu trên <TikTok/Reels/YouTube Shorts>.
Báo tôi bằng tiếng Việt, ngắn gọn: đã cài xong những gì, còn thiếu gì và tôi cần làm gì.
```

Trong lúc chạy:

- Claude có thể hỏi xin phép (tải file, chạy lệnh, mở trang web). Đọc rồi bấm **Allow** nếu đúng việc bạn nhờ.
- Thấy chữ **CONTINUE** hoặc "chưa xong, chạy tiếp" là bình thường: công cụ chạy từng đợt, Claude tự chạy lại.
  Nếu Claude dừng giữa chừng, nhắn **"tiếp tục"**.
- Giữ ứng dụng Claude mở và máy không ngủ (sleep) cho tới khi xong.
- Nếu Claude báo không tải được hiệu ứng âm thanh (SFX), nhắn: *"Tải SFX giúp tôi bằng trình duyệt"* - hoặc bỏ qua,
  video vẫn dựng được, chỉ thiếu tiếng hiệu ứng.

## Bước 7 - Phỏng vấn phong cách (làm 1 lần, ~10 phút) - bước quan trọng nhất

Claude sẽ hỏi bạn khoảng 7 vòng câu hỏi ngắn (bấm chọn hoặc gõ tự do) về: video để làm gì, độ dài và nhịp cắt, kiểu
phụ đề, nhạc và hiệu ứng âm thanh, màu và chuyển động, logo và điều cấm, video mẫu bạn thích. Trả lời càng kỹ, video
đầu tiên càng đúng ý. Dán prompt:

```text
Phỏng vấn tôi thật kỹ về phong cách dựng video tôi muốn (theo docs/onboarding.md của skill), mỗi lần hỏi ít câu thôi.
Hỏi xong thì tóm tắt lại cho tôi duyệt, rồi ghi vào my-style.
```

Mẹo trả lời:

- **Có video mẫu là tốt nhất**: dán link 1-3 video (của bạn hoặc kênh khác) và nói rõ thích điểm gì - nhịp, kiểu chữ,
  tiếng hiệu ứng, cách mở đầu…
- Câu cuối Claude sẽ hỏi *"Điều gì làm bạn khó chịu nhất khi người khác dựng video cho bạn?"* - hãy trả lời thật lòng
  và cụ thể ("chữ che mặt", "nhạc to hơn giọng", "cắt mất hơi thở, nghe giật"…).
- Tên riêng, tên thương hiệu hay bị nghe sai thì liệt kê luôn (ví dụ: *"luôn viết Phở Thìn, không viết phở thìn"*).

Không có thời gian? Nhắn: *"Phỏng vấn nhanh 4 vòng đầu thôi, còn lại dùng mặc định"*.

## Bước 8 - Video đầu tiên

**8.1. Đưa bản thô vào đúng chỗ.** Mở thư mục `Video-AI/vse-workspace/projects/` bằng File Explorer / Finder, tạo
thư mục cho video, ví dụ `video-1` (nên viết không dấu, không khoảng trắng), bên trong tạo thư mục `raw` và chép
**tất cả clip** của video đó vào:

```
vse-workspace/projects/video-1/raw/IMG_0001.MOV, IMG_0002.MOV, ...
```

Ghi âm lời dẫn / kịch bản (file âm thanh, file chữ) cũng bỏ chung vào `raw` - Claude sẽ đọc.

**8.2. Dán prompt dựng video:**

```text
Dựng video-1 (bản thô trong vse-workspace/projects/video-1/raw) theo my-style của tôi.
Nội dung: <1-3 câu: video kể gì, điểm hay nhất là gì, muốn người xem cảm thấy/làm gì>.
Độ dài mong muốn: <ví dụ 45-60 giây>.
Trước khi dựng cả video: cho tôi duyệt kịch bản (câu mở đầu, teaser, thứ tự, đoạn bỏ) và một bản thử 15 giây đầu.
```

Claude sẽ lần lượt: chép lời → xem ảnh từng clip → đề xuất kịch bản để bạn duyệt → dựng thử 15 giây → bạn góp ý →
dựng cả video → tự kiểm tra (phụ đề, độ to, độ sáng, vùng an toàn TikTok) → báo cáo.

Thời gian tham khảo: video 1 phút từ ~5 phút bản thô mất khoảng **20-40 phút**, lâu nhất là lần đầu. Không cần ngồi
canh, nhưng giữ ứng dụng mở và máy không ngủ.

**8.3. Lấy thành phẩm** trong `vse-workspace/projects/video-1/output/`:

- File `.mp4` 1080×1920 - bản để đăng.
- Thư mục `review/` - bản nhẹ 540p để xem nhanh / gửi người khác duyệt.

Phụ đề do máy nghe chép - **luôn xem lại chính tả trước khi đăng**.

## Bước 9 - Góp ý để Claude học (mỗi video, 2 phút)

Xem video, ghi lại chỗ chưa ưng **kèm giây thứ mấy** và **muốn thế nào**, rồi dán:

```text
Góp ý video-1:
- 0:05 chữ che mặt, đẩy chữ xuống thấp hơn
- 0:20-0:24 đoạn này thừa, cắt bỏ
- tiếng "bụp" ở 0:31 to quá, nhỏ lại
- nhìn chung nhịp hơi chậm, cắt khoảng lặng gắt hơn
Sửa và dựng lại. Ghi các góp ý này vào my-style; cái nào nên thành quy tắc lâu dài thì đề xuất để tôi duyệt.
```

Góp ý tốt = **chỗ nào + vấn đề + muốn thế nào**. "Chưa hay" hay "làm lại đi" thì Claude không học được gì.
Mỗi góp ý được ghi vào `my-style/journal.md`; góp ý lặp lại sẽ thành quy tắc → video sau tự đúng, không phải nhắc lại.

---

## Dùng hằng ngày (từ video thứ hai)

1. Tạo `vse-workspace/projects/<tên-video>/raw/`, chép bản thô vào.
2. Mở **cuộc trò chuyện Cowork mới** (mỗi video một cuộc), chọn đúng thư mục `Video-AI`.
3. Dán prompt dựng (bước 8.2), xem, góp ý (bước 9).

### Bảng prompt hay dùng

| Muốn | Dán / nhắn |
|---|---|
| Dựng video mới | `Dựng <tên-video> theo my-style. Nội dung: ... Độ dài: ...` |
| Dựng nhanh, không cần duyệt giữa chừng | `Dựng <tên-video> theo my-style, không cần hỏi tôi, xong thì báo.` |
| Đổi kiểu cho một video | `Dựng <tên-video> theo style office-sitcom` (các style: story-vlog, office-sitcom, review-xam, street-kindness, mini-drama, pet-dub, trend-aesthetic) |
| Làm 2 phiên bản để so sánh | `Dựng <tên-video> 2 bản: một bản 30 giây nhịp nhanh, một bản 60 giây.` |
| Xem Claude đã học gì về bạn | `Cho tôi xem my-style hiện tại của tôi, tóm tắt bằng tiếng Việt.` |
| Đặt quy tắc lâu dài | `Ghi quy tắc vào my-style: không bao giờ dùng tiếng cười giả.` |
| Sửa chính tả cố định | `Ghi vào my-style: luôn viết "phong bvb" thành "Phong BVB".` |
| Học style mới từ video mẫu | `Học phong cách từ các video trong vse-workspace/references/<tên-style>/ và tạo style mới tên <tên-style>.` |
| Làm tiếp trong CapCut | `Xuất thêm file phụ đề để tôi chỉnh tiếp trong CapCut.` |
| Claude dừng giữa chừng | `tiếp tục` |

## Dùng tiết kiệm lượt (gói Pro)

Dựng video là việc nặng, tốn lượt sử dụng hơn nhiều so với hỏi đáp. Gói Pro có giới hạn theo khung giờ; xem mức đã
dùng ở **Settings → Usage**.

- Mỗi video một cuộc trò chuyện; đừng dựng nhiều video trong cùng một cuộc.
- Gom góp ý thành **một lần** (cả danh sách) thay vì sửa từng chút một rồi dựng lại nhiều lần.
- Duyệt kịch bản + bản thử 15 giây trước khi dựng cả video - rẻ hơn nhiều so với sửa cả video.
- Hết lượt giữa chừng: chờ tới giờ mở lại rồi nhắn `tiếp tục` - công việc đã làm được lưu, không mất.

## Gặp sự cố

| Hiện tượng | Cách xử lý |
|---|---|
| Không thấy **Cowork** / **Customize** | Cập nhật ứng dụng Claude bản mới nhất, kiểm tra gói Pro (bước 1). |
| Claude nói không biết skill video-style-editor | Kiểm tra plugin/skill đã cài và **bật** (bước 4), rồi mở cuộc trò chuyện **mới**. |
| Claude báo không truy cập được máy / thư mục | Giữ ứng dụng Claude mở, máy không ngủ; chọn lại thư mục (bước 5) trong cuộc trò chuyện mới. Nếu báo không khởi động được máy ảo: tắt hẳn ứng dụng Claude, mở lại. |
| Thấy CONTINUE, "exit 3", hoặc Claude dừng | Bình thường - nhắn `tiếp tục`. |
| Không tải được SFX / model | Nhắn `Tải giúp tôi bằng trình duyệt`, hoặc thử lại lúc khác (mạng công ty đôi khi chặn). |
| Phụ đề sai chính tả | Nhắn chỗ sai + chữ đúng, và `ghi vào my-style` để lần sau tự sửa. |
| Chữ hiện trước khi nói, chữ che mặt, tiếng quá to/nhỏ | Góp ý theo mẫu bước 9 kèm giây thứ mấy. |
| Video ra không đúng ý ngay từ đầu | Nhắn `Phỏng vấn lại tôi về phong cách` (bước 7) và gửi kèm video mẫu. |
| Muốn xoá video tạm cho nhẹ máy | Xoá thư mục `projects/<tên-video>/work/` (giữ `output/`). Claude luôn hỏi trước khi xoá bất cứ thứ gì. |

## Chia sẻ phong cách cho đồng nghiệp

Thư mục `vse-workspace/my-style/` là toàn bộ "khẩu vị" của bạn. Chép nó sang `vse-workspace/my-style/` của người khác
là họ dựng được giống bạn; họ góp ý tiếp thì nó dần thành của họ. Không gửi kèm video của người khác nếu chưa được
phép.

---

Tài liệu tham khảo chính thức của Claude (tiếng Anh): [Bắt đầu với Cowork](https://support.claude.com/en/articles/13345190-get-started-with-cowork) ·
[Cài plugin](https://claude.com/docs/cowork/guide/plugins) · [Dùng skill](https://support.claude.com/en/articles/12512180-use-skills-in-claude).
Tìm hiểu sâu hơn về skill này: `docs/personalize.md` (cách Claude học khẩu vị của bạn), `docs/workflow.md` (quy trình
chi tiết).
