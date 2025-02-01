import orjson
from requests.exceptions import RequestException
from sentry import http
from .constants import API_DOMAIN


class GitLabApiError(Exception):
    def __init__(self, message="", status=0):
        super().__init__(message)
        self.status = status


class GitLabClient:
    def __init__(self, access_token):
        self.http = http.build_session()
        self.access_token = access_token

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.http.close()

    def _request(self, path):
        headers = {"Authorization": f"Bearer {self.access_token}"}

        try:
            req = self.http.get(
                f"https://{API_DOMAIN}/{path.lstrip('/')}",
                headers=headers,
            )
        except RequestException as e:
            raise GitLabApiError(f"{e}", status=getattr(e, "status_code", 0))
        if req.status_code < 200 or req.status_code >= 300:
            raise GitLabApiError(req.content, status=req.status_code)
        return orjson.loads(req.content)

    def get_group_list(self):
        return self._request("/api/v4/groups")

    def get_user(self):
        return self._request("/api/v4/user")

    def is_group_member(self, group_id):
        group_id = str(group_id)
        for g in self.get_group_list():
            if str(g["id"]) == group_id:
                return True
        return False