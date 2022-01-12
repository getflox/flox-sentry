from floxcore.context import Flox

from flox_sentry.sentry import with_sentry, Sentry, SentryException, DuplicatedException


@with_sentry
def create_team(flox: Flox, sentry: Sentry, out, **kwargs):
    """Create sentry teams"""
    team = flox.name
    try:
        sentry.create_team(team)
        out.success(f'Team "{team}" created')
    except DuplicatedException as e:
        out.info(e)
    except SentryException as e:
        out.error(e)


@with_sentry
def create_project(flox: Flox, sentry: Sentry, out, **kwargs):
    """Create sentry project"""
    try:
        sentry.create_project(flox.id, flox.name, flox.settings.sentry.default_team)
        out.success(f'Project "{flox.id}" created')
    except DuplicatedException as e:
        out.info(e)
    except SentryException as e:
        out.error(e)
        return {}

    key = {}
    try:
        key = sentry.create_key(flox.id, "flox")
    except DuplicatedException as e:
        out.info(e)
    except SentryException as e:
        out.error(e)
        return {}


@with_sentry
def dump_variables(flox: Flox, sentry: Sentry, out, **kwargs):
    try:
        key = next(filter(lambda x: x["name"] == "flox", sentry.get_key(flox.id, "flox")), None)

        return dict(
            dsn=key.get("dsn", {}).get("public")
        )
    except SentryException as e:
        out.error(e)
        return {}

    return dict()


@with_sentry
def assing_teams(flox: Flox, sentry: Sentry, out, **kwargs):
    """Assign project to the teams"""
    sentry.get_project(flox.id)

    teams = []
    for team in flox.settings.sentry.assign_teams:
        try:
            team = sentry.get_team(flox.id, team)
            teams.append(dict(id=team.get("id"), name=team.get("name"), slug=team.get("slug")))
        except Exception:
            out.warning(f"Unable to find '{team}' team, skipping")

    sentry.update_project(
        flox.id,
        flox.settings.sentry.default_team,
        dict(teams=teams)
    )
    teams_str = ", ".join(flox.settings.sentry.assign_teams)

    out.success(f"Assigned {teams_str} teams to {flox.id} project")
