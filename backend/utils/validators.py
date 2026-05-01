import re

def validate_username(username):
    if not username or len(username) < 3 or len(username) > 20:
        return False, "Tên đăng nhập phải có 3-20 ký tự"

    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Tên đăng nhập chỉ chứa chữ, số và gạch dưới"

    return True, ""

def validate_email(email):
    if not email:
        return False, "Email không được để trống"

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Email không hợp lệ"

    return True, ""

def validate_password(password):
    if not password or len(password) < 6:
        return False, "Mật khẩu phải có ít nhất 6 ký tự"

    return True, ""