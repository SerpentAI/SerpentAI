import random


class EpsilonGreedyQPolicy:

    def __init__(self, initial_epsilon=1.0, final_epsilon=0.1, max_steps=1000000):
        self.initial_epsilon = initial_epsilon
        self.final_epsilon = final_epsilon

        self.epsilon = self.initial_epsilon

        self.max_steps = max_steps

    def use_random(self):
        return random.random() <= self.epsilon

    def erode(self, factor=1):
        if self.epsilon > self.final_epsilon:
            self.epsilon -= (self.initial_epsilon - self.final_epsilon) / (self.max_steps / factor)
        else:
            self.epsilon = self.final_epsilon
