import numpy as np
import random


class ReplayMemory:
    def __init__(self, memory_size=5000):
        self.tree = SumTree(memory_size)
        self.alpha = 0.6

    def add(self, error, observation):
        priority = self._get_priority(error)
        self.tree.add(priority, observation)

    def sample(self, quantity):
        samples = list()
        segment = self.tree.total() / quantity

        for i in range(quantity):
            s = random.uniform(a=segment * i, b=segment * (i + 1))
            index, priority, observation = self.tree.get(s)

            samples.append((index, observation))

        return samples

    def update(self, index, error):
        priority = self._get_priority(error)
        self.tree.update(index, priority)

    def _get_priority(self, error):
        return (error + 0.01) ** self.alpha


class SumTree:

    def __init__(self, size=5000):
        self.position = 0
        self.size = size
        self.tree = np.zeros(2 * size - 1)
        self.data = np.zeros(size, dtype=object)

    def total(self):
        return self.tree[0]

    def add(self, priority, data):
        index = self.position + self.size - 1

        self.data[self.position] = data
        self.update(index, priority)

        self.position += 1

        if self.position >= self.size:
            self.position = 0

    def update(self, index, priority):
        delta = priority - self.tree[index]

        self.tree[index] = priority
        self._propagate(index, delta)

    def get(self, s):
        index = self._retrieve(0, s)
        data_index = index - self.size + 1

        return index, self.tree[index], self.data[data_index]

    def _propagate(self, index, delta):
        parent = (index - 1) // 2

        self.tree[parent] += delta

        if parent != 0:
            self._propagate(parent, delta)

    def _retrieve(self, index, s):
        left = 2 * index + 1
        right = left + 1

        if left >= len(self.tree):
            return index

        if s <= self.tree[left]:
            return self._retrieve(left, s)
        else:
            return self._retrieve(right, s-self.tree[left])
