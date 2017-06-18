import numpy as np
import random

import collections


class ReplayMemory:
    def __init__(self, memory_size=5000):
        self.memory_size = memory_size
        self.memory = np.empty(self.memory_size, dtype="object")

        self.index = 0

    def update(self, observation):
        self.memory[self.index % self.memory_size] = observation
        self.index += 1

    def sample(self, quantity):
        item_indices = np.random.choice(min(self.memory_size, self.index), quantity)
        return [self.memory[i] for i in item_indices]
