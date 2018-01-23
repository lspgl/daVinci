class Colors:
    lightgray = '#0070aa'
    midgray = '#dddddd'
    darkgray = '#f7f7f7'
    white = '#ffffff'

    textgray = '#6e6e6e'
    highlight = '#0070aa'

    controlred = '#ce8585'
    controlyel = '#ffbd45'
    controlgreen = '#00ce4e'


def getColor(obj, key='background-color'):
    current = obj
    while True:
        style = current.styleSheet()
        entries = (''.join(style.split())).split(';')
        d = {}
        if len(entries) > 1:
            d = dict(e.split(':') for e in entries)

        if key in d:
            return d[key]
        else:
            current = current.parent
