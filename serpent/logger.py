import enum


class Loggers(enum.Enum):
    NOOP = 0
    COMET_ML = 1


class Logger:
    def __init__(self, logger_kwargs=None):
        self.config = logger_kwargs or dict()

    def log_hyperparams(self, hyperparams, step=0):
        raise NotImplementedError()

    def log_metric(self, key, value, step=0):
        raise NotImplementedError()
    