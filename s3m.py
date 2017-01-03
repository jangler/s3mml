import struct


NOTE_NAMES = (
    'C-',
    'C#',
    'D-',
    'D#',
    'E-',
    'F-',
    'F#',
    'G-',
    'G#',
    'A-',
    'A#',
    'B-',
)


class Module():
    def __init__(self):
        pass


class Instrument():
    def __init__(self):
        pass


def read(f):
    """Read a Module from a file-like object."""
    buf = bytes(f.read())
    m = Module()
    read_header(buf, m)
    read_instruments(buf, m)
    read_patterns(buf, m)
    return m


def read_header(buf, m):
    """Read header information from buf into m."""
    m.title = struct.unpack_from('28s', buf, 0)[0].decode('ascii').strip('\0')
    m.numorders, m.numinstruments, m.numpatterns, m.flags, m.trackerversion, \
        m.sampletype = struct.unpack_from('6H', buf, 32)
    m.globalvolume, m.initialspeed, m.initialtempo, m.mastervolume, \
        m.ultraclickremoval, m.defaultpan = struct.unpack_from('6B', buf, 48)
    m.channelsettings = struct.unpack_from('32B', buf, 64)
    pos = 96
    m.orderlist = struct.unpack_from('%dB' % m.numorders, buf, pos)
    pos += m.numorders
    m.ptrinstruments = [x*16 for x in
            struct.unpack_from('%dH' % m.numinstruments, buf, pos)]
    pos += m.numinstruments * 2
    m.ptrpatterns = [x*16 for x in
            struct.unpack_from('%dH' % m.numpatterns, buf, pos)]


def read_instruments(buf, m):
    """Read instrument information from buf into m."""
    m.instruments = []
    for ptr in m.ptrinstruments:
        inst = Instrument()
        inst.type = struct.unpack_from('B', buf, ptr)[0]
        inst.filename = struct.unpack_from('12s', buf, ptr +
            1)[0].decode('ascii').strip()
        inst.oplvalues = struct.unpack_from('12B', buf, ptr + 16)
        inst.volume, inst.c2spd = struct.unpack_from('B3xI', buf, ptr + 28)
        inst.title = struct.unpack_from('28s', buf, ptr +
                36)[0].decode('ascii').strip()
        m.instruments.append(inst)


def read_patterns(buf, m):
    """Read pattern data from buf into m."""
    m.patterns = []
    for ptr in m.ptrpatterns:
        pat = []
        #packedlen = struct.unpack_from('H', buf, ptr)[0]  # unused
        ptr += 2
        for i in range(64):
            row = [None for j in range(32)]
            while True:
                what = struct.unpack_from('B', buf, ptr)[0]
                ptr += 1
                if what == 0:
                    break
                data = [None, None, None, None, None]
                if what & 0x20:  # note and instrument
                    data[0], data[1] = struct.unpack_from('BB', buf, ptr)
                    ptr += 2
                if what & 0x40:  # volume
                    data[2] = struct.unpack_from('B', buf, ptr)[0]
                    ptr += 1
                if what & 0x80:  # effect and parameter(s)
                    data[3], data[4] = struct.unpack_from('BB', buf, ptr)
                    ptr += 2
                row[what & 0x1f] = data
            pat.append(row)
        m.patterns.append(pat)


def write_song(module, f):
    # determine highest channel index used
    numchannels = 0
    for pattern in module.patterns:
        for row in pattern:
            for channel in range(len(row)):
                if row[channel] != None:
                    numchannels = max(numchannels, channel+1)

    # concatenate pattern text to f
    for order in module.orderlist:
        if order != 255:
            write_pattern(module.patterns[order], numchannels, f)
            f.write(b'\n')


def write_pattern(pattern, numchannels, f):
    for row in pattern:
        for cell in row[:numchannels]:
            write_cell(cell, f)
            f.write(b' ')
        f.write(b'\n')


def write_cell(data, f):
    if data == None:
        f.write(b'...----.00')
        return

    if data[0] == None:
        f.write(b'...--')
    elif data[0] < 128:
        f.write(('%s%01d%02d' %
            (NOTE_NAMES[data[0] % 16], data[0]/16 + 1, data[1])).encode('ascii'))
    else:
        f.write(b'===??')

    if data[2] == None:
        f.write(b'--')
    else:
        f.write(('%02d' % data[2]).encode('ascii'))

    if data[3] == None:
        f.write(b'.00')
    else:
        f.write(('%01X%02X' % tuple(data[3:5])).encode('ascii'))
