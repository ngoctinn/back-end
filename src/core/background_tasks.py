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
		logger.info(f"Xóa {deleted_count} token xác minh hết hạn")
		return deleted_count
	except Exception as e:
		logger.error(f"Lỗi khi xóa token xác minh hết hạn: {str(e)}")
		return 0
	finally:
		db.close()


def cleanup_revoked_refresh_tokens():
	"""Xóa refresh tokens đã bị thu hồi cổ hơn 7 ngày.

	Hàm này nên được chạy định kỳ (ví dụ: hàng tuần).
	"""
	db: Session = SessionLocal()
	try:
		deleted_count = crud.cleanup_old_refresh_tokens(db, days=7)
		logger.info(f"Xóa {deleted_count} refresh tokens đã bị thu hồi")
		return deleted_count
	except Exception as e:
		logger.error(f"Lỗi khi xóa refresh tokens: {str(e)}")
		return 0
	finally:
		db.close()


def run_all_cleanup_tasks():
	"""Chạy tất cả background cleanup tasks."""
	logger.info("Bắt đầu chạy cleanup tasks...")
	
	verify_deleted = cleanup_expired_tokens()
	refresh_deleted = cleanup_revoked_refresh_tokens()
	
	logger.info(f"Cleanup tasks hoàn thành. Xóa: {verify_deleted} verify tokens, {refresh_deleted} refresh tokens")
	return {
		"verification_tokens_deleted": verify_deleted,
		"refresh_tokens_deleted": refresh_deleted,
	}
