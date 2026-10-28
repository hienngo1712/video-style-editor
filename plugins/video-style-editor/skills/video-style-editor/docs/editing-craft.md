# Tay nghề dựng: bài học từ khoá CapCut + góp ý của editor chuyên

Tổng hợp 10/2026 từ hai nguồn, viết lại bằng lời của mình (không chép bài giảng):
- **Khoá CapCut PC 16 bài** (thông số, timeline, âm thanh, chữ, beauty, hiệu ứng, tốc độ, keyframe, tách nền,
  màu, proxy/xuất). Ghi chú: bài 2, 6+7, 8 bị cụt cuối ở file gốc.
- **Góp ý của 3 editor** sau khi xem 8 video của skill (6 bản FFmpeg + 2 bản CapCut) - mục 11.

Ký hiệu: **[F]** áp dụng được trong `render.py` (FFmpeg) · **[C]** chỉ làm trong CapCut ·
**[K]** khoá học nói rõ · **[G]** gợi ý của mình để lấp chỗ khoá không dạy (kiểm bằng tai/mắt trước khi tin).

---

## 0. Checklist trước khi xuất (đọc cái này nếu chỉ có 1 phút)

1. 1080×1920, **30 fps cố định**, SDR **Rec.709**, H.264 yuv420p - không giao HDR. [K][F]
2. Thoại sạch: lọc ồn (RNNoise 60 %) → đủ to, đỉnh **chạm vàng không chạm đỏ** (true peak ≤ −1,5 dBTP). [K][F]
3. Nhạc nền nằm **dưới** giọng, có ducking; SFX đa dạng, không 1 tiếng quá 2 lần, nhỏ hơn giọng. [K][G][F]
4. Phụ đề ở **~3/4 chiều cao** (giữa nửa dưới), trong vùng an toàn TikTok, không đè mặt. [K][F]
5. Một kiểu chữ cho cả video; từ khoá dùng cố định 1–2 kiểu hiệu ứng vào/ra. Phụ đề hiện **sau** tiếng nói ~0,2 s,
   từng chữ theo lời; chữ lớn hiện đúng lúc nói; không đè mặt. [K][editor]
6. Màu: chuẩn hoá từng clip (sáng, cân trắng) **trước**, rồi **một** look chung cho cả video. [K][F]
7. Cắt đúng khung, không hở; cắt hết ờ/à/ừ và khoảng lặng thừa (`tighten`); khung hình chuyển động mềm (zoom
   in/out có easing, punch-in vào mặt ở câu chốt). [K][F][editor]
8. Chuyển cảnh chỉ ở chỗ đổi ý/đổi phần, ngắn 0,3–0,5 s, cùng một kiểu. [G][editor]
9. Kiểm tổng thời lượng (không clip lạc cuối timeline) và **khung đầu tiên đủ đẹp làm ảnh bìa**. [K]

---

## 1. Thông số dự án và xuất

