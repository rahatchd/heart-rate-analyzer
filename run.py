import os

import numpy
from src import rate
from src import dill
from blessings import Terminal

shell = Terminal()


def center(text, s):
    return s.move_x(s.width / 2 - len(text) / 2) + text


print ''
print center('{s.bold}heart rate analyzer{s.normal}'.format(s=shell), shell)
print '=' * shell.width

print ''
patient = raw_input('enter {s.bold}patient ID{s.normal}: '.format(s=shell))
if os.path.isfile('data/' + patient + '.pkl'):
    print 'reading data...'
    raw = numpy.load('data/' + patient + '.pkl')
    print '{s.bold}data read{s.normal}'.format(s=shell)
    print ''
else:
    csv = raw_input('enter {s.bold}data sheet filename{s.normal}: '.format(s=shell))
    raw = dill.store(csv, patient, shell)
    while raw == -1:
        csv = raw_input(
            '<data/{}> not found, enter {s.bold}data sheet filename{s.normal}: '.format(
                csv,
                s=shell
            )
        )
        raw = dill.store(csv, patient, shell)

age = int(raw_input('enter {s.bold}patient age{s.normal}: '.format(s=shell)))
rate.analyze(raw, patient, age, shell)

print '=' * shell.width
print center('{s.bold}program terminated{s.normal}'.format(s=shell), shell)
print ''
