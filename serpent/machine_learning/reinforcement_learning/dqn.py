from serpent.input_controller import InputController
from serpent.machine_learning.reinforcement_learning.replay_memory import ReplayMemory
from serpent.machine_learning.reinforcement_learning.epsilon_greedy_q_policy import EpsilonGreedyQPolicy

from serpent.visual_debugger.visual_debugger import VisualDebugger

from keras.models import Model, Sequential
from keras.layers import Dense, Activation, Flatten, Convolution2D, MaxPooling2D, AveragePooling2D, Input, merge
from keras.optimizers import Adam, rmsprop

import numpy as np

import random
import itertools

from termcolor import cprint


class DQN:

    def __init__(
        self,
        input_shape=None,
        input_mapping=None,
        replay_memory_size=10000,
        batch_size=32,
        action_space=None,
        max_steps=1000000,
        observe_steps=None,
        initial_epsilon=1.0,
        final_epsilon=0.1,
        gamma=0.99,
        model_file_path=None,
        model_learning_rate=2.5e-4,
        override_epsilon=False
    ):
        self.type = "DQN"
        self.input_shape = input_shape
        self.replay_memory = ReplayMemory(memory_size=replay_memory_size)
        self.batch_size = batch_size
        self.action_space = action_space
        self.action_count = len(self.action_space.combinations)
        self.action_input_mapping = self._generate_action_space_combination_input_mapping(input_mapping)
        self.frame_stack = None
        self.max_steps = max_steps
        self.observe_steps = observe_steps or (0.1 * replay_memory_size)
        self.current_observe_step = 0
        self.current_step = 0
        self.initial_epsilon = initial_epsilon
        self.final_epsilon = final_epsilon
        self.previous_epsilon = initial_epsilon
        self.epsilon_greedy_q_policy = EpsilonGreedyQPolicy(
            initial_epsilon=self.initial_epsilon,
            final_epsilon=self.final_epsilon,
            max_steps=self.max_steps
        )
        self.gamma = gamma
        self.current_action = None
        self.current_action_index = None
        self.current_action_type = None
        self.first_run = True
        self.mode = "OBSERVE"

        self.model_learning_rate = model_learning_rate
        self.model = self._initialize_model()

        if model_file_path is not None:
            self.load_model_weights(model_file_path, override_epsilon)

        self.model_loss = 0

        self.visual_debugger = VisualDebugger()

    def enter_train_mode(self):
        if self.previous_epsilon is not None:
            self.epsilon_greedy_q_policy.epsilon = self.previous_epsilon
            self.previous_epsilon = None

        self.mode = "TRAIN"

    def enter_run_mode(self):
        self.previous_epsilon = self.epsilon_greedy_q_policy.epsilon
        self.epsilon_greedy_q_policy.epsilon = 0.01
        self.mode = "RUN"

    def next_step(self):
        if self.mode == "TRAIN":
            self.current_step += 1
        elif self.mode == "OBSERVE":
            self.current_observe_step += 1

        if self.mode == "OBSERVE" and self.current_observe_step >= self.observe_steps:
            self.mode = "TRAIN"

    def build_frame_stack(self, game_frame):
        frame_stack = np.stack((
            game_frame,
            game_frame,
            game_frame,
            game_frame
        ), axis=2)

        self.frame_stack = frame_stack.reshape((1,) + frame_stack.shape)

    def update_frame_stack(self, game_frame_buffer):
        game_frames = [game_frame.eighth_resolution_grayscale_frame for game_frame in game_frame_buffer.frames]
        frame_stack = np.stack(game_frames, axis=2)

        self.frame_stack = frame_stack.reshape((1,) + frame_stack.shape)

    def append_to_replay_memory(self, game_frame_buffer, reward, terminal=False):
        previous_frame_stack = self.frame_stack
        self.update_frame_stack(game_frame_buffer)

        observation = [
            previous_frame_stack,
            self.current_action_index,
            reward,
            self.frame_stack,
            terminal
        ]

        self.replay_memory.add(self.calculate_target_error(observation), observation)

    def calculate_target_error(self, observation):
        previous_target = self.model.predict(observation[0])[0][observation[1]]

        if observation[4]:
            target = observation[2]
        else:
            target = observation[2] + self.gamma * np.max(self.model.predict(observation[3]))

        return np.abs(target - previous_target)

    def pick_action(self, action_type=None):
        if action_type is None:
            self.compute_action_type()
        else:
            self.current_action_type = action_type

        qs = self.model.predict(self.frame_stack)

        if self.current_action_type == "RANDOM":
            self.current_action_index = random.randrange(self.action_count)
            self.maximum_future_rewards = None
        elif self.current_action_type == "PREDICTED":
            self.current_action_index = np.argmax(qs)
            self.maximum_future_rewards = qs

    def compute_action_type(self):
        use_random = self.epsilon_greedy_q_policy.use_random()
        self.current_action_type = "RANDOM" if use_random else "PREDICTED"

    def erode_epsilon(self, factor=1):
        if self.mode == "TRAIN":
            self.epsilon_greedy_q_policy.erode(factor=factor)

    def generate_mini_batch(self):
        if self.mode == "OBSERVE":
            return None

        return self.replay_memory.sample(self.batch_size)

    def train_on_mini_batch(self):
        mini_batch = self.generate_mini_batch()

        flashback_indices = random.sample(range(self.batch_size), 6)

        for i in range(0, len(mini_batch)):
            if i in flashback_indices:
                flashback_image = np.squeeze(mini_batch[i][1][3][:, :, :, 1])

                self.visual_debugger.store_image_data(
                    np.array(flashback_image * 255, dtype="uint8"),
                    flashback_image.shape,
                    f"flashback_{flashback_indices.index(i) + 1}"
                )

                del flashback_image

            previous_frame_stack = mini_batch[i][1][0]
            action_index = mini_batch[i][1][1]
            reward = mini_batch[i][1][2]
            frame_stack = mini_batch[i][1][3]
            terminal = mini_batch[i][1][4]

            target = self.model.predict(previous_frame_stack)
            previous_target = target[action_index]

            projected_future_rewards = self.model.predict(frame_stack)

            if terminal:
                target[action_index] = reward
            else:
                target[action_index] = reward + self.gamma * np.max(projected_future_rewards)

            error = np.abs(target[action_index] - previous_target)
            self.replay_memory.update(mini_batch[i][0], error)

            self.model.fit(previous_frame_stack, target, epochs=1, verbose=0)

    def generate_action(self):
        self.current_action = self.action_space.combinations[self.current_action_index]

    def get_action_for_index(self, action_index):
        return [action_input.upper() for action_input in self.action_input_mapping[self.action_space.combinations[action_index]]]

    def get_input_values(self):
        return self.action_input_mapping[self.current_action]

    def save_model_weights(self, file_path_prefix="datasets/model_", is_checkpoint=False):
        epsilon = self.epsilon_greedy_q_policy.epsilon

        if is_checkpoint:
            file_path = f"{file_path_prefix}_dqn_{self.current_step}_{epsilon}_.h5"
        else:
            file_path = f"{file_path_prefix}_dqn_{epsilon}_.h5"

        self.model.save_weights(file_path, overwrite=True)

    def load_model_weights(self, file_path, override_epsilon):
        self.model.load_weights(file_path)
        self.model.compile(loss="logcosh", optimizer=Adam(lr=self.model_learning_rate, clipvalue=10))

        *args, steps, epsilon, extension = file_path.split("_")
        self.current_step = int(steps)

        if override_epsilon:
            self.previous_epsilon = float(epsilon)
            self.epsilon_greedy_q_policy.epsilon = float(epsilon)

    def output_step_data(self):
        if self.mode in ["TRAIN", "OBSERVE"]:
            print(f"CURRENT MODE: {self.mode}")
        else:
            cprint(f"CURRENT MODE: {self.mode}", "grey", "on_yellow", attrs=["dark"])

        print(f"CURRENT STEP: {self.current_step}")

        if self.mode == "OBSERVE":
            print(f"CURRENT OBSERVE STEP: {self.current_observe_step}")
            print(f"OBSERVE STEPS: {self.observe_steps}")

        print(f"CURRENT EPSILON: {round(self.epsilon_greedy_q_policy.epsilon, 6)}")
        print(f"CURRENT RANDOM ACTION PROBABILITY: {round(self.epsilon_greedy_q_policy.epsilon * 100.0, 2)}%")
        print(f"LOSS: {self.model_loss}")

    def _initialize_model(self):
        input_layer = Input(shape=self.input_shape)

        tower_1 = Convolution2D(16, 1, 1, border_mode="same", activation="elu")(input_layer)
        tower_1 = Convolution2D(16, 3, 3, border_mode="same", activation="elu")(tower_1)

        tower_2 = Convolution2D(16, 1, 1, border_mode="same", activation="elu")(input_layer)
        tower_2 = Convolution2D(16, 3, 3, border_mode="same", activation="elu")(tower_2)
        tower_2 = Convolution2D(16, 3, 3, border_mode="same", activation="elu")(tower_2)

        tower_3 = MaxPooling2D((3, 3), strides=(1, 1), border_mode="same")(input_layer)
        tower_3 = Convolution2D(16, 1, 1, border_mode="same", activation="elu")(tower_3)

        merged_layer = merge([tower_1, tower_2, tower_3], mode="concat", concat_axis=1)

        output = AveragePooling2D((7, 7), strides=(8, 8))(merged_layer)
        output = Flatten()(output)
        output = Dense(self.action_count)(output)

        model = Model(input=input_layer, output=output)
        model.compile(rmsprop(lr=self.model_learning_rate, clipvalue=1), "mse")

        return model

    def _generate_action_space_combination_input_mapping(self, input_mapping):
        action_input_mapping = dict()

        for combination in self.action_space.combinations:
            combination_values = self.action_space.values_for_combination(combination)
            input_values = [input_mapping[combination_value] for combination_value in combination_values if combination_value is not None]

            action_input_mapping[combination] = list(itertools.chain.from_iterable(input_values))

        return action_input_mapping
