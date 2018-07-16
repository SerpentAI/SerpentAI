import math
import torch


class DQN(torch.nn.Module):
    def __init__(self, action_space, history=4, hidden_size=512, noisy_std=0.1, quantile=True):
        super().__init__()

        self.atoms = 200 if quantile else 51
        self.action_space = action_space

        self.quantile = quantile

        self.conv1 = torch.nn.Conv2d(history, 64, 8, stride=4, padding=1)
        self.conv2 = torch.nn.Conv2d(64, 128, 4, stride=2)
        self.conv3 = torch.nn.Conv2d(128, 256, 4, stride=2)
        self.conv4 = torch.nn.Conv2d(256, 512, 3, stride=1)

        self.fc_h_v = NoisyLinear(2048, hidden_size, std_init=noisy_std)
        self.fc_h_a = NoisyLinear(2048, hidden_size, std_init=noisy_std)
        self.fc_z_v = NoisyLinear(hidden_size, self.atoms, std_init=noisy_std)
        self.fc_z_a = NoisyLinear(hidden_size, action_space * self.atoms, std_init=noisy_std)

    def forward(self, x):
        x = torch.nn.functional.relu(self.conv1(x))
        x = torch.nn.functional.relu(self.conv2(x))
        x = torch.nn.functional.relu(self.conv3(x))
        x = torch.nn.functional.relu(self.conv4(x))
        x = x.view(-1, 2048)

        v = self.fc_z_v(torch.nn.functional.relu(self.fc_h_v(x)))
        a = self.fc_z_a(torch.nn.functional.relu(self.fc_h_a(x)))

        v, a = v.view(-1, 1, self.atoms), a.view(-1, self.action_space, self.atoms)

        q = v + a - a.mean(1, keepdim=True)

        if not self.quantile:
            q = torch.nn.functional.softmax(q, dim=2)

        return q

    def reset_noise(self):
        for name, module in self.named_children():
            if "fc" in name:
                module.reset_noise()


class NoisyLinear(torch.nn.Module):
    def __init__(self, in_features, out_features, std_init=0.4):
        super().__init__()

        self.in_features = in_features
        self.out_features = out_features
        self.std_init = std_init

        self.weight_mu = torch.nn.Parameter(torch.empty(out_features, in_features))
        self.weight_sigma = torch.nn.Parameter(torch.empty(out_features, in_features))

        self.register_buffer("weight_epsilon", torch.empty(out_features, in_features))

        self.bias_mu = torch.nn.Parameter(torch.empty(out_features))
        self.bias_sigma = torch.nn.Parameter(torch.empty(out_features))

        self.register_buffer("bias_epsilon", torch.empty(out_features))

        self.reset_parameters()
        self.reset_noise()

    def reset_parameters(self):
        mu_range = 1 / math.sqrt(self.in_features)

        self.weight_mu.data.uniform_(-mu_range, mu_range)
        self.weight_sigma.data.fill_(self.std_init / math.sqrt(self.in_features))

        self.bias_mu.data.uniform_(-mu_range, mu_range)
        self.bias_sigma.data.fill_(self.std_init / math.sqrt(self.out_features))

    def reset_noise(self):
        epsilon_in = self._scale_noise(self.in_features)
        epsilon_out = self._scale_noise(self.out_features)

        self.weight_epsilon.copy_(epsilon_out.ger(epsilon_in))
        self.bias_epsilon.copy_(epsilon_out)

    def forward(self, input):
        if self.training:
            return torch.nn.functional.linear(input, self.weight_mu + self.weight_sigma * self.weight_epsilon, self.bias_mu + self.bias_sigma * self.bias_epsilon)
        else:
            return torch.nn.functional.linear(input, self.weight_mu, self.bias_mu)

    def _scale_noise(self, size):
        x = torch.randn(size)
        return x.sign().mul_(x.abs().sqrt_())
