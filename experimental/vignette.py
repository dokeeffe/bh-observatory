#!/usr/bin/python


import numpy as np

r = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
# dist from sensor to filter
x = 25
# dia of filter
a = 26.5
fl = 750
d = 150
for z in r:
    dia = 2*((a/2)*fl)/x
    offset = (((fl*((a-(z*2))/2))/x)+z)
    print 'z=' + str(z)
    print 'dia= ' + str(dia)
    print 'offset=' + str(offset)
    if offset + d/2 > dia:
        print 'overlap'
