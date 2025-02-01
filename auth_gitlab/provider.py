from __future__ import annotations
from collections.abc import Callable
from django.http.request import HttpRequest
from sentry.auth.exceptions import IdentityNotValid
from sentry.auth.providers.oauth2 import OAuth2Callback, OAuth2Login, OAuth2Provider
from sentry.auth.services.auth.model import RpcAuthProvider
from sentry.organizations.services.organization.model import RpcOrganization
from sentry.plugins.base.response import DeferredResponse

from .client import GitLabApiError, GitLabClient
from .constants import (
    ACCESS_TOKEN_URL,
    AUTHORIZE_URL,
    CLIENT_ID,
    CLIENT_SECRET,
    SCOPE,
)
from .views import ConfirmEmail, FetchUser, SelectGroup, gitlab_configure_view


class GitLabOAuth2Provider(OAuth2Provider):
    access_token_url = ACCESS_TOKEN_URL
    authorize_url = AUTHORIZE_URL
    name = "GitLab"

    def get_client_id(self):
        return CLIENT_ID

    def get_client_secret(self):
        return CLIENT_SECRET

    def __init__(self, group=None, **config):
        super().__init__(**config)
        self.group = group

    def get_configure_view(
        self,
    ) -> Callable[[HttpRequest, RpcOrganization, RpcAuthProvider], DeferredResponse]:
        return gitlab_configure_view

    def get_auth_pipeline(self):
        return [
            OAuth2Login(
                authorize_url=self.authorize_url,
                client_id=self.get_client_id(),
                scope=SCOPE
            ),
            OAuth2Callback(
                access_token_url=self.access_token_url,
                client_id=self.get_client_id(),
                client_secret=self.get_client_secret(),
            ),
            FetchUser(group=self.group),
            ConfirmEmail(),
        ]

    def get_setup_pipeline(self):
        pipeline = self.get_auth_pipeline()
        pipeline.append(SelectGroup())
        return pipeline

    def get_refresh_token_url(self):
        return ACCESS_TOKEN_URL

    def build_config(self, state):
        return {"group": {"id": state["group"]["id"], "name": state["group"]["name"]}}

    def build_identity(self, state):
        data = state["data"]
        user_data = state["user"]
        return {
            "id": user_data["id"],
            "email": user_data["email"],
            "name": user_data["name"],
            "data": self.get_oauth_data(data),
        }

    def refresh_identity(self, auth_identity):
        with GitLabClient(auth_identity.data["access_token"]) as client:
            try:
                if not client.is_group_member(self.group["id"]):
                    raise IdentityNotValid
            except GitLabApiError as e:
                raise IdentityNotValid(e)