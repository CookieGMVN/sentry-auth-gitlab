from __future__ import annotations
from django import forms
from django.http import HttpRequest, HttpResponse
from django.http.response import HttpResponseBase
from sentry.auth.services.auth.model import RpcAuthProvider
from sentry.auth.view import AuthView
from sentry.models.authidentity import AuthIdentity
from sentry.organizations.services.organization.model import RpcOrganization
from sentry.plugins.base.response import DeferredResponse
from sentry.utils.forms import set_field_choices

from .client import GitLabClient
from .constants import ERR_NO_GROUP_ACCESS, ERR_NO_EMAIL


class FetchUser(AuthView):
    def __init__(self, group=None, *args, **kwargs):
        self.group = group
        super().__init__(*args, **kwargs)

    def handle(self, request: HttpRequest, helper) -> HttpResponse:
        with GitLabClient(helper.fetch_state("data")["access_token"]) as client:
            if self.group is not None:
                if not client.is_group_member(self.group["id"]):
                    return helper.error(ERR_NO_GROUP_ACCESS)

            user = client.get_user()

            if not user.get("email"):
                return helper.error(ERR_NO_EMAIL)

            helper.bind_state("user", user)
            return helper.next_step()


class ConfirmEmailForm(forms.Form):
    email = forms.EmailField(label="Email")


class ConfirmEmail(AuthView):
    def handle(self, request: HttpRequest, helper) -> HttpResponseBase:
        user = helper.fetch_state("user")

        try:
            auth_identity = AuthIdentity.objects.select_related("user").get(
                auth_provider=helper.provider_model, ident=user["id"]
            )
        except AuthIdentity.DoesNotExist:
            pass
        else:
            user["email"] = auth_identity.user.email

        if user.get("email"):
            return helper.next_step()

        form = ConfirmEmailForm(request.POST or None)
        if form.is_valid():
            user["email"] = form.cleaned_data["email"]
            helper.bind_state("user", user)
            return helper.next_step()

        return self.respond("sentry_auth_gitlab/enter-email.html", {"form": form})


class SelectGroupForm(forms.Form):
    group = forms.ChoiceField(label="Group")

    def __init__(self, group_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        set_field_choices(self.fields["group"], [(g["id"], g["name"]) for g in group_list])


class SelectGroup(AuthView):
    def handle(self, request: HttpRequest, helper) -> HttpResponseBase:
        with GitLabClient(helper.fetch_state("data")["access_token"]) as client:
            group_list = client.get_group_list()

        form = SelectGroupForm(group_list, request.POST or None)
        if form.is_valid():
            group_id = form.cleaned_data["group"]
            group = [g for g in group_list if group_id == str(g["id"])][0]
            helper.bind_state("group", group)
            return helper.next_step()

        return self.respond(
            "sentry_auth_gitlab/select-group.html",
            {"form": form, "group_list": group_list}
        )


def gitlab_configure_view(
    request: HttpRequest,
    organization: RpcOrganization,
    auth_provider: RpcAuthProvider
) -> DeferredResponse:
    return DeferredResponse("sentry_auth_gitlab/configure.html")