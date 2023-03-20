from floxcore import FloxContext
from sentry_api.api import SentryApi

from flox_sentry.sentry import with_sentry


@with_sentry
def create_project(flox: FloxContext, sentry: SentryApi, output, **kwargs):
    """Create sentry project"""
    output.info("Creating/Updating sentry project")

    sentry.projects.upsert(
        project_slug=flox.project.id,
        team_slug=flox.profile.sentry.team.slug,
        project=dict(
            name=flox.project.name,
            slug=flox.project.id,
            default_rules=False if flox.profile.sentry.rules else True,
            resolveAge=flox.profile.sentry.get("autoResolve", None),  # Value in hours
        ),
    )


@with_sentry
def create_alerts(flox: FloxContext, sentry: SentryApi, output, **kwargs):
    """Create sentry rules"""
    if not flox.profile.sentry.rules:
        return
    output.info("Creating/Updating sentry alert rules")

    existing_rules = sentry.project_rules.all(project_slug=flox.project.id).json()
    for rule in flox.profile.sentry.rules:
        rule_name = rule.get("name").replace("{project_id}", flox.project.id)
        rule["name"] = rule_name

        rule_exists = next(
            iter(filter(lambda existing_rule: existing_rule.get("name") == rule_name, existing_rules)), None
        )
        if not rule_exists:
            sentry.project_rules.create(project_slug=flox.project.id, rule=rule)
        else:
            sentry.project_rules.update(project_slug=flox.project.id, rule_id=rule_exists.get("id"), rule=rule)
