from django.conf import settings

CLIENT_ID = settings.GITLAB_APP_ID
CLIENT_SECRET = settings.GITLAB_API_SECRET
REQUIRE_VERIFIED_EMAIL = settings.GITLAB_REQUIRE_VERIFIED_EMAIL

ERR_NO_GROUP_ACCESS = "You do not have access to the required GitLab group."
ERR_NO_EMAIL = "We were unable to find an email address associated with your GitLab account."

SCOPE = "read_user read_api"

BASE_DOMAIN = settings.GITLAB_BASE_DOMAIN
API_DOMAIN = settings.GITLAB_API_DOMAIN

ACCESS_TOKEN_URL = f"https://{BASE_DOMAIN}/oauth/token"
AUTHORIZE_URL = f"https://{BASE_DOMAIN}/oauth/authorize"