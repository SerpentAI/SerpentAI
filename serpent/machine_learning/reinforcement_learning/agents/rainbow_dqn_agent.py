from serpent.machine_learning.reinforcement_learning.agent import Agent

from serpent.game_frame import GameFrame
from serpent.game_frame_buffer import GameFrameBuffer

from serpent.enums import InputControlTypes

from serpent.utilities import SerpentError

import os
import enum
import random

import numpy as np

try:
    import torch

    from serpent.machine_learning.reinforcement_learning.rainbow_dqn.rainbow_agent import RainbowAgent
    from serpent.machine_learning.reinforcement_learning.rainbow_dqn.replay_memory import ReplayMemory
except ImportError:
    raise SerpentError("Setup has not been been performed for the ML module. Please run 'serpent setup ml'")


class RainbowDQNAgentModes(enum.Enum):
    OBSERVE = 0
    TRAIN = 1


class RainbowDQNAgent(Agent):

    def __init__(
        self,
        name,
        game_inputs=None,
        callbacks=None,
        rainbow_kwargs=None
    ):
        super().__init__(name, game_inputs=game_inputs, callbacks=callbacks)

        if len(game_inputs) > 1:
            raise SerpentError("RainbowDQNAgent only supports a single axis of game inputs.")

        if game_inputs[0]["control_type"] != InputControlTypes.DISCRETE:
            raise SerpentError("RainbowDQNAgent only supports discrete input spaces")

        if torch.cuda.is_available():
            self.device = torch.device("cuda")

            torch.set_default_tensor_type("torch.cuda.FloatTensor")
            torch.backends.cudnn.benchmark = True
        else:
            self.device = torch.device("cpu")

        agent_kwargs = dict(
            replay_memory_capacity=100000,
            history=4,
            discount=0.99,
            multi_step=3,
            priority_weight=0.4,
            priority_exponent=0.5,
            quantile=True,
            quantiles=200,
            atoms=51,
            v_min=-10,
            v_max=10,
            batch_size=32,
            hidden_size=512,
            noisy_std=0.1,
            learning_rate=0.0000625,
            adam_epsilon=1.5e-4,
            target_update=5000,
            save_steps=5000,
            observe_steps=20000,
            max_steps=50000000,
            model=f"datasets/rainbow_dqn_{self.name}.pth"
        )

        if isinstance(rainbow_kwargs, dict):
            for key, value in rainbow_kwargs.items():
                if key in agent_kwargs:
                    agent_kwargs[key] = value

        self.agent = RainbowAgent(
            len(self.game_inputs[0]["inputs"]),
            self.device,
            quantile=agent_kwargs["quantile"],
            quantiles=agent_kwargs["quantiles"],
            atoms=agent_kwargs["atoms"],
            v_min=agent_kwargs["v_min"],
            v_max=agent_kwargs["v_max"],
            batch_size=agent_kwargs["batch_size"],
            multi_step=agent_kwargs["multi_step"],
            discount=agent_kwargs["discount"],
            history=agent_kwargs["history"],
            hidden_size=agent_kwargs["hidden_size"],
            noisy_std=agent_kwargs["noisy_std"],
            learning_rate=agent_kwargs["learning_rate"],
            adam_epsilon=agent_kwargs["adam_epsilon"],
            model=agent_kwargs["model"]
        )

        self.replay_memory = ReplayMemory(
            agent_kwargs["replay_memory_capacity"],
            self.device,
            history=agent_kwargs["history"],
            discount=agent_kwargs["discount"],
            multi_step=agent_kwargs["multi_step"],
            priority_weight=agent_kwargs["priority_weight"],
            priority_exponent=agent_kwargs["priority_exponent"]
        )

        self.priority_weight_increase = (1 - agent_kwargs["priority_weight"]) / (agent_kwargs["max_steps"] - agent_kwargs["observe_steps"])

        self.target_update = agent_kwargs["target_update"]

        self.save_steps = agent_kwargs["save_steps"]
        self.observe_steps = agent_kwargs["observe_steps"]
        self.max_steps = agent_kwargs["max_steps"]

        self.set_mode(RainbowDQNAgentModes.OBSERVE)

        self.current_episode = 1
        self.current_step = 0

        self.current_action = -1

        self.model = agent_kwargs["model"]

    def generate_actions(self, state, **kwargs):
        frames = list()

        for game_frame in state.frames:
            frames.append(torch.tensor(torch.from_numpy(game_frame.frame), dtype=torch.float32))

        self.current_state = torch.stack(frames, 0)

        if self.mode == RainbowDQNAgentModes.OBSERVE:
            self.current_action = random.randint(0, len(self.game_inputs[0]["inputs"]) - 1)
        else:
            self.current_action = self.agent.act(self.current_state)

        actions = list()

        label = self.game_inputs_mappings[0][self.current_action]
        action = self.game_inputs[0]["inputs"][label]

        actions.append((label, action, None))

        for action in actions:
            self.analytics_client.track(
                event_key="AGENT_ACTION",
                data={
                    "label": action[0],
                    "action": [str(a) for a in action[1]],
                    "input_value": action[2]
                }
            )

        return actions

    def observe(self, reward=0, terminal=False, **kwargs):
        if self.current_state is None:
            return None

        if self.callbacks.get("before_observe") is not None and self.mode == RainbowDQNAgentModes.TRAIN:
            self.callbacks["before_observe"]()

        self.agent.reset_noise()

        if self.mode == RainbowDQNAgentModes.OBSERVE:
            self.analytics_client.track(event_key="AGENT_MODE", data={"mode": f"Observing - {self.observe_steps - self.current_step} Steps Remaining"})

            self.replay_memory.append(self.current_state, self.current_action, reward, terminal)
            self.current_step += 1

            if self.current_step >= self.observe_steps:
                self.current_step = 0
                self.set_mode(RainbowDQNAgentModes.TRAIN)

        elif self.mode == RainbowDQNAgentModes.TRAIN:
            if terminal:
                self.current_episode += 1

            self.replay_memory.append(self.current_state, self.current_action, reward, terminal)
            self.current_step += 1

            self.replay_memory.priority_weight = min(self.replay_memory.priority_weight + self.priority_weight_increase, 1)

            self.agent.learn(self.replay_memory)

            if self.current_step % self.target_update == 0:
                self.agent.update_target_net()

            if self.current_step % self.save_steps == 0:
                if self.callbacks.get("before_update") is not None:
                    self.callbacks["before_update"]()

                self.save_model()

                if self.callbacks.get("after_update") is not None:
                    self.callbacks["after_update"]()

        self.current_state = None

        self.current_reward = reward
        self.cumulative_reward += reward

        self.analytics_client.track(event_key="REWARD", data={"reward": self.current_reward, "total_reward": self.cumulative_reward})

        if terminal and self.mode == RainbowDQNAgentModes.TRAIN:
            self.analytics_client.track(event_key="TOTAL_REWARD", data={"reward": self.cumulative_reward})

        if self.callbacks.get("after_observe") is not None and self.mode == RainbowDQNAgentModes.TRAIN:
            self.callbacks["after_observe"]()

    def set_mode(self, rainbow_dqn_mode):
        self.mode = rainbow_dqn_mode

        if self.mode == RainbowDQNAgentModes.OBSERVE:
            self.agent.train()
            self.analytics_client.track(event_key="AGENT_MODE", data={"mode": f"Observing - {self.observe_steps - self.current_step} Steps Remaining"})
        elif self.mode == RainbowDQNAgentModes.TRAIN:
            self.agent.train()
            self.analytics_client.track(event_key="AGENT_MODE", data={"mode": "Training"})

    def save_model(self):
        self.agent.save(self.model)
