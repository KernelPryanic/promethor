import logger
import pymongo
from prometheus_client import Gauge
import traceback
import yaml

import logging
import utils


class Mongo(object):
    def __init__(self, mongo_config_path, timeout=None,
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

        with open(mongo_config_path) as mongo_config:
            try:
                config = yaml.load(mongo_config)
            except:
                raise Exception("Can't parse Mongo config!")

        self.config = config
        connection_string = "mongodb://{}:{}@{}/{}".format(
            config["connection"]["user"], config["connection"]["password"],
            config["connection"]["addr"], config["connection"]["auth_db"])
        if config["connection"]["params"]:
            connection_string += "?{}".format(config["connection"]["params"])
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client["admin"]
        self.timeout = timeout
        self.rs_status = Gauge("mongo_rs_status",
            "Mongo replica set status", ["host"])

    @utils.loop
    def collect(self):
        try:
            for el in self.db.command("replSetGetStatus")["members"]:
                self.rs_status.labels(el["name"]).set(el["health"])
        except:
            log.error("Something wrong with Mongo rs status\n{}".
                format(traceback.format_exc()))
