import itertools


class KeyboardMouseInputSpace:

    def __init__(self, **kwargs):
        self.input_label_index_mapping = dict()
        self.input_discrete_spaces = list()

        for i, (input_label, inputs) in enumerate(kwargs.items()):
            self.input_label_index_mapping[input_label] = i
            self.input_discrete_spaces.append([0, len(inputs)])

        self.labeled_inputs = kwargs

        self.permutation_values = None

    @property
    def permutations(self):
        if self.permutation_values is None:
            input_groups = [[None] + inputs for inputs in self.labeled_inputs.values()]

            self.permutation_values = list(
                itertools.product(*[list(map(lambda t: t[0], enumerate(input_group))) for input_group in input_groups])
            )

        return self.permutation_values

    def values_for_permutation(self, permutation):
        values = list()

        for index, value_index in enumerate(permutation):
            values.append(([None] + self.labeled_inputs[list(self.labeled_inputs.keys())[index]])[value_index])

        return values
