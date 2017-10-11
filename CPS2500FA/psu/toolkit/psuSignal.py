from .colors import Colors as _C


def parseReturn1(signal):
    pass


def parseReturn2(signal):
    bytesignal = []
    for s in signal:
        if isinstance(s, bytes):
            snew = s
        else:
            snew = bytes(s, 'utf-8')
        # snew = int(snew.replace("'", '').replace('b', '').replace('\\', '').replace('x', '0x'), 0)
        bytesignal.append(snew)

    stx = int.from_bytes(bytes(bytesignal[0]), byteorder='big')
    adr = int.from_bytes(bytes(bytesignal[1]), byteorder='big')
    cmd = int.from_bytes(bytes(bytesignal[2]), byteorder='big')
    length = int.from_bytes(bytes(bytesignal[3]), byteorder='big')

    data_raw = bytesignal[4:4 + length]
    data_raw = b''.join(data_raw)
    data = int.from_bytes(bytes(data_raw), byteorder='big')
    crc_raw = bytesignal[4 + length:]
    crc_raw = b''.join(crc_raw)
    crc = int.from_bytes(bytes(crc_raw), byteorder='big')

    bytesignal = [stx, adr, cmd, length, data, crc]

    payload = {'adr': adr, 'cmd': cmd, 'data': data, 'crc': crc}

    return (bytesignal, length, payload)


def tablePrint(send_array, send_length, recieving=False):
    if not recieving:
        C1 = _C.MAGENTA
        C2 = _C.BLUE
        print(C1 + 'Sending RS485: ' + _C.ENDC)
    else:
        C1 = _C.YEL
        C2 = _C.LIME
        print(C1 + 'Recieving RS485: ' + _C.ENDC)

    formatted = ''.join(paddedHex(d) + ' | ' for d in send_array[:4])

    if send_length != 0:
        header = (C1 + '| STX  | ADR  | CMD  | LEN  | DTA' +
                  (len(str(hex(send_array[4]))) - 3) * ' ' +
                  '  | CRC ' + (len(str(hex(send_array[-1]))) - 3) * ' ' + ' |' + _C.ENDC)

        for i in range(send_length):
            formatted += paddedHex(send_array[4 + i]) + ' '
        formatted += '| '
        # for c in send_array[4 + send_length:]:
        formatted += paddedHex(send_array[-1]) + ' '
        formatted += '|' + _C.ENDC
        formatted = C2 + '| ' + formatted
    else:
        header = (C1 + '| STX  | ADR  | CMD  | LEN  | DTA  | CRC  |' + _C.ENDC)
        formatted += '-    | '
        for c in send_array[4:]:
            formatted += paddedHex(c) + ' '
        formatted += '|' + _C.ENDC
        formatted = C2 + '| ' + formatted

    print(header)
    print(formatted)


def paddedHex(value):
    str_hex = str(hex(value))
    length = len(str_hex)
    if length == 4:
        return str_hex
    else:
        split = str_hex.split('x')
        str_hex = split[0] + 'x' + '0' + split[-1]
        return str_hex
