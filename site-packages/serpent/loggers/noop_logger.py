from serpent.logger import Logger


class NoopLogger(Logger):
    
    def __init__(self, logger_kwargs=None):
        super().__init__(logger_kwargs=logger_kwargs)

    def log_hyperparams(self, hyperparams, step=0):
        pass

    def log_metric(self, key, value, step=0):
        pass
