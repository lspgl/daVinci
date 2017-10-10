class Switches:

    def __init__(self):
        self.switches = {}

    def link(self, name, label):
        self.switches[name] = label

    def enable(self, name):
        self.switches[name].box.enable()

    def disable(self, name):
        self.switches[name].box.disable()

    def get(self, name):
        return self.switches[name].box.enabled

    def activate(self, name):
        self.switches[name].box.activate()

    def deactivate(self, name):
        self.switches[name].box.deactivate()
