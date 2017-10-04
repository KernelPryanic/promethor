import os
import re
import logging


class StreamHandler(logging.StreamHandler):

    def __init__(self):
        logging.StreamHandler.__init__(self)
        fmt = '%(asctime)s %(filename)s %(levelname)s: %(message)s'
        fmt_date = '%Y-%m-%dT%T%Z'
        formatter = logging.Formatter(fmt, fmt_date)
        self.setFormatter(formatter)


class FileHandler(logging.FileHandler):

    def __init__(self, path):
        abspath = os.path.abspath(path)
        abspath_dir = re.search("^.+\/", abspath).group(0)
        if not os.path.exists(abspath_dir):
            os.makedirs(abspath_dir)
        if os.path.isdir(abspath):
            abspath = os.path.join(abspath, re.sub("py", "log", __file__))
        logging.FileHandler.__init__(self, abspath)
        fmt = '%(asctime)s %(filename)s %(levelname)s: %(message)s'
        fmt_date = '%Y-%m-%dT%T%Z'
        formatter = logging.Formatter(fmt, fmt_date)
        self.setFormatter(formatter)
