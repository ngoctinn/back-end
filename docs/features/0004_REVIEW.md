# ĐÁNH GIÁ CODE: MODULE QUẢN LÝ HÌNH ẢNH (MEDIA)

## TỔNG QUAN

Nhìn chung, module `media` đã được triển khai bám sát theo kế hoạch kỹ thuật (`0004_PLAN.md`). Cấu trúc module, các endpoint, model và schema đều được xây dựng tốt, rõ ràng và tuân thủ các quy ước của dự án.

Tuy nhiên, có một số vấn đề nghiêm trọng ở tầng data access (CRUD) và một vài điểm thiếu sót trong logic nghiệp vụ (service) cần được khắc phục để đảm bảo tính toàn vẹn dữ liệu và sự ổn định.

---

## 1. Đối Chiếu Với Kế Hoạch (Plan vs. Implementation)

### ✅ **Triển khai Tốt**

- **Cấu trúc:** Cấu trúc thư mục `src/modules/media` với các file `router.py`, `service.py`, `crud.py`, `models.py`, `schemas.py` hoàn toàn khớp với kế hoạch.
- **Model (`MediaFile`):** Model được định nghĩa chính xác với đầy đủ các trường, kiểu dữ liệu, và các ràng buộc (`unique`, `index`) như kế hoạch.
- **Router:** Các endpoints được định nghĩa đúng với các phương thức HTTP, đường dẫn, và response model. Việc sử dụng `summary` và docstring rất tốt.
- **Schemas:** `MediaResponse` và `MediaListResponse` được triển khai đúng. Việc bổ sung `DeleteMessageResponse` là một cải tiến tốt so với kế hoạch (thay vì trả về `dict` đơn thuần).

### ⚠️ **Điểm Khác Biệt So Với Kế Hoạch**

- **`MediaUploadRequest` không được sử dụng:** Kế hoạch đề cập đến schema `MediaUploadRequest`, nhưng trong thực tế, router nhận trực tiếp `UploadFile`. Đây là một cách tiếp cận phổ biến và hoàn toàn chấp nhận được trong FastAPI, không phải là lỗi.

---

## 2. Lỗi và Vấn Đề Cần Sửa (Bugs & Issues)

### 🔴 **[CRITICAL] CRUD Functions Tự Commit Transaction**

- **Vấn đề:** Các hàm trong `src/modules/media/crud.py` (`create_media_record`, `delete_media_record`) tự gọi `session.commit()`. Điều này vi phạm nguyên tắc phân tách trách nhiệm và phá vỡ tính toàn vẹn của transaction. Logic nghiệp vụ ở tầng `service` phải là nơi duy nhất quyết định khi nào commit hoặc rollback một transaction.
- **Ví dụ:** Trong `service.delete_media_file`, nếu `delete_file_from_storage` (xóa file trên Supabase) thất bại, transaction sẽ không thể rollback được vì `delete_media_record` đã commit thay đổi vào DB ngay lập tức.
- **Hướng khắc phục:**
  1.  Xóa tất cả các dòng `session.commit()` khỏi file `src/modules/media/crud.py`.
  2.  Trong `service.py`, hãy gọi `session.commit()` sau khi tất cả các thao tác (cả DB và storage) đã thành công. Hàm `delete_media_file` đã có `session.rollback()` trong `except`, điều này sẽ hoạt động đúng khi `crud.py` không tự commit.

### 🟡 **[HIGH] Bỏ Sót Validation Quan Trọng**

- **Vấn đề 1:** Hàm `upload_image_for_service` trong `service.py` không kiểm tra xem `service_id` có tồn tại trong CSDL hay không trước khi tải ảnh lên. Điều này không nhất quán với `upload_avatar_for_customer` (có kiểm tra customer) và có thể tạo ra dữ liệu rác.
- **Vấn đề 2:** Kế hoạch yêu cầu kiểm tra kích thước file (`MAX_FILE_SIZE`), nhưng logic này chưa được triển khai trong hàm `_validate_image_file`.
- **Hướng khắc phục:**
  1.  Trong `upload_image_for_service`, thêm logic để truy vấn và xác thực sự tồn tại của `Service` tương tự như cách làm với `Customer`.
  2.  Trong `_validate_image_file`, thêm đoạn kiểm tra `file.size`:
      ```python
      # Thêm vào hàm _validate_image_file trong service.py
      if file.size > MAX_FILE_SIZE:
          raise HTTPException(
              status_code=413, # Payload Too Large
              detail=f"Kích thước file quá lớn. Tối đa: {MAX_FILE_SIZE // 1024 // 1024}MB"
          )
      ```

