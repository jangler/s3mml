# settings for PMD OPL2 output

import math


TIE = '&'
CHANNELS = 'ABCDEFGHI'
EFFECTS = ['Cxx', 'Gxx']  # TODO: warn when unsupported effects are used


def envstr(num, inst, channel):
    return '@%d' % num


def volstr(volume, channel):
    return 'v%d' % ((volume-1)//4)


def write_header(module, f):
    # metadata
    if module.title:
        print('#Title    %s' % module.title, file=f)
    print('#Option   /L /V', file=f)
    print('#Filename .M\n', file=f)

    # initial tempo
    print('%s t%d\n' %
        (CHANNELS, module.initialtempo * 6 // module.initialspeed), file=f)


def write_inst(num, inst, f):
    # nm alg fb
    print('@%02d %d %d' % (num, inst.connection, inst.feedback), file=f)
    # ar dr rr sl  tl  ksl ml ksr egt vib am
    # 15 15 15 -15 -63 3   15 1   2   1   1
    print(' %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d' % (
        inst.modulator.attack,
        inst.modulator.decay,
        inst.modulator.release,
        15 - inst.modulator.sustain,
        63 - inst.modulator.volume,
        inst.modulator.levelscaling,
        inst.modulator.freqmult,
        int(inst.modulator.scaleenv),
        inst.modulator.waveselect,
        int(inst.modulator.vibrato),
        int(inst.modulator.tremolo),
    ), file=f)
    print(' %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d' % (
        inst.carrier.attack,
        inst.carrier.decay,
        inst.carrier.release,
        15 - inst.carrier.sustain,
        63 - inst.carrier.volume,
        inst.carrier.levelscaling,
        inst.carrier.freqmult,
        int(inst.carrier.scaleenv),
        inst.carrier.waveselect,
        int(inst.carrier.vibrato),
        int(inst.carrier.tremolo),
    ), file=f)
    print('', file=f)  # newline
