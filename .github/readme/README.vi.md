<p align="center">
  <strong>Attention Control</strong><br>
  <em>Kỷ luật của kiểm soát không lưu, áp dụng cho đầu ra của AI.</em>
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
độ chính xác hoặc độ an toàn. Xem [evals/README.md](../../evals/README.md).

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
