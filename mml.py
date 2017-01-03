import sys

import s3m


NOTE_NAMES = ('c', 'c+', 'd', 'd+', 'e', 'f', 'f+', 'g', 'g+', 'a', 'a+', 'b')


def notestr(cell, prevcell, f):
    if cell[0] & 128:
        print('r', end='', file=f)
    else:
        if prevcell == None or cell[1] != prevcell[1]:
            print('@%d' % cell[1], end='', file=f)
        if cell[2] != None:
            if prevcell == None or prevcell[2] == None or \
                    cell[2] // (65/15) != prevcell[2] // (65/15):
                print('v%d' % (cell[2] // (65/15)), end='', file=f)
        elif prevcell == None or (prevcell[2] != None):
            print('v15', end='', file=f)
        if prevcell == None or cell[0] // 16 != prevcell[0] // 16:
            print('o%d' % (cell[0] // 16 + 1), end='', file=f)
        print(NOTE_NAMES[cell[0] % 16], end='', file=f)


def lenstr(notelen, cell):
    # one row is a 16th note
    lengths = []
    while notelen >= 16:
        notelen -= 16
        lengths.append('1')
    while notelen >= 8:
        notelen -= 8
        lengths.append('2')
    while notelen >= 4:
        notelen -= 4
        lengths.append('4')
    while notelen >= 2:
        notelen -= 2
        lengths.append('8')
    while notelen >= 1:
        notelen -= 1
        lengths.append('16')
    if cell == None or cell[0] & 128:
        joiner = '&r'
    else:
        joiner = '&%s' % NOTE_NAMES[cell[0] % 16]
    return joiner.join(lengths)


with open(sys.argv[1], 'rb') as f:
    module = s3m.read(f)

print('#Title    %s' % module.title)
print('#Filename .M2')

print('\nABCDEFGHI t%d\n' % (module.initialtempo * 6 // module.initialspeed))

def print_pattern(pattern):
    for channel in range(9):
        print(chr(65 + channel), end=' ')
        prevcell, notelen = None, 0
        for row in pattern:
            cell = row[channel]
            if cell and cell[0]:
                if notelen != 0:
                    if prevcell == None:
                        print('r', end='')
                    print(lenstr(notelen, prevcell), end=' ')
                notestr(cell, prevcell, sys.stdout)
                prevcell, notelen = cell, 0
            elif notelen == 32:
                if prevcell == None:
                    print('r', end='')
                print(lenstr(notelen, prevcell), end=' ')
                prevcell, notelen = None, 0
            notelen += 1
        if notelen != 0:
            if prevcell == None:
                print('r', end='')
            print(lenstr(notelen, prevcell), end=' ')
        print() # newline
    print()  # newline


for order, pattern in enumerate(module.orderlist):
    if pattern < 255:
        print('; order %d, pattern %d' % (order, pattern))
        print_pattern(module.patterns[pattern])