| Quy tắc | Nguồn | Trong skill |
|---|---|---|
| Khung 9:16 đặt rõ **1080×1920**, không để "Adapted" (CapCut lấy theo clip đầu tiên). Đổi tỉ lệ khung = đổi độ phân giải xuất | K | [F] `W,H = 1080,1920` |
| **30 fps** cho TikTok/Shopee/giải trí. FPS dự án ≠ FPS clip: clip 60 fps trên timeline 30 fps chỉ lấy 1/2 khung → giật hơn. Muốn slow-mo thì quay 60, dựng 30, giảm tốc 0,5× (`setpts=2*PTS`) | K | [F] `fps=30` - xem mục 8 |
| Màu xuất luôn **SDR Rec.709**. iPhone hay quay HEVC 10-bit HLG → phải tonemap về bt709 (`zscale=t=linear,tonemap=hable,zscale=p=709:t=709:m=709`) và gắn tag bt709 | K/G | [F] đã có - tự phát hiện HLG/PQ |
| Không phóng to rồi thu nhỏ nhiều lần; 4K → 1080 tốt, 1080 → 4K vô ích. Có nhiều sticker/chữ/hiệu ứng trên nguồn 1080p thì xuất 1440×2560 cho nét | K | – |
| Bitrate tham khảo (CapCut): 1080p **8 Mbps** (fps cao 12), 1440p 16/24, 2160p 35–45/53–68. Ô Custom tính bằng **kbps** (gõ 12000, không phải 12). "Recommended" là đủ, "Higher" khi cần đẹp nhất | K | [F] CRF 19–20 ≈ 10–16 Mbps, ổn |
| H.264 + MP4 an toàn nhất để đăng; HEVC nhỏ hơn ~10 % | K | [F] |
| Kiểm **tổng thời lượng** ở Player trước khi xuất - một clip lạc ở xa làm video dài ra | K | [F] `check` |
| Nền tảng lấy **khung đầu** làm ảnh bìa (hoặc CapCut: Export → Cover) → khung 0 phải đẹp, có chữ hook | K | quy tắc khi viết plan |
| Proxy (540/720p) chỉ để dựng mượt; xuất luôn dùng file gốc. Trong skill: phân tích trên bản nhẹ, render từ gốc | K | [F] đã làm |
| Không xuất vào ổ hệ thống C: | K | – |

## 2. Cắt và timeline

- Cắt **đúng khung đầu tiên của cảnh mới**; lùi 1 khung là để sót 1 khung cảnh cũ → giật/chớp. Kiểm mối nối. [K][F]
- Clip phải **liền nhau tuyệt đối** - hở 1 khung là chớp đen. CapCut: luôn bật **Auto snapping (S)**. [K][F]
- Dựng thật thì tắt **Main track magnet** (để tự do đặt lớp); cắt nhanh thì bật cho tự khép khoảng hở. [K][C]
- Tìm điểm cắt câu bằng **sóng âm**: cụm cao = chữ, đuôi tắt dần = hết cụm (skill đã làm bằng `inspect`). [K][F]
- Ảnh tĩnh mặc định 5 s là quá dài - đặt 2–3 s. [K][F]

## 3. Âm thanh

| Quy tắc | Nguồn | Cách làm |
|---|---|---|
| **Lọc ồn thoại** trước mọi thứ. CapCut: Audio → Basic → ☐ **Noise reduction** (kiểm xem có tốn credit không trước khi dùng) | C/G | [F] đã có: mặc định RNNoise 60 % cho mọi đoạn có lời (`denoise: light`), `strong` khi rất ồn; FFT `afftdn` không xử lý được tiếng người xung quanh |
| Nâng giọng tới khi đồng hồ **chạm vàng, không đỏ** (giọng nhỏ có lúc cần +10 dB). Nền tảng còn tự nâng thêm → để đỏ là chói | K | [F] `loudnorm` 2 lượt + limiter, mục tiêu −12 LUFS, đỉnh ≤ −1,5 dBTP |
| Nén nhẹ cho giọng đều | G | [F] `style.compress: true` - **tắt mặc định** vì test cho thấy nó đẩy tiếng nền lên |
| Nhạc nền chỉ "gần chạm" mốc, **dưới** giọng; có ducking khi nói | K/G | [F] `music.gain` −24..−18 + `duck: true` |
| SFX là phụ trợ, không phải nhân vật chính; tìm SFX bằng **tiếng Anh** | K | bảng từ khoá ở `capcut-guide.md` |
| **Đa dạng SFX**: không dùng 1 tiếng quá 2 lần / video; xoay vòng nhiều biến thể (whoosh_1489/1490/1492…) | editor | [F] quy tắc khi viết plan (lint nên cảnh báo) |
| SFX **không chói**: gain −12 bình thường, −16 tinh tế, −8 chỉ cho cú chốt hiếm | editor/G | [F] `sfx.gain` |
| Fade in/out nhạc 0,5–1 s | K | [F] `afade` |
| Nhạc CapCut miễn phí chỉ an toàn trên **TikTok**; đăng FB/YouTube/Shopee có kiếm tiền → nhạc có bản quyền (Epidemic, Artlist, Envato) và giữ giấy phép để kháng nghị | K | hỏi người dùng nền tảng đăng |

