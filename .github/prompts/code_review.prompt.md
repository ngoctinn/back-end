# ĐÁNH GIÁ CODE KỸ THUẬT (THOROUGH CODE REVIEW)

## NGỮ CẢNH

Giả định tính năng đã được triển khai xong (code) và có kế hoạch kỹ thuật (`@PLAN.md`) đính kèm.

## NHIỆM VỤ

Thực hiện đánh giá code toàn diện. Lưu tài liệu về các phát hiện vào duy nhất 1 file `docs/features/<N>_REVIEW.md`.

## YÊU CẦU KIỂM TRA CHUYÊN SÂU

1.  **Triển khai Kế hoạch:** Đảm bảo rằng kế hoạch kỹ thuật đã được triển khai CHÍNH XÁC.
2.  **Lỗi và Vấn đề:** Tìm kiếm bất kỳ lỗi (bug) hoặc vấn đề rõ ràng nào trong logic.
3.  **Căn chỉnh Dữ liệu (Data Alignment):** Tìm các vấn đề tinh tế như không khớp quy ước đặt tên (ví dụ: mong đợi `snake_case` nhưng nhận được `camelCase`) hoặc cấu trúc dữ liệu bị lồng nhau không cần thiết.
4.  **Tái cấu trúc và Hiệu suất:** Tìm kiếm sự quá kỹ thuật hóa (`over-engineering`), code thừa, hoặc các tệp quá lớn (cần tái cấu trúc, khuyến nghị dưới 300 dòng).
5.  **Phong cách Code:** Đánh giá cú pháp và style có nhất quán với phần còn lại của codebase không.
