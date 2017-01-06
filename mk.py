#!/usr/bin/env python

import argparse

import mml
import s3m


# parse command-line args
parser = argparse.ArgumentParser(description="""
Convert a ScreamTracker 3 module to MML for the target compiler. Currently,
only AdLib instruments are supported.
""")
parser.add_argument('target', help='target MML compiler', choices=['pmd'])
parser.add_argument('infile', help='input S3M file')
parser.add_argument('outfile', nargs='?',
                    help='output MML file (default based on infile name)')
args = parser.parse_args()

# construct default outfile arg
if args.outfile is None:
    args.outfile = '%s.%s' % (args.infile.rpartition('.')[0],
            'MML' if args.infile.upper() == args.infile else 'mml')

# read input S3M file
with open(args.infile, 'rb') as f:
    module = s3m.read(f)

# load target settings
if args.target == 'pmd':
    import pmd
    target = pmd
else:
    # this should never happen because of the 'choice' option type
    raise ValueError('invalid target compiler: %s' % args.target)

# write output MML file
with open(args.outfile, 'w') as f:
    mml.write(f, module, target)
