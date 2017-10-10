class Indicators:

    def __init__(self):
        self.indicators = {}

    def link(self, name, label):
        self.indicators[name] = label

    def enable(self, name):
        self.indicators[name].box.enable()

    def disable(self, name):
        self.indicators[name].box.disable()

    def flash(self, name):
        self.indicators[name].box.flash()
