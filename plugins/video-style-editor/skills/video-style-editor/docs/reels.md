# Bố cục reels thiết kế sẵn (6 kiểu)

6 kiểu dựng lấy từ bộ **claude-editing-skills** của Artem Novitckii (MIT, xem `reels/NOTICE.md`), đã chuyển sang
tiếng Việt và chạy hoàn toàn trên máy: một clip nói chuyện → một reel 9:16 có đồ hoạ chuyển động, chữ xuất hiện
đúng lúc người nói nhắc tới. Khác với quy trình dựng cả video (`docs/workflow.md`), mỗi bố cục lấy **một đoạn
3-8 giây** nói **một ý**, rồi dựng thành một reel ngắn.

| Bố cục | Làm ra gì | Cần đưa thêm |
|---|---|---|
| `trial-reels` | Cùng một clip thành **3 bản trông khác hẳn nhau** để đăng thử, giữ bản giữ chân người xem tốt nhất: (1) tiêu đề to + phụ đề karaoke, (2) khung bài đăng với tiêu đề + zoom vào từ khoá, (3) con số kiểu chữ pixel trong khung | ảnh đại diện (cho bản 2) |
| `behind-the-person` | Tách người khỏi nền, đặt **đồ hoạ phía sau người**: lưới bài đăng, biểu đồ cột hoặc ảnh chụp màn hình; chữ to hiện trên ngực; thẻ hồ sơ đếm số tăng dần | ảnh bài đăng / số liệu thật |
| `explainer` | Người ở dưới trong khung bo góc, đầu "trồi" lên khỏi khung; phía trên giải thích ý: **trước → sau** có mũi tên, hoặc danh sách đánh số | không bắt buộc (có ảnh thì đẹp hơn) |
| `split-screen` | Chia đôi màn hình: trên là hình minh hoạ (nhãn "Bước 1", tiêu đề, cửa sổ: lưới ảnh có con trỏ chọn / ảnh chụp màn hình / danh sách tích dần), dưới là người nói; phụ đề nằm trên đường chia | ảnh chụp màn hình (tuỳ chọn) |
| `ranking-list` | **Bảng xếp hạng S → F** trên ngực: mỗi món hiện lên khi được nhắc tên, rơi vào hạng khi nói kết luận | ảnh các món (tuỳ chọn) |
| `storytelling` | **3 thẻ hình** phía trên + tiêu đề nền đen + phụ đề nhỏ, xuất hiện cùng lúc trên một đoạn quay liền, phụ đề kiểu TikTok | ảnh / bài đăng của chính bạn |

## Dùng thế nào (người dùng)

Bỏ clip vào `vse-workspace/projects/<tên>/raw/` như thường, rồi nhắn Claude, ví dụ:

- *"Dựng clip IMG_1234 trong projects/quan-moi theo kiểu explainer, chọn đoạn hay nhất."*
- *"Làm trial-reels 3 bản từ đoạn mở đầu clip này để mình đăng thử."*
- *"Dựng split-screen bước 1 cho clip hướng dẫn, phía trên là ảnh chụp màn hình trong thư mục assets."*
- *"Clip này mình xếp hạng mấy món ăn, làm ranking-list giúp."*

Claude sẽ: chép lời → chọn đoạn → xem một khung hình để biết mắt / cằm ở đâu → viết spec → dựng → xem ảnh kiểm tra
(vùng đỏ là chỗ nút TikTok/Instagram che) → sửa nếu cần → đưa bạn file `output/<clip>.<kiểu>.mp4`.

Lần đầu trong mỗi phiên làm việc, Claude tự cài bộ dựng (~30 giây, ~250 MB, lấy từ npm). Một reel 7 giây mất
khoảng 1-3 phút; kiểu có tách người (`behind-the-person`, `explainer`) lâu hơn. Claude có thể phải chạy 2-3 lượt
(báo `CONTINUE`) - bình thường.

## Quy tắc chung (rút từ 6 bố cục)

- **Một ý mỗi clip.** Đoạn nói hai ý → làm hai reel.
- **Hình xuất hiện đúng lúc nói từ đó** - không có gì hiện trước khi được nói (trừ tiêu đề có sẵn từ khung đầu).
- **Không bịa số liệu, bình luận, tên người.** Con số / bình luận phải là thứ người nói nhắc tới hoặc bạn đưa.
- Chữ và đồ hoạ tránh 220 px trên cùng, 420 px dưới cùng và 100 px mỗi bên; phụ đề không che miệng.
- Dùng ảnh của chính bạn. Ảnh / logo người khác chỉ khi được phép; thẻ chữ luôn dùng được.
- `trial-reels`: ba bản phải khác nhau về **lời hứa**, không chỉ khác màu chữ. Đăng cả ba cùng ngày, giữ bản có tỉ lệ
  giữ chân 3 giây đầu tốt nhất.

## Cho Claude (kỹ thuật)

- Lệnh: `$V reel setup | list | words | frame | sheet | build <layout> <spec.json>` (`scripts/reels_cli.py`).
  Hướng dẫn từng bố cục, định dạng spec, quy tắc thẩm mỹ: `reels/<layout>/GUIDE.md` - đọc trước khi viết spec.
- Spec để ở `<job>/plans/<clip>.<layout>.json`, đường dẫn tính từ file spec (`"video": "../raw/IMG_1234.MOV"`).
  Mốc thời gian là giây tính từ `start` hoặc **từ được nói** (`"vui"`, `"học#2"`, `"tâm+0.2"`) - dùng từ, viết thường.
- Lời chép bằng model tiếng Việt trong máy (không dấu câu): `reel words` xuống dòng ở mỗi khoảng lặng.
  Sửa chính tả phụ đề bằng `"fix": {"tu-asr": "Từ đúng"}` trong spec, hoặc `$V style word` (my-style).
- Tiêu đề, nhãn, thẻ: viết tiếng Việt có dấu. Font có dấu: Inter, Montserrat Black (thay Archivo Black), Playfair
  Display / Noto Serif Display (thay hai font serif), VT323 (thay font pixel), TikTok Sans.
- Nhãn mặc định đã là tiếng Việt (Trước / Sau, VUỐT →, Theo dõi, Bình luận...); đổi bằng các trường `label`, `cta`,
  `button`, `title` trong spec.
- Render chia đoạn 2 giây (`VSE_REEL_CHUNK`), mỗi đoạn lưu lại; tách người lưu theo từng 60 khung. Thoát mã 3 =
  chạy lại đúng lệnh. Bộ dựng nằm ngoài thư mục chia sẻ (`~/.cache/vse-reels-runtime`, `~/.cache/vse-reels-build`) vì
  HyperFrames cần xoá file tạm và symlink, mà thư mục Cowork không cho.
- Sau khi giao reel, hỏi góp ý và ghi vào my-style như mọi video (`$V style note ... --tag reels`).
