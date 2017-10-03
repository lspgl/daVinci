class Colors:
    lightgray = '#323232'
    midgray = '#202020'
    darkgray = '#131313'

    textgray = '#9b9b9b'
    highlight = '#00bfc6'

    controlred = '#ff615f'
    controlyel = '#ffbd45'
    controlgreen = '#00ce4e'


def getColor(obj, key='background-color'):
    style = obj.styleSheet()
    entries = (''.join(style.split())).split(';')
    d = dict(e.split(':') for e in entries)
    return d[key]