## 4. Chữ và phụ đề

**Vị trí - vùng an toàn TikTok 1080×1920** [K + G]

```
y   0 –  ~190 px (10 %)  : thanh trên (Đang theo dõi / Dành cho bạn) - không đặt chữ
y ~190 – ~1500 px        : vùng an toàn; tâm phụ đề ở ~1400–1450 px (≈ 75 % - giữa nửa dưới)
y ~1500 – 1920 px (20 %) : tên kênh, mô tả, hashtag, thanh nhạc - không đặt chữ
x  > ~950 px (cột phải)  : nút tim / bình luận / chia sẻ - tránh, nhất là ở nửa dưới
```

- Khoá học: chia đôi khung, phụ đề ở **giữa nửa dưới**. Thấp quá bị chữ TikTok che; ở giữa thì che mặt người;
  cao quá thì mỏi mắt vì người xem nhìn xuống. [K]
- **Skill hiện tại** (sau góp ý): phụ đề `Cap` bám đáy `caption_margin_v` **470** (trước là 640 → đáy chữ ở 67 %, đè
  vào giữa hình - đúng như editor nói); teaser 520; tiêu đề 230 (trước 150 - nằm trong thanh trên của TikTok).
  `check` vẽ đường đỏ giới hạn vùng an toàn lên ảnh kiểm tra. [F]
- Hành động diễn ra ở nửa dưới → `caption_pos: top` (tâm ~25–30 %), không đặt sát mép trên. [F]

**Kiểu chữ** [K]
- Font **không chân, đứng (không nghiêng), có Việt hoá** - thiếu Việt hoá là vỡ dấu (gặp ở CapCut: font template
  không có chữ hoa có dấu → dùng Oswald-Bold / Be Vietnam Pro).
- Cỡ vừa, không tràn mép (~60–76 px trên 1080 rộng; ≤ 2 dòng, ~16–20 ký tự/dòng). Đọc được ở preview nhỏ trên
  máy tính là đọc được trên điện thoại.
- Tương phản với nền; **viền (stroke) thay vì bóng** - bóng làm nhoè cạnh chữ nhỏ.
- **Một style cho cả video**: tạo 1 lớp chữ chuẩn → chia theo câu (kế thừa style) → sửa đồng loạt bằng chọn tất cả.

**Hiệu ứng chữ** [K + editor]
- CapCut: tab Animation → **In / Out / Loop**; kéo thanh trên clip chữ để đặt thời lượng; Loop chỉnh bằng Speed.
- **Chỉ dùng 1–2 kiểu vào/ra cố định** cho từ khoá suốt video (vd. pop-in 0,2 s cho từ khoá, slide-up cho tiêu đề).
  Quá nhiều kiểu → rối mắt. [F] đã có: chữ lớn + teaser "pop", tiêu đề hiện dần.
- **Mẫu tiêu đề (heading) cố định**: CapCut Text templates hoặc lưu sẵn 2–3 kiểu (tên quán/địa điểm, con số lớn,
  câu hook). Trong skill: style `Big`, `Title`, `Teaser` chính là bộ heading - giữ nhất quán giữa các video. [C][F]

**Làm phụ đề nhanh trong CapCut** [K]: nghe 1 lượt, đặt **marker** ở cuối mỗi câu → cắt lớp chữ tại marker → gõ.
Với skill: tải `captions.ass`/`.srt` lên (Captions → Upload caption file) rồi đổi style.

## 5. Chuyển cảnh và hiệu ứng

- Mặc định **cắt thẳng**. Thêm chuyển cảnh **ở chỗ đổi ý / đổi phần** (vào quán, chuyển sang phỏng vấn, kết),
  1–3 cái / video ~60 s, **cùng một kiểu**, 0,3–0,5 s. Không đặt ở mọi vết cắt. [G][editor]
