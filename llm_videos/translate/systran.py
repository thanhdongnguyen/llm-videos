from . import Translate, make_request_get, make_request_post, make_request_upload, make_provider_error, make_provider_success
from os import environ

class SysTran(Translate):
    def __init__(self):
        super().__init__()
        self.api_key = environ.get("SYSTRAN_API_KEY")
        self.domain = "https://api-translate.systran.net"
        self.headers = {
            "Authorization": f"Key {self.api_key}"
        }

    def translate_text(self, text: str, from_lang: str, to_lang: str):
        endpoint = f"{self.domain}/translation/text/translate"

        try:
            response = make_request_get(
                endpoint,
                params={
                    "source": from_lang,
                    "target": to_lang,
                    "input": text,
                    "encoding": "utf-8",
                },
                headers=self.headers
            )
            resp = response.json()
            if resp["error"]["statusCode"] != 200:
                return make_provider_error(
                    resp["error"]["statusCode"],
                    resp["error"]["message"],
                    resp["request_id"]
                )
            content = "".join([t["output"] for t in resp["outputs"]])

            return make_provider_success(content, resp["request_id"])

        except Exception as e:
            return make_provider_error(500, str(e))


    def translate_file(self, path_file: str, from_lang: str, to_lang: str):
        endpoint = f"{self.domain}/translation/file/translate"

        try:
            response = make_request_upload(
                endpoint,
                file_key="input",
                file_path=path_file,
                additional_data={
                    "source": from_lang,
                    "target": to_lang,
                    "encoding": "utf-8",
                    "async": True,
                },
                headers=self.headers
            )
            resp = response.json()
            if resp["error"]["statusCode"] != 200:
                return make_provider_error(
                    resp["error"]["statusCode"],
                    resp["error"]["message"],
                    resp["request_id"]
                )

            return make_provider_success("", resp["requestId"], status="pending", have_queue=True, queue_id=resp["requestId"])

        except Exception as e:
            return make_provider_error(500, str(e))

    def check_status_file(self, request_id: str):
        endpoint = f"{self.domain}/translation/file/status"

        resp = make_request_get(endpoint, params={"requestId": request_id}, headers=self.headers)
        resp = resp.json()
        return resp["status"]


    def get_file_aysnc(self, request_id: str):

        status = self.check_status_file(request_id)
        if status != "finished":
            return make_provider_success("", request_id, status="pending")

        endpoint = f"{self.domain}/translation/file/result"

        resp = make_request_get(endpoint, params={"requestId": request_id}, headers=self.headers)
        resp = resp.text
        return make_provider_success(resp, request_id, status="success")
