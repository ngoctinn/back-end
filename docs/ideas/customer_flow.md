Refining the Flow

I'm honing in on the customer flow. My focus is crafting a clear, Markdown-formatted description. This will address the "Lazy Registration" issue and other solutions for the identified problems. I'm exploring various customer journey stages to build a coherent story.

Crafting the Structure

The markdown document's structure is coming together nicely. I'm focusing on defining core components: User and Customer. I am building out the flows: Walk-in, Lazy Registration, and Account Linking. Now I'm working on the detailed steps, making sure all customer journeys are included. I'm building it from the customer journey, with clear, step-by-step instructions.

Developing the Structure

I'm solidifying the overall structure of the Markdown document. Now, I'm focusing on outlining the core components, which are User and Customer. The goal is to build out detailed flows for Walk-in, Lazy Registration, and Account Linking. Now I'm working on detailing each step within the journeys, ensuring all possible customer scenarios are included. I'm taking a customer-centric approach, building step-by-step instructions.

Chắc chắn rồi. Đây là bản mô tả chi tiết và hoàn chỉnh nhất về các luồng quản lý khách hàng trong hệ thống của bạn, được trình bày dưới dạng Markdown.

Phân Tích Chi Tiết Luồng Quản Lý Khách Hàng (Customer Journey)
Tài liệu này mô tả chi tiết các kịch bản và quy trình xử lý cho mọi đối tượng khách hàng trong hệ thống Spa CRM, dựa trên kiến trúc tách biệt giữa Định danh (User) và Hồ sơ (Customer).

🧬 Nguyên Tắc Thiết Kế Cốt Lõi
Bảng Customer: Là "Hồ sơ CRM", nguồn chân lý duy nhất cho thông tin nghiệp vụ (tên, SĐT, lịch sử điều trị). Được định danh chính qua phone_number. Bảng này chứa tất cả mọi người từng tương tác với spa.

Bảng User: Là "Chìa khóa Đăng nhập", chỉ chịu trách nhiệm xác thực (email, mật khẩu). Một record ở đây đại diện cho một tài khoản có khả năng truy cập hệ thống online.

🌊 Các Luồng Khách Hàng Chi Tiết
Hệ thống sẽ xử lý 3 luồng chính sau đây một cách mượt mà.

Luồng 1: Khách Hàng Vãng Lai (Walk-in)
Đây là kịch bản đơn giản nhất, xảy ra hoàn toàn tại quầy spa.

Bối cảnh: Một khách hàng mới, chị An, lần đầu đến spa hoặc gọi điện để đặt lịch. Chị không có nhu cầu sử dụng hệ thống online.

Hành động của Lễ tân:

Mở chức năng "Thêm Khách Hàng Mới" hoặc "Tìm Kiếm Khách Hàng".

Nhập SĐT của chị An. Hệ thống không tìm thấy SĐT này.

Lễ tân điền thông tin cơ bản: Họ và Tên (full_name) và Số Điện Thoại (phone_number).

Xử lý của Backend:

Hệ thống nhận yêu cầu tạo mới.

Tạo một record duy nhất trong bảng Customer.

Giá trị user_id trong record này được để là NULL.

Bảng User hoàn toàn không bị ảnh hưởng.

Kết quả:

Chị An có một hồ sơ CRM trong hệ thống.

Mọi lịch hẹn, ghi chú điều trị sau này của chị sẽ được liên kết với customer.id này.

Luồng 2: Khách Hàng Mới Đăng Ký Online (Luồng Nhanh Gọn)
Luồng này ưu tiên trải nghiệm người dùng, giảm thiểu rào cản khi tạo tài khoản.

Bối cảnh: Anh Bình muốn tạo tài khoản trên website của spa để xem các dịch vụ. Anh chưa muốn cung cấp SĐT ngay lập tức.

Bước 2a: Đăng ký Tối giản ("Lazy Registration")
Hành động của Người dùng:

Truy cập trang "Đăng ký".

Chỉ cần nhập 2 thông tin: Email và Mật khẩu.

Xử lý của Backend (trong một Transaction):

Tạo Định danh: Tạo một record mới trong bảng User với email và password_hash. is_active được đặt là False.

Tạo Hồ sơ "Chờ": Tạo một record mới trong bảng Customer. Record này là một "hồ sơ chờ" (stub profile), chỉ chứa một thông tin duy nhất là user_id trỏ đến user.id vừa tạo. Các trường full_name và phone_number đều là NULL.

