from floxcore import Plugin

from flox_sentry.project import create_alerts, create_project


class SentryPlugin(Plugin):
    def __init__(self) -> None:
        super().__init__(help="Setup Sentry for your project")

        self.project_stages.add(callback=create_project, priority=10000)
        self.project_stages.add(callback=create_alerts, priority=20000)


plugin = SentryPlugin()
