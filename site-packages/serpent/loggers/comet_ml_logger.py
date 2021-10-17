from serpent.logger import Logger

from comet_ml import Experiment

import inspect


class CometMLLogger(Logger):
    
    def __init__(self, logger_kwargs=None):
        super().__init__(logger_kwargs=logger_kwargs)

        self.experiment = Experiment(
            api_key=self.config["api_key"], 
            project_name=self.config["project_name"],
            log_code=False,
            log_graph=False,
            auto_param_logging=False,
            auto_metric_logging=False,
            auto_output_logging=None,
            log_env_details=False,
            log_git_metadata=False
        )
        
        if "reward_func" in self.config:
            self.experiment.set_code(inspect.getsource(self.config["reward_func"]))

    def log_hyperparams(self, hyperparams, step=0):
        self.experiment.log_multiple_params(hyperparams, step=step)

    def log_metric(self, key, value, step=0):
        self.experiment.log_metric(key, value, step=step)