- CapCut: chuyển cảnh chỉ đặt được **giữa 2 clip liền nhau trên track chính** (không ở track phụ, không qua khoảng hở);
  nhóm **Camera** là các kiểu zoom; Duration chỉnh trong bảng; có "Apply to all" (đừng lạm dụng). [K][C]
- Mẹo: chuyển cảnh vào clip đầu / ra clip cuối → đặt clip **Transparent** (Media → Library) bên cạnh; cũng dùng để
  làm video **loop liền mạch** (đuôi nối về đầu). [K]
- Hiệu ứng: kéo lớp effect lên timeline, nó tác động mọi thứ bên dưới trong đúng khoảng của nó. Chồng 2–3 hiệu ứng
  có thể ra look riêng - nhưng giữ tiết chế. [K][C]
- FFmpeg: `xfade=transition=zoomin|fade|slideleft|wipeleft:duration=0.3`; skill hiện có `paper`, `flash`. [F]

## 6. Keyframe, zoom nhấn

- Keyframe = đổi một thông số từ A → B trong một khoảng; sau keyframe cuối giá trị giữ nguyên. [K]
- **Punch-in**: Scale 100 → 130 % (150 % là mạnh), khớp động tác/từ khoá: key đầu khi hành động bắt đầu, key cuối khi
  xong, rồi trả về 100 %. Thấy trễ thì dời key **sớm hơn**. [K] Talking-head: 1,12–1,3. [G]
- Zoom + lia: key **cả Scale và Position** ở cùng điểm đầu, không thì khung bị khựng/nhảy. [K]
- **Giữ rồi mới chạy**: đặt 1 key "giữ" ngay trước điểm cue (A→B, giữ B, B→C) - thiếu nó chuyển động bắt đầu quá sớm. [K]
- Bẫy CapCut: đã có keyframe mà sửa khi đầu đọc **không đứng trên key** → tạo key mới → chuyển động giật/ngược.
  Luôn nhảy đúng key bằng ◁ ◇ ▷ trước khi sửa. [K][C]
- Easing (khoá không dạy): trong FFmpeg dùng smoothstep `p*p*(3-2*p)` hoặc ease-out `1-(1-p)^2`, dài 0,25–0,4 s;
  phóng ×2 trước khi zoompan để khỏi rung. [G][F]
- Keyframe màu theo nhịp nhạc (xám → bão hoà → vàng → sáng) để đánh dấu "reveal"/đổi phần. [K]

## 7. Tốc độ (speed ramp)

- Giới hạn slow-mo theo FPS nguồn: 30 fps → chỉ chậm nhẹ (~0,8×?); 60 fps → tới ~0,4×; 120/240 → 0,1–0,3×.
  Chậm hơn mức đó phải nội suy (CapCut: Smooth slow-mo → **Optical flow** / Frame blending; FFmpeg
  `minterpolate=fps=60:mi_mode=mci`) - optical flow có thể méo ở chuyển động nhanh. [K][F]
- Curve: tự kéo (Customize) thay vì preset; **mọi đỉnh phải thoải** (nâng 1 điểm thì nâng cả điểm bên cạnh). Đỉnh
  thường 2–3×; 5–10× là quá. [K] FFmpeg: ghép đoạn ngắn 1→1,5→2→1,5→1, không nhảy thẳng 1→3. [G]
- Ăn nhịp nhạc: marker ở **đầu mỗi beat**, nhanh trên beat, chậm giữa các beat; chỉnh xong độ dài clip rồi mới vẽ
  curve. Đoạn ramp thường tắt tiếng gốc, để nhạc dẫn. Giữ cao độ giọng (`atempo`); đổi cao độ chỉ để hài. [K]

## 8. Màu

**Thứ tự** [K]: (1) chuẩn hoá kỹ thuật (LOG/HDR → Rec.709) → (2) sáng/tương phản từng clip theo **scope** →
(3) cân trắng → (4) HSL để đồng bộ giữa các clip → (5) **một** look sáng tạo cho cả video → (6) hoàn thiện nhẹ.

