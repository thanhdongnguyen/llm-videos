

error_define = {
    403: {
        "en": "Forbidden",
        "vi": "Không được phép truy cập"
    },
    500: {
        "en": "Internal Server Error",
        "vi": "Lỗi máy chủ"
    },
    10: {
        "en": "Email is existed",
        "vi": "Email đã tồn tại"
    },
    11: {
        "en": "Account isn't existed",
        "vi": "Tài khoản không tồn tại"
    },
    12: {
        "en": "Account/Password is incorrect",
        "vi": "Tài khoản/Mật khẩu không chính xác"
    },
    13: {
        "en": "Register successfully",
        "vi": "Đăng ký thành công"
    },
    14: {
        "en": "Login successfully",
        "vi": "Đăng nhập thành công"
    },
    15: {
        "en": "Account isn't existed",
        "vi": "Tài khoản không tồn tại"
    },
    16: {
        "en": "Account is blocked",
        "vi": "Tài khoản bị khóa"
    },
    17: {
        "en": "Parameters Invalid",
        "vi": "Tham số không hợp lệ"
    },
    18: {
        "en": "Info Account Update Invalid",
        "vi": "Thông tin cập nhật tài khoản không hợp lệ"
    },
    19: {
        "en": "Video not found",
        "vi": "Video không tồn tại"
    }


}


def get_error(code: int, lang: str = "vi") -> dict:
    err = error_define[code][lang]

    return {
        "message": err,
        "code": code
    }