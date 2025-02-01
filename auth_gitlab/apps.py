from django.apps import AppConfig


class Config(AppConfig):
    name = "sentry.auth.providers.gitlab"

    def ready(self):
        from sentry.auth import register
        from .provider import GitLabOAuth2Provider
        register("gitlab", GitLabOAuth2Provider)