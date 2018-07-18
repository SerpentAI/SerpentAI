import torch

from .cnn_base import CNNBase
from .distributions import Categorical


class Policy(torch.nn.Module):
    def __init__(self, observation_shape, action_space, recurrent_policy):
        super().__init__()

        # Image input only for now...
        self.base = CNNBase(observation_shape[0], recurrent_policy)

        # Discrete space only for now...
        self.distribution =  Categorical(self.base.output_size, action_space)
        self.state_size = self.base.state_size

    def forward(self, inputs, states, masks):
        raise NotImplementedError

    def act(self, inputs, states, masks, deterministic=False):
        value, actor_features, states = self.base(inputs, states, masks)
        distribution = self.distribution(actor_features)

        if deterministic:
            action = distribution.mode()
        else:
            action = distribution.sample()

        action_log_probs = distribution.log_probs(action)

        return value, action, action_log_probs, states

    def get_value(self, inputs, states, masks):
        value, _, _ = self.base(inputs, states, masks)
        return value

    def evaluate_actions(self, inputs, states, masks, action):
        value, actor_features, states = self.base(inputs, states, masks)
        distribution = self.distribution(actor_features)

        action_log_probs = distribution.log_probs(action)
        distribution_entropy = distribution.entropy().mean()

        return value, action_log_probs, distribution_entropy, states
