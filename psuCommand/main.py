import serial


def test(a, c, d, f=0):
    pass


def main():
    name0 = '/dev/cu.usbserial-FT084RPW'
    name1 = '/dev/cu.usbserial-FT084SMN'

    ser0 = serial.Serial(name0, timeout=1)
    ser1 = serial.Serial(name1, timeout=1)

    r0 = ser0.read()
    r1 = ser1.read()

    print(r0, r1)


if __name__ == '__main__':
    main()
