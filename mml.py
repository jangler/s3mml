# generalized MML compilation functions

NOTE_NAMES = ('c', 'c+', 'd', 'd+', 'e', 'f', 'f+', 'g', 'g+', 'a', 'a+', 'b')


def notestr(cell, state, channel, instruments, target):
    # state is the current channel state, structured like the cell
    string = ''

    if cell[0] is not None and cell[0] & 128:
        string += 'r'
    else:
        # instrument column
        if cell[1] and cell[1] != state[1]:
            string += target.envstr(cell[1], instruments[cell[1]-1], channel)

        # volume column
        if cell[2] is not None and (state[2] is None or
                target.volstr(cell[2], channel) !=
                        target.volstr(state[2], channel)):
            string += target.volstr(cell[2], channel)

        # "octave column"
        if cell[0] and (state[0] is None or cell[0] // 16 != state[0] // 16):
            string += 'o%d' % (cell[0] // 16 + 1)

        # effects columns
        if cell[3] == 7:
            string += target.TIE  # Gxx

        # note column
        string += NOTE_NAMES[cell[0] % 16]

    return string


def lenstr(notelen, tie='&'):
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
    return tie.join(lengths)


def print_pattern(pattern, instruments, target, f):
    startrow, endrow = 0, -1  # Cxx stuff
    cxx = False
    for channel in range(len(target.CHANNELS)):
        print(chr(65 + channel), file=f, end=' ')
        chanstate, notelen = [None, None, None, None, None], 0
        if endrow == -1:
            endrow = len(pattern)
        for i, row in enumerate(pattern[startrow:endrow]):
            cell = row[channel]
            if cell and cell[0]:
                if not cell[0] & 128 and cell[2] is None:
                    cell[2] = 64  # blank volume is max volume
                if notelen != 0:
                    if not any(col for col in chanstate):
                        print('r', file=f, end='')
                    print(lenstr(notelen, target.TIE), file=f, end=' ')
                print(notestr(cell, chanstate, channel, instruments, target),
                        file=f, end='')
                if chanstate[0] is None or not cell[0] & 128:
                    chanstate[0] = cell[0]
                chanstate[1] = cell[1] or chanstate[1]
                chanstate[2] = cell[2] if cell[2] is not None else chanstate[2]
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
                print('r', file=f, end='')
            print(lenstr(notelen, target.TIE), file=f, end='')
        print('', file=f)  # newline
    print('', file=f)  # newline


def write(f, module, target):
    target.write_header(module, f)
    for i, inst in enumerate(module.instruments):
        target.write_inst(i+1, inst, f)
    for order, pattern in enumerate(module.orderlist):
        if pattern < 255:
            print('; order %d, pattern %d' % (order, pattern), file=f)
            print_pattern(module.patterns[pattern], module.instruments,
                    target, f)
