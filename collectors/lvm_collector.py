import logger
import lvm
from prometheus_client import Gauge
import re
import traceback
import time

import logging


def loop(func):
    def wrapper(self, *args, **kwargs):
        if self.timeout is not None:
            while True:
                func(self, *args, **kwargs)
                time.sleep(self.timeout)
        else:
            func(self, *args, **kwargs)
        return
    return wrapper


class LVM(object):
    def __init__(self, timeout=None, loglevel=None, filelog=None):
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
        self.metric = Gauge("lvm", "LVM data in percentages", ["lv", "vg"])

    @loop
    def collect(self):
        try:
            vg_names = lvm.listVgNames()
            for vg_name in vg_names:
                vg = lvm.vgOpen(vg_name, 'r')
                lvs = vg.listLVs()
                for lv in lvs:
                    self.metric.labels(lv.getName(), vg_name).set(
                        lv.getProperty("data_percent")[0] / 1000000.0)
                vg.close()
        except:
            log.error("Something wrong with lvm data collection\n{}".
                format(traceback.format_exc()))
