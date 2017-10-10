class Physics:

    def __init__(self, label):
        self.label = label

    def update(self, cache):
        self.label.update(cache)
