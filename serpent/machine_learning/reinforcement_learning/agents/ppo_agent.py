from serpent.machine_learning.reinforcement_learning.agent import Agent

from serpent.game_frame import GameFrame
from serpent.game_frame_buffer import GameFrameBuffer

from serpent.enums import InputControlTypes

from serpent.logger import Loggers

from serpent.utilities import SerpentError

import os
import enum
import copy
import json

import numpy as np

try:
    import torch

    from serpent.machine_learning.reinforcement_learning.ppo.policy import Policy
    from serpent.machine_learning.reinforcement_learning.ppo.ppo import PPO
    from serpent.machine_learning.reinforcement_learning.ppo.rollout_storage import RolloutStorage
except ImportError:
    raise SerpentError("Setup has not been been performed for the ML module. Please run 'serpent setup ml'")


class PPOAgentModes(enum.Enum):
    OBSERVE = 0
    TRAIN = 1
    EVALUATE = 2


class PPOAgent(Agent):

    def __init__(
        self,
        name,
        game_inputs=None,
        callbacks=None,
        seed=420133769,
        input_shape=None,
        ppo_kwargs=None,
        logger=Loggers.NOOP,
        logger_kwargs=None
    ):
        super().__init__(
            name, 
            game_inputs=game_inputs, 
            callbacks=callbacks, 
            seed=seed,
            logger=logger,
            logger_kwargs=logger_kwargs
        )

        if len(game_inputs) > 1:
            raise SerpentError("PPOAgent only supports a single axis of game inputs.")

        if game_inputs[0]["control_type"] != InputControlTypes.DISCRETE:
            raise SerpentError("PPOAgent only supports discrete input spaces")

        if torch.cuda.is_available():
            self.device = torch.device("cuda")

            torch.set_default_tensor_type("torch.cuda.FloatTensor")
            torch.backends.cudnn.benchmark = True

            torch.cuda.manual_seed_all(seed)
        else:
            self.device = torch.device("cpu")
            torch.set_num_threads(1)

        torch.manual_seed(seed)

        agent_kwargs = dict(
            is_recurrent=False,
            surrogate_objective_clip=0.2,
            epochs=4,
            batch_size=32,
            value_loss_coefficient=0.5,
            entropy_regularization_coefficient=0.01,
            learning_rate=0.0001,
            adam_epsilon=0.00001,
            epsilon=0.3,
            memory_capacity=1024,
            discount=0.99,
            gae=False,
            gae_tau=0.95,
            save_steps=10000,
            model=f"datasets/ppo_{self.name}.pth",
            seed=seed
        )

        if isinstance(ppo_kwargs, dict):
            for key, value in ppo_kwargs.items():
                if key in agent_kwargs:
                    agent_kwargs[key] = value

        self.discount = agent_kwargs["discount"]
        
        self.gae = agent_kwargs["gae"]
        self.gae_tau = agent_kwargs["gae_tau"]

        input_shape = (4, input_shape[0], input_shape[1]) # 4x Grayscale OR Quantized

        self.actor_critic = Policy(input_shape, len(self.game_inputs[0]["inputs"]), agent_kwargs["is_recurrent"])

        if torch.cuda.is_available():
            self.actor_critic.cuda(device=self.device)

        self.agent = PPO(
            self.actor_critic,
            agent_kwargs["surrogate_objective_clip"],
            agent_kwargs["epochs"],
            agent_kwargs["batch_size"],
            agent_kwargs["value_loss_coefficient"],
            agent_kwargs["entropy_regularization_coefficient"],
            lr=agent_kwargs["learning_rate"],
            eps=agent_kwargs["adam_epsilon"],
            max_grad_norm=agent_kwargs["epsilon"]
        )

        self.storage = RolloutStorage(
            agent_kwargs["memory_capacity"],
            1,
            input_shape,
            len(self.game_inputs[0]["inputs"]),
            self.actor_critic.state_size
        )

        if torch.cuda.is_available():
            self.storage.cuda(device=self.device)

        self.current_episode = 1
        self.current_step = 0

        self.mode = PPOAgentModes.TRAIN
        
        self.save_steps = agent_kwargs["save_steps"]

        self.model_path = agent_kwargs["model"]

        if os.path.isfile(self.model_path):
            self.restore_model()

        self.logger.log_hyperparams(agent_kwargs)

    def generate_actions(self, state, **kwargs):
        frames = list()

        for game_frame in state.frames:
            frames.append(torch.tensor(torch.from_numpy(game_frame.frame), dtype=torch.float32))

        self.current_state = torch.stack(frames, 0)
        self.current_state = self.current_state[None, :]

        with torch.no_grad():
            self.current_value, self.current_action, self.current_action_log_prob, self.current_states = self.actor_critic.act(
                self.current_state, 
                self.storage.states[self.storage.step], 
                self.storage.masks[self.storage.step]
            )

        actions = list()

        label = self.game_inputs_mappings[0][int(self.current_action[0])]
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

        if self.callbacks.get("before_observe") is not None:
            self.callbacks["before_observe"]()

        rewards = torch.from_numpy(np.expand_dims(np.stack([reward]), 1)).float()
        masks = torch.tensor([0.0] if terminal else [1.0], dtype=torch.float32)

        self.current_state *= masks[0]

        self.storage.insert(
            self.current_state, 
            self.current_states, 
            self.current_action, 
            self.current_action_log_prob, 
            self.current_value, 
            rewards,
            masks
        )

        if terminal:
            self.current_episode += 1

        self.current_step += 1

        if self.storage.step == (self.storage.num_steps - 1):
            if self.callbacks.get("before_update") is not None:
                self.callbacks["before_update"]()

            with torch.no_grad():
                next_value = self.actor_critic.get_value(self.storage.observations[-1], self.storage.states[-1], self.storage.masks[-1]).detach()

            self.storage.compute_returns(next_value, self.gae, self.discount, self.gae_tau)

            value_loss, action_loss, entropy = self.agent.update(self.storage)
            self.analytics_client.track(event_key="PPO_INTERNALS", data={"value_loss": value_loss, "action_loss": action_loss, "entropy": entropy})
            
            self.logger.log_metric("entropy", entropy, step=self.current_step)
            self.logger.log_metric("value_loss", value_loss, step=self.current_step)
            self.logger.log_metric("action_loss", action_loss, step=self.current_step)

            self.storage.after_update()

            if self.callbacks.get("after_update") is not None:
                self.callbacks["after_update"]()

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

        if terminal:
            self.analytics_client.track(event_key="TOTAL_REWARD", data={"reward": self.cumulative_reward})
            self.logger.log_metric("episode_rewards", self.cumulative_reward, step=self.current_step)

        if self.callbacks.get("after_observe") is not None:
            self.callbacks["after_observe"]()


    def save_model(self):
        model = self.actor_critic
        
        if torch.cuda.is_available():
            model = copy.deepcopy(self.actor_critic).cpu()

        torch.save(model, self.model_path)

        with open(self.model_path.replace(".pth", ".json"), "w") as f:
            data = {
                "current_episode": self.current_episode,
                "current_step": self.current_step
            }

            f.write(json.dumps(data))

    def restore_model(self):
        if not os.path.isfile(self.model_path):
            return

        self.actor_critic = torch.load(self.model_path)

        if torch.cuda.is_available():
            self.actor_critic = self.actor_critic.cuda(device=self.device)

        file_path = self.model_path.replace(".pth", ".json")

        if os.path.isfile(file_path):
            with open(file_path, "r") as f:
                data = json.loads(f.read())

            self.current_episode = data["current_episode"]
            self.current_step = data["current_step"]

        self.emit_persisted_events()
