"""Các background tasks định kỳ cho hệ thống.

Chứa các hàm cần chạy định kỳ như xóa token hết hạn, cleanup cache, v.v.
"""

import logging
from datetime import datetime

from sqlalchemy.orm import Session

from src.core.db import SessionLocal
from src.modules.auth import crud


logger = logging.getLogger(__name__)


def cleanup_expired_tokens():
	"""Xóa tất cả token xác minh hết hạn.

	Hàm này nên được chạy định kỳ (ví dụ: mỗi giờ, mỗi ngày).
	Có thể sử dụng APScheduler, Celery, hoặc task scheduler khác.
	"""
	db: Session = SessionLocal()
	try:
		deleted_count = crud.delete_expired_tokens(db)
		logger.info(f"Xóa {deleted_count} token hết hạn")
		return deleted_count
	except Exception as e:
		logger.error(f"Lỗi khi xóa token hết hạn: {str(e)}")
		return 0
	finally:
		db.close()