### 🟠 **[MEDIUM] Cấu Hình Hardcode**

- **Vấn đề:** Các hằng số `ALLOWED_IMAGE_TYPES` và `MAX_FILE_SIZE` đang được định nghĩa (hardcode) trực tiếp trong `src/modules/media/service.py`. Kế hoạch đã chỉ định `MAX_FILE_SIZE` nên nằm trong `src/core/config.py` để quản lý tập trung.
- **Hướng khắc phục:**
  1.  Di chuyển `MAX_FILE_SIZE` vào lớp `Settings` trong `src/core/config.py`.
  2.  Import `settings` từ `src.core.config` vào `service.py` và sử dụng `settings.MAX_FILE_SIZE`.
  3.  `ALLOWED_IMAGE_TYPES` có thể giữ lại ở `service.py` vì nó ít có khả năng thay đổi, nhưng việc đưa ra config cũng là một lựa chọn tốt.

---

## 3. Tái Cấu Trúc và Tối Ưu Hóa (Refactoring & Optimization)

### 💡 **[REFACTOR] Lặp Lại Logic Mapping Model -> Schema (DRY)**

- **Vấn đề:** Logic chuyển đổi từ object model `MediaFile` sang schema `MediaResponse` bị lặp lại ở 3 nơi: `upload_avatar_for_customer`, `upload_image_for_service`, và `get_media_for_entity`. Điều này vi phạm nguyên tắc DRY (Don't Repeat Yourself).
- **Hướng khắc phục:** Tạo một hàm helper hoặc sử dụng Pydantic `model_validate` để thực hiện việc chuyển đổi.
  **Cách 1: Dùng helper function (khuyến nghị)**
  ```python
  # Thêm hàm này vào service.py hoặc schemas.py
  def map_media_model_to_response(media: MediaFile) -> MediaResponse:
      """Chuyển đổi MediaFile model sang MediaResponse schema."""
      return MediaResponse(
          id=media.id,
          file_path=media.file_path,
          public_url=media.public_url,
          file_type=media.file_type,
          file_size=media.file_size,
          related_entity_type=media.related_entity_type,
          related_entity_id=media.related_entity_id,
          created_at=media.created_at,
      )

  # Sử dụng trong service.py
  # return map_media_model_to_response(media)
  ```
  **Cách 2: Dùng Pydantic `model_validate`**
  Trong `schemas.py`, `MediaResponse` có thể được cấu hình để tạo từ ORM model.
  ```python
  class MediaResponse(BaseModel):
      # ... các trường ...
      class Config:
          orm_mode = True # hoặc from_attributes = True cho Pydantic v2

  # Sử dụng trong service.py
  # return MediaResponse.from_orm(media)
  ```

### 💡 **[IMPROVEMENT] Tự Động Cập Nhật `updated_at`**

- **Vấn đề:** Model `MediaFile` có trường `updated_at`, nhưng không có logic nào tự động cập nhật trường này khi record thay đổi.
- **Hướng khắc phục:** SQLModel/SQLAlchemy không tự động cập nhật trường này như một số framework khác. Để triển khai, có thể sử dụng `sqlalchemy.event` để lắng nghe sự kiện "before_update" và cập nhật giá trị. Tuy nhiên, với nhu cầu hiện tại của module (chủ yếu là tạo và xóa), đây là một cải tiến có thể xem xét sau.

---

## 4. Phong Cách và Quy Ước (Style & Conventions)

- **Điểm cộng:** Code tuân thủ rất tốt các quy ước của dự án.
  - **PEP 8:** Code được định dạng sạch sẽ, đúng chuẩn.
  - **Tiếng Việt:** Docstring và comment tiếng Việt rõ ràng, có ý nghĩa, giúp người đọc dễ hiểu mục đích của code.
  - **Typing:** Sử dụng type hints đầy đủ và chính xác.

---

## KẾT LUẬN

Module `media` có nền tảng tốt nhưng chưa sẵn sàng để sử dụng.

**Ưu tiên hàng đầu là phải sửa lỗi `CRITICAL` về việc `crud.py` tự commit transaction.** Sau đó, cần bổ sung các validation còn thiếu để đảm bảo hệ thống hoạt động ổn định và an toàn. Cuối cùng, áp dụng các đề xuất tái cấu trúc (DRY) sẽ giúp code base sạch sẽ và dễ bảo trì hơn trong tương lai.
