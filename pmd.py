# settings for PMD output

import math


TIE = '&'
CHANNELS = 'ABCDEFGHI'
EFFECTS = ['Cxx', 'Gxx']  # TODO: warn when unsupported effects are used


def envcurve(value, outrange=15):
    # adjust envelope curves from opl2 to opna
    return int(value**(3/4) * outrange/7.5)


def envstr(num, inst, channel):
    # return FM instrument or SSG envelope definition
    if channel in range(6, 9):
        carrier = inst.carrier
        return 'E%d,%d,%d,%d,%d' % (
            envcurve(carrier.attack, 31),
            envcurve(carrier.decay, 31),
            0 if carrier.sustainsound else envcurve(carrier.release, 31),
            envcurve(carrier.release),
            15 - envcurve(carrier.sustain),
        )
    else:
        return '@%d' % num


def volstr(volume, channel):
    # map linear volume 0-64 to log volume 0-127 (FM) or 0-15 (SSG)
    outrange = 15 if channel in range(6, 9) else 127
    return 'V%d' % int(outrange/6 * math.log2(1+volume))


def write_header(module, f):
    # metadata
    if module.title:
        print('#Title    %s' % module.title, file=f)
    print('#Filename .M2\n', file=f)

    # initial tempo
    print('%s t%d\n' %
        (CHANNELS, module.initialtempo * 3 // module.initialspeed), file=f)


def write_inst(num, inst, f):
    # nm alg fb
    # use alg 5 (op1 is modulator, all else are carriers) since op1 is the only
    # operator that can do feedback
    print('@%d 5 %d' % (num, inst.feedback), file=f)
    # ar dr sr rr sl tl  ks ml dt ams
    # 31 31 31 15 15 127 3  15 7  1
    print('%d %d %d %d %d %d %d %d %d %d' % (
        envcurve(inst.modulator.attack, 31),
        envcurve(inst.modulator.decay, 31),
        0 if inst.modulator.sustainsound else
            envcurve(inst.modulator.release, 31),
        envcurve(inst.modulator.release),
        15 - envcurve(inst.modulator.sustain),
        63 - inst.modulator.volume,
        int(inst.modulator.scaleenv),
        inst.modulator.freqmult,
        0, 0,
    ), file=f)
    print('%d %d %d %d %d %d %d %d %d %d' % (
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # unused
    ), file=f)
    print('%d %d %d %d %d %d %d %d %d %d' % (
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # unused
    ), file=f)
    print('%d %d %d %d %d %d %d %d %d %d' % (
        envcurve(inst.carrier.attack, 31),
        envcurve(inst.carrier.decay, 31),
        0 if inst.carrier.sustainsound else
                envcurve(inst.carrier.release, 31),
        envcurve(inst.carrier.release),
        15 - envcurve(inst.carrier.sustain),
        63 - inst.carrier.volume,
        int(inst.carrier.scaleenv),
        inst.carrier.freqmult,
        0, 0,
    ), file=f)
    print('', file=f)  # newline