- Tin **scope** (RGB parade / waveform 0–1023 / vectorscope) hơn màn hình. Vượt 1023 = cháy, không cứu được với
  file Rec.709; đè đen về 0 = mất chi tiết. [K]
- Cân trắng: chỉnh Temp/Tint tới khi 3 kênh R-G-B **trùng nhau ở vùng trắng/xám**. [K] FFmpeg `grayworld` hoặc
  `colortemperature`. [F]
- Làm sáng mặt bằng **Highlight** (hoặc curves vùng trung), không kéo Brightness toàn khung - mặt cần cả vùng sáng và
  vùng tối để có khối. [K] FFmpeg `curves` chữ S nhẹ, đỉnh < 1. [F]
- Tương phản vừa đủ để không bẹt (`eq=contrast=1.05–1.15`); bão hoà theo cảm xúc (giảm = hoài niệm/êm, tăng = tươi);
  thường giảm nhẹ sau khi áp LUT; `vibrance` an toàn cho da hơn `saturation`. [K][F]
- Look: **một lớp Filter/Adjustment phủ cả video**, cường độ **70–80 %**; **không chồng 2 filter**. LUT sáng tạo
  không áp lên footage LOG chưa chuẩn hoá. [K] FFmpeg: `lut3d` trộn 70–100 % (`blend=all_opacity`). [F]
- Hoàn thiện: Fade nhẹ (nâng đen → cảm giác film), grain nhẹ, vignette kéo mắt vào chủ thể; sharpen hiếm khi cần. [K]
- **Tự động cân sáng trong skill** [G][F]: đo mỗi clip **một lần** bằng `signalstats` (YAVG/YMIN/YMAX) → sửa cố định
  (`eq=gamma/brightness` hoặc `curves`) về cùng mục tiêu (YAVG ~0,42–0,50, không cắt trắng). **Không** dùng
  `normalize`/`histeq` theo từng khung → nhấp nháy. Đã có: `style.color_match`, `style.look` (mục 12).
- Da người: làm mịn nhẹ thôi - mịn hết cỡ mất sáng tối, thành da nhựa; sửa từ lúc quay (dặn mở mắt tự nhiên…). [K]

## 9. Tách nền, clip ngang trong video dọc

- Auto removal (CapCut) tách người không cần phông xanh - chỉ có trong CapCut. Phông xanh/xanh dương vì ít trùng da,
  tóc, môi; mặc đồ xanh thì key màu xanh dương. [K][C]
- Clip ngang trong video dọc: nền **mờ** cùng clip (CapCut: Basic → Background → Blur; FFmpeg
  `split → scale+crop+boxblur làm nền → overlay clip ở giữa`) thay vì cắt mất 2 bên. [K][F] đã có: `fit: blur`.

## 10. Thói quen CapCut nên cài một lần

Shortcut preset **"Shortcut 2"** (giống Premiere: C = dao cắt, Ctrl+K cắt tại đầu đọc, S = snapping, ←/→ từng khung,
↑/↓ nhảy điểm cắt, Ctrl+M xuất) · Auto snapping **bật** · Preview axis (Shift+P) **tắt** · Free layer **bật** ·
Preview quality = Performance priority (không ảnh hưởng xuất) · Image duration 2–3 s · project fps = 30, color space
Rec.709 · iPhone HEVC trên Windows: cài codec (K-Lite) để xem được file. [K][C]

---

## 11. Góp ý của 3 editor (10/2026, xem cả 8 video) → hướng xử lý

