import collections
import random

import torch

from serpent.machine_learning.reinforcement_learning.rainbow_dqn.segment_tree import SegmentTree


Transition = collections.namedtuple("Transition", ("timestep", "state", "action", "reward", "nonterminal"))
blank_transition = Transition(0, torch.zeros(100, 100, dtype=torch.uint8), None, 0, False)


class ReplayMemory:

    def __init__(
        self,
        capacity,
        device,
        history=4,
        discount=0.99,
        multi_step=3,
        priority_weight=0.4,
        priority_exponent=0.5
    ):
        self.capacity = capacity
        self.device = device

        self.history = history
        self.discount = discount
        self.multi_step = multi_step
        self.priority_weight = priority_weight
        self.priority_exponent = priority_exponent

        self.timestep = 0
        self.transitions = SegmentTree(capacity)

    def __iter__(self):
        self.current_index = 0
        return self

    def __next__(self):
        if self.current_index == self.capacity:
            raise StopIteration

        state_stack = [None] * self.history
        state_stack[-1] = self.transitions.data[self.current_index].state

        previous_timestep = self.transitions.data[self.current_index].timestep

        for t in reversed(range(self.history - 1)):
            if previous_timestep == 0:
                state_stack[t] = blank_transition.state
            else:
                state_stack[t] = self.transitions.data[self.current_index + t - self.history + 1].state
                previous_timestep -= 1

        state = torch.stack(state_stack, 0).to(dtype=torch.float32, device=self.device).div_(255)

        self.current_index += 1

        return state

    def append(self, state, action, reward, terminal):
        state = state[-1].mul(255).to(dtype=torch.uint8, device=torch.device("cpu"))

        self.transitions.append(Transition(self.timestep, state, action, reward, not terminal), self.transitions.max)
        self.timestep = 0 if terminal else self.timestep + 1

    def sample(self, batch_size):
        priority_total = self.transitions.total()

        segment = priority_total / batch_size
        batch = [self._get_sample_from_segment(segment, i) for i in range(batch_size)]

        probabilities, indices, tree_indices, states, actions, returns, next_states, nonterminals = zip(*batch)
        probabilities = torch.tensor(probabilities, dtype=torch.float32, device=self.device) / priority_total

        states, next_states, = torch.stack(states), torch.stack(next_states)
        actions, returns, nonterminals = torch.cat(actions), torch.cat(returns), torch.stack(nonterminals)

        capacity = self.capacity if self.transitions.full else self.transitions.index

        weights = (capacity * probabilities) ** -self.priority_weight
        weights = weights / weights.max()

        return tree_indices, states, actions, returns, next_states, nonterminals, weights

    def update_priorities(self, indices, priorities):
        priorities.pow_(self.priority_exponent)
        [self.transitions.update(index, priority) for index, priority in zip(indices, priorities)]

    def _get_transition(self, index):
        transition = [None] * (self.history + self.multi_step)
        transition[self.history - 1] = self.transitions.get(index)

        for t in range(self.history - 2, -1, -1):
            if transition[t + 1].timestep == 0:
                transition[t] = blank_transition
            else:
                transition[t] = self.transitions.get(index - self.history + 1 + t)

        for t in range(self.history, self.history + self.multi_step):
            if transition[t - 1].nonterminal:
                transition[t] = self.transitions.get(index - self.history + 1 + t)
            else:
                transition[t] = blank_transition

        return transition

    def _get_sample_from_segment(self, segment, i):
        valid = False

        while not valid:
            sample = random.uniform(i * segment, (i + 1) * segment)
            probability, index, tree_index = self.transitions.find(sample)

            if (self.transitions.index - index) % self.capacity > self.multi_step and (index - self.transitions.index) % self.capacity >= self.history and probability != 0:
                valid = True

        transition = self._get_transition(index)

        state = torch.stack([trans.state for trans in transition[:self.history]]).to(dtype=torch.float32, device=self.device).div_(255)
        next_state = torch.stack([trans.state for trans in transition[self.multi_step:self.multi_step + self.history]]).to(dtype=torch.float32, device=self.device).div_(255)

        action = torch.tensor([transition[self.history - 1].action], dtype=torch.int64, device=self.device)

        R = torch.tensor([sum(self.discount ** n * transition[self.history + n - 1].reward for n in range(self.multi_step))], dtype=torch.float32, device=self.device)

        nonterminal = torch.tensor([transition[self.history + self.multi_step - 1].nonterminal], dtype=torch.float32, device=self.device)

        return probability, index, tree_index, state, action, R, next_state, nonterminal
