import os
import random

import torch
from torch import nn, optim

from serpent.machine_learning.reinforcement_learning.rainbow_dqn.dqn import DQN


class RainbowAgent:
    def __init__(
        self,
        action_space,
        device,
        quantile=True,
        quantiles=200,
        atoms=51,
        v_min=-10,
        v_max=10,
        batch_size=32,
        multi_step=3,
        discount=0.99,
        history=4,
        hidden_size=512,
        noisy_std=0.1,
        learning_rate=0.0000625,
        adam_epsilon=1.5e-4,
        model=None
    ):
        self.action_space = action_space
        self.quantile = quantile
        self.atoms = quantiles if quantile else atoms

        if quantile:
            self.cumulative_density = (2 * torch.arange(self.atoms).to(device=device) + 1) / (2 * self.atoms)
        else:
            self.Vmin = v_min
            self.Vmax = v_max

            self.support = torch.linspace(v_min, v_max, self.atoms).to(device=device)
            self.delta_z = (v_max - v_min) / (self.atoms - 1)

        self.batch_size = batch_size

        self.multi_step = multi_step
        self.discount = discount

        self.online_net = DQN(self.action_space, history=history, hidden_size=hidden_size, noisy_std=noisy_std, quantile=quantile).to(device=device)

        if model and os.path.isfile(model):
            self.online_net.load_state_dict(torch.load(model, map_location="cpu"))

        self.online_net.train()

        self.target_net = DQN(self.action_space, history=history, hidden_size=hidden_size, noisy_std=noisy_std, quantile=quantile).to(device=device)
        self.update_target_net()
        self.target_net.train()

        for param in self.target_net.parameters():
            param.requires_grad = False

        self.optimiser = torch.optim.Adam(self.online_net.parameters(), lr=learning_rate, eps=adam_epsilon)

    def reset_noise(self):
        self.online_net.reset_noise()

    def act(self, state):
        with torch.no_grad():
            return (self.online_net(state.unsqueeze(0)) * ((1 / self.atoms) if self.quantile else self.support)).sum(2).argmax(1).item()

    def act_e_greedy(self, state, epsilon=0.05):
        return random.randrange(self.action_space) if random.random() < epsilon else self.act(state)

    def learn(self, replay_memory):
        idxs, states, actions, returns, next_states, nonterminals, weights = replay_memory.sample(self.batch_size)

        ps = self.online_net(states)
        ps_a = ps[range(self.batch_size), actions]

        with torch.no_grad():
            pns = self.online_net(next_states)
            dns = ((1 / self.atoms) if self.quantile else self.support.expand_as(pns)) * pns

            argmax_indices_ns = dns.sum(2).argmax(1)

            self.target_net.reset_noise()

            pns = self.target_net(next_states)
            pns_a = pns[range(self.batch_size), argmax_indices_ns]

            if self.quantile:
                Ttheta = returns.unsqueeze(1) + nonterminals * (self.discount ** self.multi_step) * pns_a
            else:
                Tz = returns.unsqueeze(1) + nonterminals * (self.discount ** self.multi_step) * self.support.unsqueeze(0)
                Tz = Tz.clamp(min=self.Vmin, max=self.Vmax)

                b = (Tz - self.Vmin) / self.delta_z
                l, u = b.floor().to(torch.int64), b.ceil().to(torch.int64)

                l[(u > 0) * (l == u)] -= 1
                u[(l < (self.atoms - 1)) * (l == u)] += 1

                m = states.new_zeros(self.batch_size, self.atoms)

                offset = torch.linspace(0, ((self.batch_size - 1) * self.atoms), self.batch_size).unsqueeze(1).expand(self.batch_size, self.atoms).to(actions)

                m.view(-1).index_add_(0, (l + offset).view(-1), (pns_a * (u.float() - b)).view(-1))
                m.view(-1).index_add_(0, (u + offset).view(-1), (pns_a * (b - l.float())).view(-1))

        if self.quantile:
            u = Ttheta - ps_a
            kappa_cond = (u < 1).to(torch.float32)
            huber_loss = 0.5 * u ** 2 * kappa_cond + (u.abs() - 0.5) * (1 - kappa_cond)
            loss = torch.sum(torch.abs(self.cumulative_density - (u < 0).to(torch.float32)) * huber_loss, 1)
        else:
            loss = -torch.sum(m * ps_a.log(), 1)

        self.online_net.zero_grad()
        (weights * loss).mean().backward()
        self.optimiser.step()

        if self.quantile:
            loss = (self.atoms * loss).clamp(max=5)

        replay_memory.update_priorities(idxs, loss.detach())

    def update_target_net(self):
        self.target_net.load_state_dict(self.online_net.state_dict())

    def save(self, file_name):
        torch.save(self.online_net.state_dict(), file_name)

    def evaluate_q(self, state):
        with torch.no_grad():
            return (self.online_net(state.unsqueeze(0)) * ((1 / self.atoms) if self.quantile else self.support)).sum(2).max(1)[0].item()

    def train(self):
        self.online_net.train()

    def eval(self):
        self.online_net.eval()
