from functools import wraps
from typing import Dict

import requests
from requests import Session, HTTPError
from requests_toolbelt.sessions import BaseUrlSession
from slugify import slugify


def http_client(api_url: str, token: str, version: int = 0):
    if not api_url.endswith("/"):
        api_url = api_url + "/"

    api_url = api_url + f"api/{version}/"

    s = BaseUrlSession(api_url)
    s.headers.update({"Authorization": f"Bearer {token}"})
    s.headers.update({"content-type": "application/json"})

    return s


class SentryException(Exception):
    pass


class DuplicatedException(SentryException):
    pass


class Sentry:
    """
    Abstraction for https://docs.sentry.io/api/
    """

    def __init__(self, client: Session, organization: str):
        self.http_client = client
        self.organization = organization

    def create_project(self, project_id: str, project_name: str, team_slug: str) -> None:
        r = self.http_client.post(f"teams/{self.organization}/{team_slug}/projects/",
                                  json={"name": project_name, "slug": project_id})

        if r.status_code == requests.codes.conflict:
            raise DuplicatedException(f'Project "{project_name}" already exists')

        try:
            r.raise_for_status()
        except HTTPError as e:
            raise SentryException(e)

        return r.json()

    def create_key(self, project_id: str, name: str) -> None:
        r = self.http_client.post(f"projects/{self.organization}/{project_id}/keys/",
                                  json={"name": name})

        if r.status_code == requests.codes.conflict:
            raise DuplicatedException(f'Key "{name}" already exists')

        try:
            r.raise_for_status()
        except HTTPError as e:
            raise SentryException(e)

        return r.json()

    def get_key(self, project_id: str, name: str) -> None:
        r = self.http_client.get(f"projects/{self.organization}/{project_id}/keys/")

        try:
            r.raise_for_status()
        except HTTPError as e:
            raise SentryException(e)

        return r.json()

    def create_team(self, team: str) -> None:
        r = self.http_client.post(f"organizations/{self.organization}/teams/",
                                  json={"name": team, "slug": slugify(team)})
        if r.status_code == requests.codes.conflict:
            raise DuplicatedException(f'Team "{team}" already exists')

        try:
            r.raise_for_status()
        except HTTPError as e:
            raise SentryException(e)

    def get_project(self, project: str) -> Dict:
        r = self.http_client.get(f"projects/{self.organization}/{project}/")

        try:
            r.raise_for_status()
        except HTTPError as e:
            raise SentryException(e)

        return r.json()

    def update_project(self, project, team, data) -> Dict:
        r = self.http_client.post(f"projects/{self.organization}/{project}/teams/{team}/",
                                  json=data)

        try:
            r.raise_for_status()
        except HTTPError as e:
            raise SentryException(e)

        return r.json()

    def get_team(self, organisation: str, team_slug) -> Dict:
        r = self.http_client.get(f"teams/{self.organization}/{team_slug}/")

        try:
            r.raise_for_status()
        except HTTPError as e:
            raise SentryException(e)
    
        return r.json()


def with_sentry(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        flox = kwargs.get("flox")

        client = http_client(flox.settings.sentry.url, flox.secrets.getone("sentry_token", required=True))
        sentry = Sentry(client, flox.settings.sentry.organization)
        kwargs["sentry"] = sentry

        return f(*args, **kwargs)

    return wrapper