| Góp ý | Nguồn khoá học | Trạng thái trong skill |
|---|---|---|
| Âm thanh chưa lọc ồn, còn tạp âm (cả 3) | Mục 3 | `denoise` có nhưng phải bật tay → **mặc định lọc nhẹ mọi đoạn thoại**  |
| SFX đơn điệu, lặp; phần 2 bị chói | Mục 3 | quy tắc ≤ 2 lần/tiếng, gain −12/−16; lint đếm lặp  |
| Chưa cân sáng tự động, chưa có LUT/màu (cả 3) | Mục 8 | đo `signalstats` + 1 look chung (`color_match`, `look` - đã có) |
| Chữ có thể lòi khỏi vùng an toàn TikTok; phụ đề che giữa hình | Mục 4 | `caption_margin_v` ≈ 440–480, Title ≥ 220 (đổi mặc định) |
| Từ khoá nên 1–2 kiểu hiệu ứng vào/ra cố định | Mục 4 | quy tắc khi làm CapCut; hiệu ứng vào cho `big`/từ khoá  |
| Nên có heading sẵn | Mục 4 | `Big`/`Title`/`Teaser` là bộ heading; giữ nhất quán |
| Chuyển cảnh chỉ ở đầu, cần 1–2 cái ở chỗ chuyển ý | Mục 5 | quy tắc khi viết plan: đánh dấu chỗ đổi phần → `transition` |
| Lời/mạch nội dung cần dạy AI từ từ | – | ghi mỗi góp ý về câu chữ vào `SKILL.md` mục 3 |

## 12. Đã đưa vào `render.py` (26/10/2026) và kết quả test trên 2 video barber (v3 → v4)

| Việc | Cách làm trong skill | Đo được |
|---|---|---|
| Lọc ồn thoại | mặc định `denoise: light` cho mọi đoạn có phụ đề = RNNoise (`arnndn`, model "leavened-quisling", tải ở `setup_assets.py`) trộn **60 %**; `strong` = 100 %. Gemini nghe bản 80 %: giọng ngoài trời bị nghẹt, người nói xa mic (không cài mic) bị nuốt, đuôi chữ nhẹ ("đi") bị cụt → hạ xuống 60 %; người nói xa mic: `denoise: false` + `vol`. FFT (`afftdn`) gần như vô dụng với tiếng người nói xung quanh (đo: +0,5 dB) nên chỉ là dự phòng khi thiếu model | khoảng cách giọng/tiếng nền +10…+20 dB (ở 80 %) |
| Bộ nén giọng | có `style.compress` nhưng **tắt mặc định** - test cho thấy nó đẩy tiếng nền giữa các chữ lên ~4 dB | – |
| Cân sáng | `color_match`: đo YAVG từng clip một lần (keyframe) → `eq=gamma` cố định, đi 70 % về mục tiêu 0,45 | P2: độ sáng 100–147 → 102–127, hết nhảy sáng; P1: 5 → 2 lần nhảy (còn lại là chớp trắng chủ ý) |
| Màu chung | `style.look` (`clean` mặc định = tương phản 1,05 + vibrance nhẹ; `warm`/`cool`/`film`/file `.cube` trộn 80 %) | đồng đều hơn khi xem ảnh so sánh |
| HDR iPhone | tự phát hiện HLG/PQ → tonemap về Rec.709 (`zscale`+`tonemap=hable`), gắn tag bt709 khi xuất | thử bằng clip HLG giả lập |
| Vùng an toàn | phụ đề `caption_margin_v` 470 (≈ 72–75 % chiều cao), teaser 520, tiêu đề 230; `check` vẽ đường đỏ giới hạn | phụ đề nằm trên áo choàng, không đè mặt |
| Hiệu ứng chữ cố định | chữ lớn + câu teaser: "pop" 112–135 % → 100 %; tiêu đề: hiện dần | – |
| Chuyển cảnh giữa video | `transition: zoom`; lint cảnh báo video > 45 s không có chuyển cảnh ở giữa | P1 thêm 2 cái ở chỗ đến quán / bắt đầu cắt tóc |
| SFX đơn điệu, chói | lint cảnh báo 1 SFX > 2 lần; P2 hạ gain (−4…−7 → −10…−12) | lint sạch |
| Clip ngang | `fit: blur` | thử bằng ảnh test |
| Xuất bị ngắt giữa chừng | bước ghép cuối chia đoạn 12 s, lưu lại, chạy tiếp được (máy ảo 2 nhân: ~2,3 s xử lý / 1 s video, video > 70 s vượt 1 lần chạy lệnh) | P2 82 s xuất trọn vẹn qua 2 lần chạy |
| Độ to | mục tiêu −12 LUFS (nền tảng tự đưa về ~−14) | −11,9 / −12,2 LUFS, đỉnh ≤ −1,6 dBTP |

