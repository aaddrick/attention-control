<p align="center">
  <strong>Attention Control</strong><br>
  <em>Kỷ luật của kiểm soát không lưu, áp dụng cho đầu ra của AI.</em><br>
  <em>Viết cho người đọc có ADHD.</em>
</p>

<p align="center">
  <a href="../../LICENSE"><img src="https://img.shields.io/github/license/aaddrick/attention-control?style=flat" alt="License"></a>
  <a href="../workflows/plugin-load-check.yml"><img src="https://img.shields.io/github/actions/workflow/status/aaddrick/attention-control/plugin-load-check.yml?label=plugin%20loads&style=flat" alt="Plugin load check"></a>
</p>

<p align="center">
  <a href="../../README.md">English</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.ko.md">한국어</a> ·
  <strong>Tiếng Việt</strong> ·
  <a href="README.pt-BR.md">Português (BR)</a>
</p>

## Cài đặt

<details open>
<summary><strong>Claude Code</strong></summary>

```bash
claude plugin marketplace add aaddrick/attention-control
claude plugin install attention-control@attention-control
```

Sau đó chạy `/config`, chọn **Output style**, rồi chọn **Attention Control**. Nó
có hiệu lực sau `/clear` hoặc ở phiên làm việc kế tiếp.

Muốn bỏ qua menu chọn, hãy thêm dòng này vào `~/.claude/settings.json`:

```json
{ "outputStyle": "Attention Control" }
```

</details>

<details>
<summary><strong>Codex</strong></summary>

```bash
codex plugin marketplace add aaddrick/attention-control --ref main
codex plugin add attention-control@attention-control
```

Sau đó gõ `$attention-control` để áp dụng phong cách này.

</details>

<details>
<summary><strong>Cursor, Gemini CLI và cài đặt thủ công</strong></summary>

Xem [INSTALL.md](../../INSTALL.md).

</details>

## Nó làm gì

Thuật ngữ kiểm soát không lưu tồn tại vì một lý do: một người đang quá tải sẽ nghe
nhầm chỉ dẫn. Ngành hàng không giải quyết việc này bằng hai kỷ luật. Từ vựng được
kiểm soát khiến mỗi từ chỉ mang một nghĩa. Cấu trúc thông điệp cố định đặt chỉ dẫn
lên trước và bối cảnh xuống sau.

Phong cách này áp dụng cả hai kỷ luật cho trợ lý lập trình của bạn. Trợ lý mở đầu
bằng hành động bạn có thể chạy ngay, và viết mỗi câu sao cho một từ chỉ mang một
nghĩa.

