## ⚙️ Hướng Dẫn Toàn Diện Cho AI: Clean Code, PEP 8 & Comment Tiếng Việt

**Mục tiêu cốt lõi:** Luôn tạo ra code **sạch (Clean Code)**, tuân thủ nghiêm ngặt **PEP 8 (nếu là Python)**, và sử dụng **tiếng Việt** để comment code một cách ngắn gọn, rõ ràng, và có ý nghĩa.

---

## I. Nguyên Tắc Clean Code Bắt Buộc

| Quy Tắc                      | Mô Tả Yêu Cầu Chi Tiết                                                                                              |
| :--------------------------- | :------------------------------------------------------------------------------------------------------------------ |
| **Tên Rõ Ràng & Có Ý Nghĩa** | Tên biến, hàm, lớp (class) phải **mô tả rõ ràng** mục đích của chúng. (Ví dụ: `tinh_tong_don_hang` thay vì `ttdh`). |
| **Hàm Ngắn Gọn**             | Hàm phải **ngắn nhất có thể** và chỉ làm **một việc duy nhất** (Single Responsibility Principle - SRP).             |
| **Tránh Lặp Lại (DRY)**      | Không lặp lại cùng một đoạn logic (Don't Repeat Yourself). Tái sử dụng code thông qua hàm, lớp hoặc module.         |
| **Xử Lý Lỗi Rõ Ràng**        | Xử lý các trường hợp lỗi một cách rõ ràng, tránh trả về các giá trị mơ hồ như `None` nếu có thể.                    |
| **Định Dạng Nhất Quán**      | Luôn áp dụng phong cách định dạng (dấu cách, thụt đầu dòng, xuống dòng) phù hợp với ngôn ngữ.                       |

---

## II. Quy Tắc Python Cụ Thể (PEP 8)

Khi viết code Python, **BẮT BUỘC** tuân thủ PEP 8:

1.  **Thụt Lề (Indentation):** Dùng **4 khoảng trắng** (spaces) cho mỗi cấp độ thụt lề. **Không dùng tab.**
2.  **Độ Dài Dòng:** Giới hạn dòng ở **79 ký tự** (72 ký tự cho docstring/comment dài).
3.  **Đặt Tên:**
    - **`snake_case`** cho biến, hàm, phương thức (ví dụ: `du_lieu_khach_hang`).
    - **`CapWords`** (PascalCase) cho tên Lớp (ví dụ: `DonHangMoi`).
    - **`CAPS_SNAKE_CASE`** cho Hằng Số (ví dụ: `GIOI_HAN_TUOI`).
4.  **Imports:**
    - Mỗi `import` trên một dòng riêng.
    - Nhóm theo thứ tự: Thư viện chuẩn > Thư viện bên thứ ba > Thư viện cục bộ (cách nhau bởi một dòng trống).

---

## III. Quy Tắc Comment (Sử Dụng Tiếng Việt)

| Loại Comment          | Yêu Cầu Thực Hiện Bằng Tiếng Việt                                                                                     | Ghi Chú                                         |
| :-------------------- | :-------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------- |
| **Docstring**         | Bắt buộc mô tả **Chức năng chính**, **Tham số (Params)** và **Giá trị trả về (Return)** của các hàm và lớp công khai. | Sử dụng Tiếng Việt chuẩn.                       |
| **Giải Thích Logic**  | Chỉ comment những đoạn code có **logic không hiển nhiên** hoặc **cần giải thích LÝ DO** cho quyết định thiết kế.      | **Hạn chế** comment code đã rõ ràng.            |
| **Định Dạng**         | Comment phải **ngắn gọn** (không quá một câu), **súc tích**, và **nằm sát dòng code** mà nó giải thích.               | Sử dụng dấu `//` hoặc `#` tùy ngôn ngữ.         |
| **Ghi Chú Công Việc** | Sử dụng **`// TODO:`** hoặc **`# FIXME:`** để đánh dấu những việc cần làm/sửa sau này.                                | Giữ nguyên từ khóa tiếng Anh (`TODO`, `FIXME`). |

---

## 🚀 Tóm Tắt & Ưu Tiên

1.  **Code phải tự giải thích trước.**
2.  **Chỉ comment những gì không thể tự giải thích.**
3.  **Tất cả comment phải ngắn gọn bằng TIẾNG VIỆT.**
4.  **Code Python phải tuân thủ PEP 8.**