Kích hoạt: Gửi email xác thực đến địa chỉ email của anh Bình.

Kết quả:

Anh Bình có một tài khoản User và một hồ sơ Customer liên kết nhưng chưa có thông tin CRM.

Sau khi xác thực email, anh có thể đăng nhập, xem các thông tin chung của spa.

Bước 2b: Bổ Sung Thông Tin Khi Cần Thiết
Bối cảnh: Sau khi đăng nhập, anh Bình quyết định đặt lịch hẹn đầu tiên.

Hành động của Hệ thống:

Khi anh Bình vào trang đặt lịch, hệ thống kiểm tra hồ sơ Customer liên kết với tài khoản của anh.

Phát hiện full_name và phone_number đang là NULL.

Hiển thị một form yêu cầu: "Để hoàn tất đặt lịch, vui lòng cung cấp Họ Tên và Số Điện Thoại để chúng tôi tiện liên lạc."

Xử lý của Backend:

Nhận thông tin full_name và phone_number.

UPDATE record Customer tương ứng với user_id của anh Bình, điền vào các trường còn thiếu.

Kết quả:

Hồ sơ CRM của anh Bình được hoàn thiện.

Anh có thể tiếp tục quá trình đặt lịch hẹn.

Luồng 3: Khách Hàng Cũ Tạo Tài Khoản Online & Liên Kết
Đây là luồng quan trọng nhất để đảm bảo tính toàn vẹn dữ liệu và trải nghiệm khách hàng thân thiết.

Bối cảnh: Chị Chi đã là khách hàng vãng lai của spa từ lâu. Toàn bộ lịch sử điều trị của chị đã được lưu trong một hồ sơ Customer (có full_name, phone_number nhưng user_id là NULL). Hôm nay, chị quyết định tạo tài khoản online.

Bước 3a: Đăng ký như Người dùng Mới
Hành động của Chị Chi: Chị thực hiện y hệt Luồng 2a. Chị đăng ký tài khoản bằng email của mình.

Kết quả tạm thời: Hệ thống tạo ra một cặp User và Customer "chờ" hoàn toàn mới cho chị Chi. Tại thời điểm này, hệ thống chưa biết tài khoản online này và hồ sơ CRM cũ là của cùng một người.

Bước 3b: Kích hoạt Luồng "Liên Kết Dữ Liệu"
Hành động của Hệ thống:

Sau khi chị Chi đăng nhập, trên trang quản lý tài khoản, hệ thống hiển thị một khu vực nổi bật.

Thông điệp: "Bạn là khách hàng thân thiết của chúng tôi? Liên kết ngay để xem lại toàn bộ lịch sử điều trị và nhận các ưu đãi đặc biệt!"

Bước 3c: Xác Minh & Hợp Nhất
Hành động của Chị Chi:

Chị bấm vào nút "Liên kết".

Hệ thống yêu cầu chị nhập Số Điện Thoại chị đã dùng tại spa.

Xử lý của Backend:

Backend nhận SĐT và tìm kiếm trong bảng Customer một record thỏa mãn 2 điều kiện: phone_number khớp VÀ user_id IS NULL.

Nếu tìm thấy, hệ thống gửi một mã OTP (One-Time Password) đến SĐT đó để xác minh.

Hành động của Chị Chi: Chị nhập mã OTP vừa nhận được.

Bước 3d: Hoàn Tất Hợp Nhất
Xử lý của Backend (trong một Transaction):

Khi OTP được xác thực thành công.

Bước 1 - Tìm đối tượng:

Lấy user_id của tài khoản đang đăng nhập (tài khoản mới của chị Chi).

Xác định "hồ sơ chờ" (Customer rỗng) liên kết với user_id này.

Xác định "hồ sơ cũ" (Customer đầy đủ) được tìm thấy qua SĐT.

Bước 2 - Hợp nhất:

Cập nhật "hồ sơ cũ": UPDATE Customer SET user_id = [user_id của chị Chi] WHERE phone_number = ...

Bước 3 - Dọn dẹp:

Xóa "hồ sơ chờ" để tránh dư thừa dữ liệu: DELETE FROM Customer WHERE id = [id của hồ sơ chờ].

Kết quả cuối cùng:

Tài khoản User của chị Chi giờ đã được liên kết với hồ sơ Customer chứa toàn bộ lịch sử của chị.

Dữ liệu được hợp nhất, không bị trùng lặp, không mất mát. Chị Chi đăng nhập vào và thấy toàn bộ quá trình điều trị của mình.
