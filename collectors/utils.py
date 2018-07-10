import time


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
