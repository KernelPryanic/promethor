import logger
import pymysql
from prometheus_client import Gauge
import traceback
import yaml

import logging
import utils


class SQL(object):
    def __init__(self, sql_config_path, timeout=None,
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

        with open(sql_config_path) as sql_config:
            try:
                config = yaml.load(sql_config)
            except:
                raise Exception("Can't parse SQL config!")

        self.config = config
        self.connection = pymysql.connect(
            host=config["connection"]["host"],
            user=config["connection"]["user"],
            password=config["connection"]["password"],
            db=config["connection"]["db"],
            charset=config["connection"]["charset"]
        )
        self.timeout = timeout
        self.sql_pending = Gauge("sql_pending",
            "SQL pending queries", ["host"])

    @utils.loop
    def collect(self):
        try:
            with self.connection.cursor() as cursor:
                sql = '''SELECT COUNT(`id`)
                    FROM `PROCESSLIST`
                    WHERE `INFO` is not NULL
                    AND `time` >= {}
                '''.format(self.config["metrics"]["pending_threshold"])
                cursor.execute(sql)
                result = cursor.fetchone()
                self.sql_pending.labels(self.connection.host).set(result[0])
        except:
            log.error("Something wrong with SQL data collection\n{}".
                format(traceback.format_exc()))
