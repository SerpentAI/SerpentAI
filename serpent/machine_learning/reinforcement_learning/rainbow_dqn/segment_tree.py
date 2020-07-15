

class SegmentTree:

    def __init__(self, size):
        self.index = 0

        self.size = size
        self.full = False

        self.sum_tree = [0] * (2 * size - 1)

        self.data = [None] * size

        self.max = 1

    def update(self, index, value):
        self.sum_tree[index] = value
        self._propagate(index, value)
        self.max = max(value, self.max)

    def append(self, data, value):
        self.data[self.index] = data
        self.update(self.index + self.size - 1, value)
        self.index = (self.index + 1) % self.size
        self.full = self.full or self.index == 0
        self.max = max(value, self.max)

    def find(self, value):
        index = self._retrieve(0, value)
        data_index = index - self.size + 1

        return (self.sum_tree[index], data_index, index)

    def get(self, data_index):
        return self.data[data_index % self.size]

    def total(self):
        return self.sum_tree[0]

    def _retrieve(self, index, value):
        left, right = 2 * index + 1, 2 * index + 2

        if left >= len(self.sum_tree):
            return index
        elif value <= self.sum_tree[left]:
            return self._retrieve(left, value)
        else:
            return self._retrieve(right, value - self.sum_tree[left])

    def _propagate(self, index, value):
        parent = (index - 1) // 2
        left, right = 2 * parent + 1, 2 * parent + 2

        self.sum_tree[parent] = self.sum_tree[left] + self.sum_tree[right]

        if parent != 0:
            self._propagate(parent, value)
