from typing import Tuple

from floxcore.config import Configuration, ParamDefinition


class SentryConfiguration(Configuration):
    def parameters(self) -> Tuple[ParamDefinition, ...]:
        return (
            ParamDefinition("url", "URL to sentry", default="https://sentry.io/"),
            ParamDefinition("organization", "Sentry default organization"),
            ParamDefinition("default_team", "Default team which should be used for new projects (must exists)"),
            ParamDefinition("create_team", "Create a new team per project", boolean=True),
            ParamDefinition("assign_teams", "Grant permission to teams", multi=True, default=""),
        )

    def secrets(self) -> Tuple[ParamDefinition, ...]:
        return (
            ParamDefinition("token", "Sentry Access Token", secret=True),
        )

    def schema(self):
        pass
