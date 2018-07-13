### -- Authored by: gkuznets --- ###

import logging
import traceback

from datetime import datetime, timedelta

import dateutil.parser
import requests
import yaml

from prometheus_client import Gauge

import logger
import utils


class TokenAuth(requests.auth.AuthBase):
    def __init__(self, auth_token):
        self._auth_str = "Bearer " + auth_token

    def __call__(self, r):
        r.headers["Authorization"] = self._auth_str
        return r


class Metric(object):
    def __init__(self, name, organization, project, horizon):
        self._organization = organization
        self._project = project
        self._horizon = timedelta(seconds=horizon)
        self._name = name
        self._gauge = Gauge("sentry_events",
            "Number if errors for {}/{} from Sentry during last {} sec.".
            format(organization, project, horizon), ["project", "name"])

    @staticmethod
    def _count_events(events, younger_than):
        count = 0
        for event in events:
            date_received = dateutil.parser.parse(
                event["dateReceived"]).replace(tzinfo=None)
            if date_received > younger_than.replace(tzinfo=None):
                count += 1
            else:
                break
        return count

    @staticmethod
    def _next_page_url(link_header):
        parts = [part.strip() for part in link_header.split(";")]
        try:
            rel_next_pos = parts.index('rel="next"')
            return parts[rel_next_pos - 1].split(" ")[1][1:-1]
        except ValueError:
            return None

    def update(self, api_token, base_api_url):
        cut_off_time = datetime.utcnow() - self._horizon
        total_events_count = 0
        request_url = base_api_url + "projects/{}/{}/events/".format(
            self._organization, self._project)
        auth = TokenAuth(api_token)
        while request_url:
            response = requests.get(request_url, auth=auth)
            if response.status_code != 200:
                log.error("Request to Sentry API ({}) failed: {}".format(
                    request_url, response.text))
                return
            events = response.json()
            relevant_events_count = self._count_events(events,
                younger_than=cut_off_time)
            total_events_count += relevant_events_count
            if total_events_count < len(events):
                break

            request_url = self._next_page_url(response.headers["Link"])

        self._gauge.labels(self._project, self._name).set(total_events_count)


class SentryEvents(object):
    def __init__(self, config_path, timeout=None,
                 loglevel=None, filelog=None):
        global log

        if "log" not in globals():
            if filelog is not None:
                log = logging.getLogger(__name__)
                log.addHandler(logger.FileHandler(filelog))
                log.setLevel(getattr(logging, loglevel))
            else:
                log = logging.getLogger(__name__)
                log.addHandler(logger.StreamHandler())
                log.setLevel(getattr(logging, loglevel))

        self.timeout = timeout

        with open(config_path) as config_file:
            try:
                self.config = yaml.load(config_file)
            except:
                raise Exception("Can't parse Sentry config!")

        self._api_token = self.config["api_token"]
        self._base_api_url = self.config["base_api_url"]
        self._metrics = [Metric(m["name"], m["organization"],
                                m["project"], m["horizon"])
            for m in self.config["metrics"]]

    @utils.loop
    def collect(self):
        try:
            for metric in self._metrics:
                metric.update(self._api_token, self._base_api_url)
        except:
            log.error("Something wrong with Sentry events collection\n{}".
                format(traceback.format_exc()))
