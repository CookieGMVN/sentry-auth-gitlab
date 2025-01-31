from typing import Any, Dict, Optional
from requests.exceptions import RequestException
from sentry import http
from sentry.utils import json
from .constants import API_ENDPOINT

class GitLabApiError(Exception):
    def __init__(self, message: str = "", status: int = 0):
        super().__init__(message)
        self.status = status

class GitLabClient:
    def __init__(self, access_token: str):
        self.http = http.build_session()
        self.access_token = access_token

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.http.close()

    def _request(
        self, 
        path: str, 
        method: str = "GET", 
        params: Optional[Dict[str, Any]] = None, 
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to the GitLab API.
        
        Args:
            path: API endpoint path
            method: HTTP method (GET, POST, etc.)
            params: URL parameters
            data: Request body data
            
        Returns:
            Parsed JSON response
            
        Raises:
            GitLabApiError: If the request fails or returns an error status
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }

        url = f"{API_ENDPOINT}/{path.lstrip('/')}"

        try:
            req = self.http.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data if data else None,
                timeout=30,
            )
        except RequestException as e:
            raise GitLabApiError(f"Request failed: {e}", status=getattr(e, "status_code", 0))

        if req.status_code < 200 or req.status_code >= 300:
            raise GitLabApiError(
                f"GitLab API request failed: {req.content}", 
                status=req.status_code
            )

        return json.loads(req.content)

    def get_user(self) -> Dict[str, Any]:
        """
        Get information about the authenticated user.
        
        Returns:
            User information dictionary
        """
        return self._request("/user")

    def get_group(self, group_id: int) -> Dict[str, Any]:
        """
        Get information about a specific group.
        
        Args:
            group_id: GitLab group ID
            
        Returns:
            Group information dictionary
        """
        return self._request(f"/groups/{group_id}")

    def is_group_member(self, group_id: int) -> bool:
        """
        Check if the authenticated user is a member of the specified group.
        
        Args:
            group_id: GitLab group ID
            
        Returns:
            True if user is a member, False otherwise
        """
        try:
            # First check if the user can access the group
            group = self.get_group(group_id)
            
            # Then verify membership by checking the members list
            members = self._request(f"/groups/{group_id}/members/all")
            user_info = self.get_user()
            
            return any(member["id"] == user_info["id"] for member in members)
        except GitLabApiError as e:
            if e.status == 404:
                return False
            raise

    def get_group_members(self, group_id: int) -> list[Dict[str, Any]]:
        """
        Get all members of a specific group.
        
        Args:
            group_id: GitLab group ID
            
        Returns:
            List of group members
        """
        return self._request(f"/groups/{group_id}/members/all")

    def get_user_groups(self) -> list[Dict[str, Any]]:
        """
        Get all groups that the authenticated user is a member of.
        
        Returns:
            List of groups
        """
        return self._request("/groups", params={"min_access_level": 10})  # 10 = Guest access
