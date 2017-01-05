import math
import sys

import s3m


NOTE_NAMES = ('c', 'c+', 'd', 'd+', 'e', 'f', 'f+', 'g', 'g+', 'a', 'a+', 'b')


def notestr(cell, state):
    # state is the current channel state, structured like the cell
    string = ''
    if cell[0] != None and cell[0] & 128:
        string += 'r'
    else:
        if cell[1] and cell[1] != state[1]:
            string += '@%d' % cell[1]
        if cell[2] != None and (state[2] == None or
                int(3.6 * math.log(1 + cell[2])) != \
                        int(3.6 * math.log(1 + state[2]))):
            string += 'v%d' % int(3.6 * math.log(1 + cell[2]))
        if cell[0] and (state[0] == None or cell[0] // 16 != state[0] // 16):
            string += 'o%d' % (cell[0] // 16 + 1)
        if cell[3] == 7:
            string += '&'  # Gxx
        string += NOTE_NAMES[cell[0] % 16]
    return string


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

print('\nABCDEFGHI t%d\n' % (module.initialtempo * 3 // module.initialspeed))


def print_pattern(pattern):
    startrow, endrow = 0, -1  # Cxx stuff
    cxx = False
    for channel in range(9):
        print(chr(65 + channel), end=' ')
        chanstate, notelen = [None, None, None, None, None], 0
        if endrow == -1:
            endrow = len(pattern)
        for i, row in enumerate(pattern[startrow:endrow]):
            cell = row[channel]
            if cell and cell[0]:
                if not cell[0] & 128 and cell[2] == None:
                    cell[2] = 64  # blank volume is max volume
                if notelen != 0:
                    if not any(col for col in chanstate):
                        print('r', end='')
                    print(lenstr(notelen), end=' ')
                print(notestr(cell, chanstate), end='')
                if chanstate[0] == None or not cell[0] & 128:
                    chanstate[0] = cell[0]
                chanstate[1] = cell[1] or chanstate[1]
                chanstate[2] = cell[2] if cell[2] != None else chanstate[2]
                chanstate[3], chanstate[4] = cell[3], cell[4]
                notelen = 0
            notelen += 1
            if cell and cell[3]:
                if cell[3] == 3:  # Cxx
                    startrow, endrow, cxx = cell[4], i+1, True
                    break
        if not cxx:
            startrow, endrow = 0, -1
        if notelen != 0:
            if not any(col for col in chanstate):
                print('r', end='')
            print(lenstr(notelen), end='')
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
