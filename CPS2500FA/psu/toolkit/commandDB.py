class CommandDB:

    def __init__(self):
        self.db = {}
        # Useful key subsets
        # All read keys
        self.readkeys = [0x00, 0x03, 0x10,
                         0x11, 0x12, 0x13,
                         0x14, 0x15, 0x16,
                         0x18, 0x19, 0x1A,
                         0x1B,
                         ]
        # Physical state keys
        self.physkeys = [0x10, 0x11, 0x12,
                         0x13, 0x14, 0x15]
        # Keys with 10.6 bits
        self.splitByte = [0x13, 0x14, 0x15]

        # Device info keys
        self.devicekeys = [0x18, 0x19, 0x1A,
                           0x1B]
        # Error keys
        self.errorkeys = [0x16, 0x17]

        # Unimplemented keys
        self.unimplemented = [0x25, 0x26]

        # Core functions --------------------------------------------------
        self.db[0x00] = {'desc': 'Reading on/off state',
                         'data': None,
                         'length': 0,
                         'retval': 'bool',
                         'rvl': 1}
        self.db[0x01] = {'desc': 'Turning off',
                         'data': 0x0811,
                         'length': 2,
                         'retval': 'error',
                         'rvl': 1}
        self.db[0x02] = {'desc': 'Turning on',
                         'data': 0x55AA,
                         'length': 2,
                         'retval': 'error',
                         'rvl': 1}
        self.db[0x03] = {'desc': 'Reading current limit setpoint',
                         'data': None,
                         'length': 0,
                         'retval': 'phys',
                         'rvl': 2,
                         'unit': 'A',
                         'maxval': 66}
        self.db[0x04] = {'desc': 'Writing current limit setpoint',
                         'data': 'val',
                         'length': 2,
                         'retval': 'error',
                         'rvl': 1}
        # Address ---------------------------------------------------------
        self.db[0x05] = {'desc': 'Changing address',
                         'data': 'val',
                         'length': 1,
                         'retval': None,
                         'rvl': 0}
        self.db[0x06] = {'desc': 'Resetting address',
                         'data': 0x1234,
                         'length': 2,
                         'retval': None,
                         'rvl': 0}
        # Reading properties ----------------------------------------------
        self.db[0x10] = {'desc': 'Reading output voltage',
                         'data': None,
                         'length': 0,
                         'retval': 'phys',
                         'rvl': 2,
                         'unit': 'V',
                         'maxval': 48}
        self.db[0x11] = {'desc': 'Reading output current',
                         'data': None,
                         'length': 0,
                         'retval': 'phys',
                         'rvl': 2,
                         'unit': 'A',
                         'maxval': 84}
        self.db[0x12] = {'desc': 'Reading output power',
                         'data': None,
                         'length': 0,
                         'retval': 'phys',
                         'rvl': 2,
                         'unit': 'W',
                         'maxval': 4032}
        self.db[0x13] = {'desc': 'Reading input voltage',
                         'data': 0,
                         'length': 1,
                         'retval': 'phys',
                         'rvl': 2,
                         'res': 10.6,
                         'unit': 'V'}
        self.db[0x14] = {'desc': 'Reading input frequency',
                         'data': 0,
                         'length': 1,
                         'retval': 'phys',
                         'rvl': 2,
                         'res': 10.6,
                         'unit': 'Hz'}
        self.db[0x15] = {'desc': 'Reading temperature',
                         'data': 0,
                         'length': 1,
                         'retval': 'phys',
                         'rvl': 2,
                         'res': 10.6,
                         'unit': 'C'}
        # Error mask ------------------------------------------------------
        self.db[0x16] = {'desc': 'Reading error mask',
                         'data': None,
                         'length': 0,
                         'retval': 'val',
                         'rvl': 2}
        self.db[0x17] = {'desc': 'Clearing error mask',
                         'data': None,
                         'length': 0,
                         'retval': 'error',
                         'rvl': 1}
        # Device Information ----------------------------------------------
        self.db[0x18] = {'desc': 'Power board HW version',
                         'data': None,
                         'length': 0,
                         'retval': 'val',
                         'rvl': 2}
        self.db[0x19] = {'desc': 'Control board HW version',
                         'data': None,
                         'length': 0,
                         'retval': 'val',
                         'rvl': 2}
        self.db[0x1A] = {'desc': 'Firmware version',
                         'data': None,
                         'length': 0,
                         'retval': 'val',
                         'rvl': 2}
        self.db[0x1B] = {'desc': 'Serial number',
                         'data': None,
                         'length': 0,
                         'retval': 'val',
                         'rvl': 8}
        # Error lines ---------------------------------------------------
        self.db[0x20] = {'desc': 'Pulling ERROR line',
                         'data': None,
                         'length': 0,
                         'retval': 'error',
                         'rvl': 2}
        self.db[0x21] = {'desc': 'Pulling STATUS line',
                         'data': None,
                         'length': 0,
                         'retval': 'error',
                         'rvl': 1}
        self.db[0x22] = {'desc': 'Pulling ERROR485 line',
                         'data': None,
                         'length': 0,
                         'retval': 'error',
                         'rvl': 1}
        self.db[0x23] = {'desc': 'Clear all error lines',
                         'data': None,
                         'length': 0,
                         'retval': 'error',
                         'rvl': 1}
        # Multicasting ----------------------------------------------------
        self.db[0x24] = {'desc': 'Configure multicast-domain master',
                         'data': 'val',
                         'length': 1,
                         'retval': 'bool',
                         'rvl': 1}
        # Warning mask ------------------------------------------------------
        self.db[0x25] = {'desc': 'Reading warning mask',
                         'data': None,
                         'length': 0,
                         'retval': 'val',
                         'rvl': 2}
        self.db[0x26] = {'desc': 'Clearing warning mask',
                         'data': None,
                         'length': 0,
                         'retval': 'error',
                         'rvl': 1}
        # Bootloader ------------------------------------------------------
        self.db[0x30] = {'desc': 'Device in bootloader',
                         'data': None,
                         'length': 0,
                         'retval': 'val',
                         'rvl': 2}
        self.db[0x31] = {'desc': 'Going to bootloader',
                         'data': 0xBEEF,
                         'length': 2,
                         'retval': None,
                         'rvl': 0}

        # Misc -----------------------------------------------------------
        self.db[0x80] = {'desc': 'Protocol error',
                         'data': None,
                         'length': 0,
                         'retval': 'val',
                         'rvl': 2}
