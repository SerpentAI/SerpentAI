import torch

from .noisy_linear import NoisyLinear


class DQN3(torch.nn.Module):
    def __init__(self, action_space, history=4, hidden_size=512, noisy_std=0.1, quantile=True):
        super().__init__()

        self.atoms = 200 if quantile else 51
        self.action_space = action_space

        self.quantile = quantile

        self.conv1 = torch.nn.Conv2d(history, 32, 8, stride=4, padding=1)
        self.conv2 = torch.nn.Conv2d(32, 64, 4, stride=2)
        self.conv3 = torch.nn.Conv2d(64, 64, 3)

        self.fc_h_v = NoisyLinear(5184, hidden_size, std_init=noisy_std)
        self.fc_h_a = NoisyLinear(5184, hidden_size, std_init=noisy_std)
        self.fc_z_v = NoisyLinear(hidden_size, self.atoms, std_init=noisy_std)
        self.fc_z_a = NoisyLinear(hidden_size, action_space * self.atoms, std_init=noisy_std)

    def forward(self, x):
        x = torch.nn.functional.relu(self.conv1(x))
        x = torch.nn.functional.relu(self.conv2(x))
        x = torch.nn.functional.relu(self.conv3(x))
        x = x.view(-1, 5184)

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


class DQN4(torch.nn.Module):
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
