import math
import sys

import s3m


NOTE_NAMES = ('c', 'c+', 'd', 'd+', 'e', 'f', 'f+', 'g', 'g+', 'a', 'a+', 'b')


def linlog(vol, outrange=15):
    # map linear volume 0-64 to log volume 0-15
    return int(outrange/6 * math.log2(1+vol))


def notestr(cell, state, instruments, ssg=False):
    # state is the current channel state, structured like the cell
    string = ''
    if cell[0] != None and cell[0] & 128:
        string += 'r'
    else:
        if cell[1] and cell[1] != state[1]:
            if ssg:
                inst = instruments[cell[1]-1].carrier
                string += 'E%d,%d,%d,%d,%d' % (
                    envcurve(inst.attack, 31),
                    envcurve(inst.decay, 31),
                    0 if inst.sustainsound else envcurve(inst.release, 31),
                    envcurve(inst.release),
                    15 - envcurve(inst.sustain),
                    # linlog(inst.volume),  # attack level (??)
                )
            else:
                string += '@%d' % cell[1]

        volrange = 15 if ssg else 127
        if cell[2] != None and (state[2] == None or
                linlog(cell[2], volrange) != linlog(state[2], volrange)):
            string += 'V%d' % linlog(cell[2], volrange)

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


def print_pattern(pattern, instruments):
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
                ssg = channel in range(6, 9)
                print(notestr(cell, chanstate, instruments, ssg), end='')
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


def envcurve(value, outrange=15):
    # adjust envelope curves from opl2 to opna
    return int(value**(3/4) * outrange/7.5)


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
        envcurve(inst.modulator.attack, 31),
        envcurve(inst.modulator.decay, 31),
        0 if inst.modulator.sustainsound else \
                envcurve(inst.modulator.release, 31),
        envcurve(inst.modulator.release),
        15 - envcurve(inst.modulator.sustain),
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
        envcurve(inst.carrier.attack, 31),
        envcurve(inst.carrier.decay, 31),
        0 if inst.carrier.sustainsound else \
                envcurve(inst.carrier.release, 31),
        envcurve(inst.carrier.release),
        15 - envcurve(inst.carrier.sustain),
        63 - inst.carrier.volume,
        int(inst.carrier.scaleenv),
        inst.carrier.freqmult,
        0, 0,
    ))
    print()

for order, pattern in enumerate(module.orderlist):
    if pattern < 255:
        print('; order %d, pattern %d' % (order, pattern))
        print_pattern(module.patterns[pattern], module.instruments)