Phong cách này nhắm tới một loại người đọc: người đọc có ADHD. Các quy tắc hình dạng
sinh ra từ người đọc đó. Xem
[Vì sao có các quy tắc hình dạng](#vì-sao-có-các-quy-tắc-hình-dạng).

## Điều gì thay đổi

<table>
<tr>
<td width="50%">

### Trước

> Câu hỏi hay! Để tôi xem qua. Có vẻ luồng xác thực của bạn có vài phần liên quan
> đến nhau. Nhìn vào `src/auth.ts`, logic xác minh token có thể đang dùng một API
> đã lỗi thời — hàm `verifyToken` quanh dòng 42-58 dường như được viết theo chữ ký
> cũ của `jsonwebtoken`. Một hướng có thể cân nhắc là cập nhật gói này và tái cấu
> trúc hàm đó. Nhân tiện, các phiên bản phụ thuộc nói chung của bạn có lẽ cũng nên
> được rà lại vào lúc nào đó. Hy vọng điều này hữu ích! Cứ cho tôi biết nếu bạn
> muốn tìm hiểu sâu hơn phần nào.

</td>
<td width="50%">

### Sau

> Chạy `npm install jsonwebtoken@latest`, rồi sửa `src/auth.ts:42`.
>
> 1. Mở `src/auth.ts`
> 2. Thay `verifyToken` (dòng 42–58) bằng đoạn mã bên dưới
> 3. Chạy `npm test -- auth.spec.ts`
>
> Chữ ký cũ gây ra lỗi này. `jsonwebtoken` v9 đã bỏ dạng callback mà dòng 47 dùng.
>
> Tiếp theo: dán dòng lỗi đầu tiên nếu một bài kiểm thử thất bại.

</td>
</tr>
</table>

## Hai lớp

**Hình dạng** quyết định nói gì và theo thứ tự nào. 10 quy tắc:

1. Mở đầu bằng hành động kế tiếp.
2. Đánh số công việc nhiều bước.
3. Kết thúc bằng một hành động kế tiếp cụ thể.
4. Chặn các nhánh lạc đề.
5. Nhắc lại trạng thái ở mỗi lượt.
6. Ước lượng thời gian bằng đơn vị cụ thể.
7. Cho thấy điều gì giờ đã chạy được.
8. Báo lỗi một cách thẳng thắn.
9. Giới hạn danh sách ở 5 mục.
10. Không mở bài, không tóm tắt lại, không câu chào kết.

**Ngôn ngữ** quyết định cách viết từng câu:

- Một từ, một nghĩa. Một hành động, một động từ. Không xoay vòng từ đồng nghĩa.
- Động từ chuẩn: check, make sure, start, stop, use, show, find, change, remove, need.
- Dùng thể chủ động và nêu rõ chủ thể hành động.
- Chỉ dùng thì đơn. Không dùng thì hoàn thành, không chồng trợ động từ.
- Tối đa 20 từ mỗi câu chỉ dẫn, 25 từ mỗi câu giải thích. Cụm danh từ tối đa 3 từ.

Toàn văn: [`output-styles/attention-control.md`](../../output-styles/attention-control.md).

## Vì sao có các quy tắc hình dạng

Năm sự thật về cách người có ADHD đọc sinh ra toàn bộ 10 quy tắc hình dạng. Bảng
dưới đây ghi rõ mỗi sự thật tạo ra quy tắc nào.

| Sự thật | Trợ lý làm gì |
|---|---|
| **Trí nhớ làm việc rất nhỏ.** Thứ không nằm trên màn hình coi như không còn. | Nó không bao giờ viết "hãy nhớ X". Nó nhắc lại trạng thái ở mỗi lượt: "Xong bước 3 trên 5: tôi đã đổi schema. Tiếp theo: chạy `scripts/backfill.py`." (quy tắc 5, 9) |
| **Biết câu trả lời khác với làm xong câu trả lời.** Công việc chết ở khoảng trống giữa hai điều đó. | Nó đưa câu lệnh, không đưa nhãn. "Thêm header còn thiếu" là một cái nhãn. `Authorization: Bearer ${token}` mới là bản sửa. (quy tắc 1, 2) |
| **Bắt đầu là bước khó nhất.** | Dòng đầu tiên phải nhỏ, rõ ràng và làm được ngay. Dòng cuối nêu một hành động mất chưa tới hai phút. "Mở tệp" cũng được tính. (quy tắc 1, 3) |
| **Mọi ước lượng thời gian nghe như nhau.** "Hơi mất công" và "vài giờ" đọng lại giống hệt nhau. | Nó viết "khoảng 15 phút nếu đã có kiểm thử, cả một buổi chiều nếu chưa". Nó không viết "hơi mất công". (quy tắc 6) |
| **Dopamine khan hiếm.** Một thắng lợi bị chôn vùi thì không đọng lại. | Sau khi sửa, nó nêu kết quả bằng lời cụ thể: "Đăng nhập bằng magic link đã chạy. Chạy `npm run dev` và mở `/login`." (quy tắc 7) |

Hai quy tắc nữa bảo vệ chính sự chú ý. Quy tắc 4 chặn lạc đề, nên một việc đang mở
vẫn chỉ là một việc. Quy tắc 10 bỏ phần mở bài và câu chào kết, nên câu trả lời bắt
đầu ngay ở dòng 1.

Vì vậy phong cách này không phải là "nói cho ngắn". Sự ngắn gọn mà bỏ mất câu lệnh,
con số hay điều kiện sẽ bắt người đọc đi thêm một vòng, và một vòng như thế đủ làm
đứt mạch việc. Quy tắc 8 cũng theo logic đó: một lỗi cần vị trí, nguyên nhân và bản
sửa, không kèm "ôi không" ở phía trước. Sự hốt hoảng không phải thông tin, mà nó
tranh cùng một phần chú ý với thông tin.

Bạn không cần chẩn đoán ADHD thì điều này mới có ích. Một người đọc đang mệt, một
người đọc trên điện thoại và một người mở 40 tab đều đọc theo cùng một cách.

## Điều nó không bao giờ đụng tới

Mã nguồn, lệnh, đường dẫn tệp, định danh, thông báo lỗi và văn bản trích dẫn được
giữ nguyên từng ký tự. Phong cách này chỉ chi phối phần văn xuôi do chính trợ lý
viết ra.

Độ chính xác quan trọng hơn sự ngắn gọn. Không quy tắc nào loại bỏ một sự kiện, một
con số, một điều kiện hay một giới hạn phạm vi để rút ngắn câu. Một cách nói dè dặt
mang sự không chắc chắn thật sự thì được giữ lại.

## Đánh giá

Bộ đánh giá so sánh chất lượng phản hồi với một mốc chuẩn không áp phong cách. Nó
không đo độ dài.

```bash
python3 scripts/run_evals.py validate
python3 scripts/run_evals.py plan --trials 3
```

20 ca kiểm thử, 6 tiêu chí chấm điểm, và một cổng phát hành chặn ứng viên làm giảm
độ chính xác hoặc độ an toàn.

Điểm yếu nằm ở bộ chấm, nên bộ đánh giá nhắm thẳng vào đó. `blind` giấu điều kiện và
cân bằng vị trí trình bày. Bộ chấm chấm mỗi nhóm hai lần, lần sau đảo ngược thứ tự,
rồi báo cáo hai lần lệch nhau bao nhiêu. Trình chạy làm việc trong một thư mục rỗng
và không đọc cấu hình nào của bạn. Ghi chú thiết kế và số đo đứng sau nó nằm ở
[evals/README.md](../../evals/README.md).

## Tự chỉnh

Fork, sửa `output-styles/attention-control.md`, rồi tạo lại mọi bản sao dành riêng
cho từng trợ lý:

```bash
python3 scripts/sync_style.py
```

Thay bằng bản của bạn:

```bash
claude plugin uninstall attention-control
claude plugin marketplace remove attention-control
claude plugin marketplace add <your-username>/attention-control
claude plugin install attention-control@attention-control
```

## Ghi công

Phong cách này kết hợp hai tác phẩm đã có. Không tác giả nào trong hai người tham
gia dự án này.

**Lớp hình dạng:** [`i-have-adhd`](https://github.com/ayghri/i-have-adhd) của
Ayoub G. (MIT). Bộ đánh giá cũng bắt nguồn từ dự án đó.

**Lớp ngôn ngữ:** [phong cách đầu ra `asd-ste100`](https://gist.github.com/L1nefeed/4164ecaaf77879e76dca3c06f142f1c2)
của [L1nefeed](https://github.com/L1nefeed), bản thân nó là bản cô đọng của
[ASD-STE100](https://www.asd-ste100.org/) Simplified Technical English, ấn bản 9.

Dự án này không sao chép văn bản nào từ đặc tả ASD và không được chứng nhận, xác
nhận hay liên kết với tổ chức phát hành. Chi tiết trong [NOTICE.md](../../NOTICE.md).

## Giấy phép

MIT. Xem [LICENSE](../../LICENSE).
