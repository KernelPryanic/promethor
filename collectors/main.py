import argparse
import logger
from prometheus_client import start_http_server

import logging
from lvm_collector import LVM
from sql_queries_collector import SQL


def main():
    try:
        parser = argparse.ArgumentParser()

        parser.add_argument("-c", "--collectors", dest="collectors",
            nargs='+', default=[], choices=["lvm", "sql"],
            help="List of desired collectors to include")
        parser.add_argument("-p", "--port", dest="port",
            default=8000, help="Port of http info server")
        parser.add_argument("-t", "--timeout", dest="timeout",
            default=10, help="Timeout of cleaning. "
                "Live it empty in case of using cron job.")
        parser.add_argument("--loglevel", dest="loglevel",
            default="INFO",
            choices=["CRITICAL", "ERROR", "WARNING",
                "INFO", "DEBUG", "NOTSET"],
            help="Logging level")
        parser.add_argument("-l", "--log", dest="log",
            help="Redirect logging to file")
        parser.add_argument("--sql", dest="sql",
            default="/etc/promethor/sql.yml", help="Path to SQL config")
        args = parser.parse_args()

        if "sql" in args.collectors and args.sql is None:
            parser.error("SQL collector requires --sql")

        global log

        if args.log is not None:
            log = logging.getLogger(__name__)
            log.addHandler(logger.FileHandler(args.log))
            log.setLevel(getattr(logging, args.loglevel))
        else:
            log = logging.getLogger(__name__)
            log.addHandler(logger.StreamHandler())
            log.setLevel(getattr(logging, args.loglevel))

        start_http_server(int(args.port))

        if "lvm" in args.collectors:
            lvm_collector = LVM(int(args.timeout), args.loglevel, args.log)
            lvm_collector.collect()
        if "sql" in args.collectors:
            sql_collector = SQL(args.sql, int(args.timeout), args.loglevel,
                args.log)
            sql_collector.collect()

    except KeyboardInterrupt:
        print('\nThe process was interrupted by the user')
        raise SystemExit

if __name__ == "__main__":
    main()
