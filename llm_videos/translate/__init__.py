import requests

def make_request_get(url, params=None, headers=None):
    response = requests.get(url, params=params, headers=headers)
    return response

def make_request_post(url, data=None, headers=None):
    headers["Content-Type"] = "application/json"
    response = requests.post(url, data=data, headers=headers)
    return response

def make_request_upload(url, file_path, file_key='file', additional_data=None, headers=None):
    files = {file_key: open(file_path, 'rb')}
    data = additional_data if additional_data is not None else {}

    response = requests.post(url, files=files, data=data, headers=headers)

    files[file_key].close()
    return response


def make_provider_success(message: str, request_id=None, status: str = "pending", have_queue: bool=False, queue_id: str = "") -> dict:
    return {
        "success": True,
        "message": message,
        "status": status,
        "request_id": request_id,
        "have_queue": have_queue,
        "queue_id": queue_id,
    }

def make_provider_error(statusCode: int, message: str, request_id=None) -> dict:
    return {
        "success": False,
        "code": statusCode,
        "message": message,
        "request_id": request_id,
    }


class Translate:
    def __init__(self):
        pass

    def translate_text(self):
        pass

    def translate_file(self):
        pass

    def get_file_async(self):
        pass