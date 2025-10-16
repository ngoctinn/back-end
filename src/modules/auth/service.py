"""Service layer cho auth module.

DEPRECATED: Module này đã được tách thành auth_service.py và token_service.py.
Tệp này chỉ để đảm bảo backward compatibility.

Vui lòng sử dụng:
- auth_service: cho register, login, logout, refresh token
- token_service: cho email verification, password reset
"""

# Re-export từ các service modules mới cho backward compatibility
from .auth_service import (
	create_access_token_for_user,
	create_refresh_token_value,
	hash_password,
	verify_password,
	register_user,
	login_user,
	refresh_access_token,
	logout_user,
)
from .token_service import (
	create_verification_token_value,
	create_reset_token_value,
	initiate_email_verification,
	confirm_email,
	initiate_password_reset,
	confirm_password_reset,
)

__all__ = [
	"create_access_token_for_user",
	"create_refresh_token_value",
	"hash_password",
	"verify_password",
	"register_user",
	"login_user",
	"refresh_access_token",
	"logout_user",
	"create_verification_token_value",
	"create_reset_token_value",
	"initiate_email_verification",
	"confirm_email",
	"initiate_password_reset",
	"confirm_password_reset",
]
