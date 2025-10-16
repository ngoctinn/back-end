## Xác thực và Quản lý Phiên với FastAPI

Tính năng Chính: Hệ thống Xác thực Người dùng (Auth Service) và Quản lý Truy cập dựa trên Vai trò (RBAC) hoàn chỉnh cho Backend REST API.

Ngữ cảnh:

Mô hình User: Chỉ lưu trữ thông tin xác thực (email, password_hash, roles).

Tách biệt Domain: Người dùng (User) là một đối tượng xác thực riêng biệt, không chứa dữ liệu nghiệp vụ (Nhân viên/Khách hàng).

Quản lý Phiên: Sử dụng JWT (Access Token) và Opaque Refresh Token để quản lý phiên an toàn.

Toàn diện: Hỗ trợ đầy đủ các luồng cơ bản (Đăng ký/Đăng nhập), Xác minh Email, và Đặt lại Mật khẩu an toàn.

### Mục tiêu

- Triển khai hệ thống xác thực người dùng an toàn với FastAPI.
- Sử dụng JWT cho Access Token và Opaque Token cho Refresh Token.
- Áp dụng Role-Based Access Control (RBAC) để phân quyền người dùng.
- Đảm bảo các luồng xác thực, quản lý phiên và khôi phục tài khoản an toàn.

1. Luồng Xác thực Tài khoản Mới
   Đăng ký (POST /auth/register): Hệ thống nhận thông tin, sử dụng Bcrypt để hash mật khẩu, tạo User mới (với trạng thái chưa kích hoạt), gán Role mặc định (user). Sau đó, tạo Verification Token (Opaque) và gửi email xác minh. Phản hồi xác nhận thành công và yêu cầu người dùng kiểm tra email.

Xác minh Email (GET /auth/verify?token=...): Khi người dùng click vào link, Backend tìm kiếm và kiểm tra token. Nếu hợp lệ, token được đánh dấu đã dùng và tài khoản được kích hoạt (user.is_active=True).

2. Luồng Quản lý Phiên (Session)
   Đăng nhập (POST /auth/login): Xác thực mật khẩu và kiểm tra tài khoản đã kích hoạt. Nếu thành công, hệ thống cấp Access Token (JWT, ngắn hạn) và Refresh Token (Opaque Token, dài hạn). JWT được trả trong body JSON, còn Refresh Token được gửi vào HTTP-Only Cookie để tăng cường bảo mật (chống XSS).

Gia hạn (POST /auth/refresh): Backend nhận Refresh Token từ Cookie. Token được kiểm tra tính hợp lệ và trạng thái thu hồi (revoke) trong DB/Redis. Nếu hợp lệ, một Access Token (JWT) mới được cấp.

Đăng xuất (POST /auth/logout): Backend nhận Refresh Token từ Cookie, thực hiện thu hồi (revoke) token đó khỏi DB/Redis (vô hiệu hóa nó ngay lập tức), và yêu cầu trình duyệt xóa Cookie tương ứng.

3. Luồng Khôi phục Tài khoản An toàn
   Yêu cầu Reset Mật khẩu (POST /auth/password-reset-request): Hệ thống nhận email, tạo Reset Token (Opaque, TTL ngắn) và gửi email chứa link đặt lại. Phản hồi phải luôn chung chung ("Nếu tài khoản tồn tại...") để chống dò tìm tài khoản (Username Enumeration).

Đặt lại Mật khẩu (POST /auth/password-reset): Backend nhận Token và Mật khẩu mới. Sau khi kiểm tra Token hợp lệ, hệ thống hash và cập nhật mật khẩu mới. BẮT BUỘC, hệ thống phải Xóa TẤT CẢ Refresh Token hiện tại của người dùng đó khỏi DB/Redis để chấm dứt mọi phiên làm việc cũ.

4. Luồng Phân quyền (RBAC)
   Xác định User (get_current_user Dependency): Lấy JWT từ Header, xác minh, giải mã để lấy ID người dùng, và query DB để lấy đối tượng User cùng danh sách Roles hiện tại.

Kiểm tra Quyền (require_roles Dependency): Dependency này được sử dụng tại các route bảo vệ. Nó so sánh Role của người dùng hiện tại với các Role yêu cầu. Nếu có bất kỳ sự trùng khớp nào, truy cập được cho phép. Ngược lại, trả về 403 Forbidden.
