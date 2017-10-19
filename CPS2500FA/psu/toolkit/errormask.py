class Masks:
    error = {0: 'Mains overvoltage',
             1: 'Mains undervoltage',
             2: 'Output 1 overvoltage',
             3: 'Output 1 undervoltage',
             4: 'Output 1 overcurrent',
             5: 'Output 2 overvoltage',
             6: 'Output 2 undervoltage',
             7: 'Overtemperature',
             8: 'AC loss',
             9: 'Short circuit condition',
             15: 'Hardware error'}
    retcode = {0: 'No Error',
               1: 'Value not in range',
               2: 'Addr-in not high',
               3: 'Error in register'}
    warning = {0: 'Cannot match setpoint',
               1: 'High temperature'}
