class Colors:
    lightgray = '#323232'
    midgray = '#202020'
    darkgray = '#131313'
    white = '#ffffff'

    textgray = '#9b9b9b'
    highlight = '#00bfc6'

    controlred = '#ff615f'
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
