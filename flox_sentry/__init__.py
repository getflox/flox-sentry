from floxcore.command import Stage
from floxcore.context import Flox
from floxcore.plugin import Plugin

from flox_sentry.configure import SentryConfiguration
from flox_sentry.project import create_team, create_project, assing_teams, dump_variables


class SentryPlugin(Plugin):
    def configuration(self):
        return SentryConfiguration()

    def handle_variables(self, flox: Flox):
        return (
            Stage(dump_variables, 1900),
        )

    def handle_project(self, flox: Flox):
        return [
            Stage(create_team, require=["sentry.create_team"]),
            Stage(create_project, 1900),
            Stage(dump_variables, 1900),
            Stage(assing_teams),
        ]

    def configured(self, flox) -> bool:
        return all([flox.settings.sentry.default_team, flox.settings.sentry.organization])


def plugin():
    return SentryPlugin()
