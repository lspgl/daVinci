class Text:

    def __init__(self):
        self.text = {}

    def link(self, name, label):
        self.text[name] = label

    def setText(self, name, txt):
        self.text[name].setText(txt)