Chưa làm: cân trắng tự động (dễ lệch màu khi khung hình nhiều hoa đỏ/biển hiệu) - chỉnh tay bằng `tint`;
easing cho zoom của từng đoạn (`zoom` hiện là cố định, chỉ `transition: zoom` có chuyển động).

## 13. Góp ý bằng video của editor (28/10/2026) → đã đưa vào code

Editor xem các bản dựng (cả bản FFmpeg và bản CapCut) rồi quay màn hình nói góp ý. Skill nghe lại bằng cách chuyển
lời thành chữ (ASR tiếng Việt) và xem khung hình. Các điểm chính và cách skill xử lý:

| Editor nói | Vì sao | Trong skill bây giờ |
|---|---|---|
| Chữ (phụ đề, chữ lớn "TỰ CHỦ / TỰ DO / TỰ LO") nhảy ra **trước** khi nói | người xem đọc trước câu chốt → mất hay | phụ đề hiện **sau tiếng nói ~0,2 s** (`caption_lag`), mốc chữ bắt theo lúc tiếng thật sự bật lên (mốc ASR sớm ~50 ms, 1/4 số chữ sớm ≥ 0,2 s); hiện **từng chữ theo lời** (`caption_reveal`); chữ lớn nhiều dòng hiện từng dòng đúng lúc nói dòng đó |
| Một đoạn (bản CapCut, cảnh trong xe) phụ đề lệch 1–2 s | file phụ đề nhập vào CapCut lệch | CapCut: nhập phụ đề xong kiểm khớp ở 3 chỗ (đầu/giữa/cuối), lùi cả lớp +0,2 s |
| Cắt hết "ừ, à, ờ", phần thừa | video liền mạch, người xem không muốn dừng | `vse.py tighten`: cắt tiếng đệm + lặng > 0,45 s, chỗ cắt đổi zoom 1,0/1,12 thành jump cut có chủ ý; liệt kê chỗ "có tiếng mà không có chữ" (ASR hay bỏ sót "ờ") để kiểm |
| Zoom in vào mặt người được nhắc tới; zoom in/out có keyframe mềm | khung hình có nhịp, nhấn đúng chỗ | `motion: auto`: mỗi đoạn ≥ 1,5 s đẩy vào/kéo ra chậm 6 % có easing; chữ lớn → punch-in +12 % vào mặt người nói; zoom nhắm vào mặt (YuNet) |
| Chữ đè mặt người ngồi giữa khung | mặt là chỗ người xem nhìn | dò mặt từng đoạn (3 khung) → phụ đề lên trên / teaser lên trên / chữ lớn xuống dưới nếu đè mặt |

Đo trên 2 video barber (v5 → v6): phụ đề 0 lần chồng nhau (check báo), cắt thêm 0,8 s + 1,7 s thừa, độ sáng không
đổi, xuất trong giới hạn thời gian máy (mỗi lệnh ≤ 150 s, chạy tiếp được).

Bài học khi làm tự động (cho người sửa code):
- `import cv2` (opencv-python) tự gắn thư viện của nó vào `LD_LIBRARY_PATH` → mọi lệnh ffmpeg sau đó chậm ~20 lần.
  `faces.py` trả biến này về như cũ ngay sau khi import.
- Sự kiện phụ đề chồng thời gian nhau thì libass xếp chồng 2 dòng → nhìn như chữ bị nhân đôi. `build_ass` nối đuôi
  các sự kiện; `check` đếm số chỗ chồng (phải là 0).
- OpenCV 5 bỏ Haar cascade → dùng YuNet (`setup_assets.py` tải model 230 KB).
