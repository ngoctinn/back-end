"""Module xử lý gửi email cho hệ thống.

Chứa các hàm để gửi email xác minh đăng ký và đặt lại mật khẩu.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from src.core.config import settings


def _get_verification_email_template(
    user_email: str, token: str, frontend_url: str
) -> str:
    """Tạo HTML template cho email xác minh đăng ký.

    Args:
        user_email: Email người dùng
        token: Token xác minh
        frontend_url: URL frontend để tạo link xác minh

    Returns:
        HTML content của email
    """
    verify_link = f"{frontend_url}/auth/verify-email?token={token}"
    html_content = f"""
    <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .content {{
                    background-color: #ffffff;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .header h2 {{
                    color: #2c3e50;
                    margin: 0;
                }}
                .button {{
                    display: inline-block;
                    background-color: #3498db;
                    color: #ffffff;
                    padding: 12px 30px;
                    border-radius: 5px;
                    text-decoration: none;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 12px;
                    color: #7f8c8d;
                }}
                .expiry-notice {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 10px;
                    margin: 15px 0;
                    border-radius: 3px;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="content">
                    <div class="header">
                        <h2>Xác minh Email của Bạn</h2>
                    </div>

                    <p>Xin chào,</p>
                    <p>Cảm ơn bạn đã đăng ký tài khoản với chúng tôi.
                    Để hoàn tất quá trình đăng ký, vui lòng xác minh
                    địa chỉ email của bạn bằng cách nhấp vào nút dưới đây:</p>

                    <center>
                        <a href="{verify_link}" class="button">Xác minh Email</a>
                    </center>

                    <div class="expiry-notice">
                        <strong>⏱️ Lưu ý:</strong> Link xác minh sẽ hết hạn
                        sau 24 giờ. Nếu bạn không xác minh trong thời gian này,
                        vui lòng yêu cầu gửi lại email.
                    </div>

                    <p>Hoặc sao chép link dưới đây vào trình duyệt:</p>
                    <p style="word-break: break-all; background-color: #f9f9f9;
                    padding: 10px; border-radius: 3px; font-size: 12px;">
                        {verify_link}
                    </p>

                    <p>Nếu bạn không yêu cầu đăng ký, vui lòng bỏ qua email này.</p>

                    <div class="footer">
                        <p>© 2025 Spa Online CRM. Tất cả quyền được bảo lưu.</p>
                        <p>Nếu bạn có thắc mắc, vui lòng liên hệ:
                        <a href="mailto:support@spa-crm.local">support@spa-crm.local</a></p>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """
    return html_content


def _get_password_reset_email_template(
    token: str, frontend_url: str
) -> str:
    """Tạo HTML template cho email đặt lại mật khẩu.

    Args:
        token: Token đặt lại mật khẩu
        frontend_url: URL frontend để tạo link reset

    Returns:
        HTML content của email
    """
    reset_link = f"{frontend_url}/auth/reset-password?token={token}"
    html_content = f"""
    <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .content {{
                    background-color: #ffffff;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .header h2 {{
                    color: #e74c3c;
                    margin: 0;
                }}
                .button {{
                    display: inline-block;
                    background-color: #e74c3c;
                    color: #ffffff;
                    padding: 12px 30px;
                    border-radius: 5px;
                    text-decoration: none;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 12px;
                    color: #7f8c8d;
                }}
                .security-notice {{
                    background-color: #f8d7da;
                    border-left: 4px solid #f5c6cb;
                    padding: 10px;
                    margin: 15px 0;
                    border-radius: 3px;
                    font-size: 14px;
                    color: #721c24;
                }}
                .expiry-notice {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 10px;
                    margin: 15px 0;
                    border-radius: 3px;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="content">
                    <div class="header">
                        <h2>Đặt lại Mật khẩu của Bạn</h2>
                    </div>

                    <p>Xin chào,</p>
                    <p>Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho
                    tài khoản của bạn. Để đặt lại mật khẩu, vui lòng
                    nhấp vào nút dưới đây:</p>

                    <center>
                        <a href="{reset_link}" class="button">Đặt lại Mật khẩu</a>
                    </center>

                    <div class="expiry-notice">
                        <strong>⏱️ Lưu ý:</strong> Link đặt lại mật khẩu
                        sẽ hết hạn sau 1 giờ. Vui lòng thực hiện thay đổi
                        trong thời gian này.
                    </div>

                    <p>Hoặc sao chép link dưới đây vào trình duyệt:</p>
                    <p style="word-break: break-all; background-color: #f9f9f9;
                    padding: 10px; border-radius: 3px; font-size: 12px;">
                        {reset_link}
                    </p>

                    <div class="security-notice">
                        <strong>🔒 Cảnh báo bảo mật:</strong> Nếu bạn không yêu cầu
                        đặt lại mật khẩu, vui lòng bỏ qua email này hoặc thay đổi
                        mật khẩu ngay để bảo vệ tài khoản của bạn.
                    </div>

                    <div class="footer">
                        <p>© 2025 Spa Online CRM. Tất cả quyền được bảo lưu.</p>
                        <p>Nếu bạn có thắc mắc về bảo mật, vui lòng liên hệ:
                        <a href="mailto:security@spa-crm.local">security@spa-crm.local</a></p>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """
    return html_content


def send_email_async(to_email: str, subject: str, html_content: str) -> bool:
    """Gửi email không đồng bộ thông qua SMTP.

    Args:
        to_email: Email người nhận
        subject: Tiêu đề email
        html_content: Nội dung HTML của email

    Returns:
        True nếu gửi thành công, False nếu thất bại
    """
    try:
        # Tạo message MIME
        message = MIMEMultipart("alternative")
        message["From"] = f"{settings.MAIL_USERNAME}"
        message["To"] = to_email
        message["Subject"] = subject

        # Gắn HTML content
        part = MIMEText(html_content, "html")
        message.attach(part)

        # Kết nối SMTP và gửi
        if settings.MAIL_SSL_TLS:
            server = smtplib.SMTP_SSL(settings.MAIL_SERVER, settings.MAIL_PORT)
        else:
            server = smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT)
            if settings.MAIL_STARTTLS:
                server.starttls()

        server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
        server.send_message(message)
        server.quit()

        return True
    except Exception as e:
        # Log lỗi nhưng không expose chi tiết lỗi SMTP
        print(f"Lỗi gửi email: {str(e)}")
        return False


def send_verification_email(email: str, token: str) -> bool:
    """Gửi email xác minh đăng ký.

    Args:
        email: Email người dùng cần xác minh
        token: Token xác minh để tạo link

    Returns:
        True nếu gửi thành công, False nếu thất bại
    """
    subject = "Xác minh Email của Bạn - Spa Online CRM"
    html_content = _get_verification_email_template(
        email, token, settings.FRONTEND_URL
    )
    return send_email_async(email, subject, html_content)


def send_password_reset_email(email: str, token: str) -> bool:
    """Gửi email đặt lại mật khẩu.

    Args:
        email: Email người dùng cần reset mật khẩu
        token: Token đặt lại mật khẩu để tạo link

    Returns:
        True nếu gửi thành công, False nếu thất bại
    """
    subject = "Đặt lại Mật khẩu - Spa Online CRM"
    html_content = _get_password_reset_email_template(token, settings.FRONTEND_URL)
    return send_email_async(email, subject, html_content)
