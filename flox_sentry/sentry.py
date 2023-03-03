from functools import wraps

from sentry_api.api import SentryApi


def with_sentry(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        flox = kwargs.get("flox")

        kwargs["sentry"] = SentryApi(
            organization_slug=flox.profile.sentry.organization, endpoint_url=flox.profile.sentry.url
        )

        return f(*args, **kwargs)

    return wrapper
