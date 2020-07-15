import torch


def init(module, weight_init, bias_init, gain=1):
    weight_init(module.weight.data, gain=gain)
    bias_init(module.bias.data)

    return module


class Flatten(torch.nn.Module):
    def forward(self, x):
        return x.view(x.size(0), -1)


class CNNBase(torch.nn.Module):
    def __init__(self, num_inputs, use_gru):
        super().__init__()

        init_ = lambda m: init(
            m,
            torch.nn.init.orthogonal_,
            lambda x: torch.nn.init.constant_(x, 0),
            torch.nn.init.calculate_gain("relu")
        )

        self.main = torch.nn.Sequential(
            init_(torch.nn.Conv2d(num_inputs, 32, 8, stride=4)),
            torch.nn.ReLU(),
            init_(torch.nn.Conv2d(32, 64, 4, stride=2)),
            torch.nn.ReLU(),
            init_(torch.nn.Conv2d(64, 64, 3, stride=1)),
            torch.nn.ReLU(),
            Flatten(),
            init_(torch.nn.Linear(5184, 512)),
            torch.nn.ReLU()
        )

        if use_gru:
            self.gru = torch.nn.GRUCell(512, 512)
            torch.nn.init.orthogonal_(self.gru.weight_ih.data)
            torch.nn.init.orthogonal_(self.gru.weight_hh.data)
            self.gru.bias_ih.data.fill_(0)
            self.gru.bias_hh.data.fill_(0)

        init_ = lambda m: init(
            m,
            torch.nn.init.orthogonal_,
            lambda x: torch.nn.init.constant_(x, 0)
        )

        self.critic_linear = init_(torch.nn.Linear(512, 1))

        self.train()

    @property
    def state_size(self):
        if hasattr(self, "gru"):
            return 512
        else:
            return 1

    @property
    def output_size(self):
        return 512

    def forward(self, inputs, states, masks):
        x = self.main(inputs / 255.0)

        if hasattr(self, "gru"):
            if inputs.size(0) == states.size(0):
                x = states = self.gru(x, states * masks)
            else:
                x = x.view(-1, states.size(0), x.size(1))

                masks = masks.view(-1, states.size(0), 1)                
                outputs = []
                
                for i in range(x.size(0)):
                    hx = states = self.gru(x[i], states * masks[i])
                    outputs.append(hx)

                x = torch.cat(outputs, 0)

        return self.critic_linear(x), x, states
