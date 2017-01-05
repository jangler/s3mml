import sys

import s3m


NOTE_NAMES = ('c', 'c+', 'd', 'd+', 'e', 'f', 'f+', 'g', 'g+', 'a', 'a+', 'b')


def notestr(cell, prevcell, f):
    if cell[0] & 128:
        print('r', end='', file=f)
    else:
        if prevcell == None or cell[1] != prevcell[1]:
            print('@%d' % cell[1], end='', file=f)
            print('v15', end='', file=f)
        if cell[2] != None:
            if prevcell == None or prevcell[2] == None or \
                    cell[2] // (65/15) != prevcell[2] // (65/15):
                print('v%d' % (cell[2] // (65/15)), end='', file=f)
        elif prevcell == None or (prevcell[2] != None):
            print('v15', end='', file=f)
        if prevcell == None or cell[0] // 16 != prevcell[0] // 16:
            print('o%d' % (cell[0] // 16 + 1), end='', file=f)
        if cell[3] != None and cell[3] == 7:
            print('&', end='', file=f)  # Gxx
        print(NOTE_NAMES[cell[0] % 16], end='', file=f)


def lenstr(notelen, sep='&'):
    # represent note value with ties of dotted numbers
    lengths = []
    while notelen > 0:
        length = None
        # one row is a 16th note
        for i in (1, 2, 4, 8, 16):
            if length:
                if notelen >= 16/i:
                    length += '.'
                    notelen -= 16/i
                else:
                    break  # can't use . anymore
            elif notelen >= 16/i:
                length = str(i)
                notelen -= 16/i
                if notelen >= i:
                    break  # use &1 instead of ....
        lengths.append(length)
    return sep.join(lengths)


with open(sys.argv[1], 'rb') as f:
    module = s3m.read(f)

print('#Title    %s' % module.title)
print('#Filename .M2')

print('\nABCDEFGHI t%d' % (module.initialtempo * 3 // module.initialspeed))


def print_pattern(pattern):
    startrow, endrow = 0, -1  # Cxx stuff
    cxx = False
    for channel in range(9):
        print(chr(65 + channel), end=' ')
        prevcell, notelen = None, 0
        if endrow == -1:
            endrow = len(pattern)
        for i, row in enumerate(pattern[startrow:endrow]):
            cell = row[channel]
            if cell and cell[0]:
                if notelen != 0:
                    if prevcell == None:
                        print('r', end='')
                    print(lenstr(notelen), end=' ')
                notestr(cell, prevcell, sys.stdout)
                prevcell, notelen = cell, 0
            notelen += 1
            if cell and cell[3]:
                if cell[3] == 3:  # Cxx
                    startrow, endrow, cxx = cell[4], i+1, True
                    break
        if not cxx:
            startrow, endrow = 0, -1
        if notelen != 0:
            if prevcell == None:
                print('r', end='')
            print(lenstr(notelen), end=' ')
        print() # newline
    print()  # newline


for i, inst in enumerate(module.instruments):
    # nm alg fb
    print('@%d 5 %d' % (i+1, inst.feedback))
    # ar dr sr rr sl tl ks ml dt ams
    # ar dr sr 0-31
    # rr sl 0-15
    # tl 0-127
    # ks 0-3
    # ml 0-15
    # dt 0-7 (-3~+3)
    # ams 0-1
    print('%d %d %d %d %d %d %d %d %d %d' % (
        inst.modulator.attack * 2,
        inst.modulator.decay * 2,
        0 if inst.modulator.sustainsound else inst.modulator.release,
        inst.modulator.release,
        15 - inst.modulator.sustain,
        63 - inst.modulator.volume,
        int(inst.modulator.scaleenv),
        inst.modulator.freqmult,
        0, 0,
    ))
    print('%d %d %d %d %d %d %d %d %d %d' % (
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # unused
    ))
    print('%d %d %d %d %d %d %d %d %d %d' % (
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # unused
    ))
    print('%d %d %d %d %d %d %d %d %d %d' % (
        inst.carrier.attack * 2,
        inst.carrier.decay * 2,
        0 if inst.carrier.sustainsound else inst.carrier.release,
        inst.carrier.release,
        15 - inst.carrier.sustain,
        63 - inst.carrier.volume,
        int(inst.carrier.scaleenv),
        inst.carrier.freqmult,
        0, 0,
    ))
    print()

for order, pattern in enumerate(module.orderlist):
    if pattern < 255:
        print('; order %d, pattern %d' % (order, pattern))
        print_pattern(module.patterns[pattern])
