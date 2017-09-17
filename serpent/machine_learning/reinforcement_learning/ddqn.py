from serpent.machine_learning.reinforcement_learning.dqn import DQN

import numpy as np

from keras.optimizers import Adam

import random


class DDQN(DQN):

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
        model_learning_rate=1e-4,
        override_epsilon=False
    ):
        super().__init__(
            input_shape=input_shape,
            input_mapping=input_mapping,
            replay_memory_size=replay_memory_size,
            batch_size=batch_size,
            action_space=action_space,
            max_steps=max_steps,
            observe_steps=observe_steps,
            initial_epsilon=initial_epsilon,
            final_epsilon=final_epsilon,
            gamma=gamma,
            model_file_path=model_file_path,
            model_learning_rate=model_learning_rate,
            override_epsilon=override_epsilon
        )

        self.type = "DDQN"
        self.model_online = self._initialize_model()

    def calculate_target_error(self, observation):
        previous_target = self.model_online.predict(observation[0])[0][observation[1]]

        if observation[4]:
            target = observation[2]
        else:
            best_action = np.argmax(self.model_online.predict(observation[3]))
            q = self.model.predict(observation[3])[0][best_action]

            target = observation[2] + self.gamma * q

        return np.abs(target - previous_target)

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

            target = self.model_online.predict(previous_frame_stack)
            previous_target = target[0][action_index]

            if terminal:
                target[0][action_index] = reward
            else:
                best_action = np.argmax(self.model_online.predict(frame_stack))
                q = self.model.predict(frame_stack)[0][best_action]

                target[0][action_index] = reward + self.gamma * q

            error = np.abs(target[0][action_index] - previous_target)
            self.replay_memory.update(mini_batch[i][0], error)

            self.model_online.fit(previous_frame_stack, target, epochs=1, verbose=0)

        self.model_loss = 0

    def pick_action(self, action_type=None):
        if action_type is None:
            self.compute_action_type()
        else:
            self.current_action_type = action_type

        qs = self.model_online.predict(self.frame_stack)

        if self.current_action_type == "RANDOM":
            self.current_action_index = random.randrange(self.action_count)
            self.maximum_future_rewards = None
        elif self.current_action_type == "PREDICTED":
            self.current_action_index = np.argmax(qs)
            self.maximum_future_rewards = qs

    def save_model_weights(self, file_path_prefix="datasets/model_", is_checkpoint=False):
        epsilon = self.epsilon_greedy_q_policy.epsilon

        if is_checkpoint:
            file_path = f"{file_path_prefix}_dqn_{self.current_step}_{epsilon}_.h5"
        else:
            file_path = f"{file_path_prefix}_dqn_{epsilon}_.h5"

        self.model_online.save_weights(file_path, overwrite=True)

    def load_model_weights(self, file_path, override_epsilon):
        self.model_online.load_weights(file_path)
        self.model_online.compile(loss="logcosh", optimizer=Adam(lr=self.model_learning_rate, clipvalue=10))

        self.update_target_model()

        *args, steps, epsilon, extension = file_path.split("_")
        self.current_step = int(steps)

        if override_epsilon:
            self.previous_epsilon = float(epsilon)
            self.epsilon_greedy_q_policy.epsilon = float(epsilon)

    def update_target_model(self):
        print("Updating target model...")
        self.model.set_weights(self.model_online.get_weights())
