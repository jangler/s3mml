#!/usr/bin/env python

import s3m
import sys

with open(sys.argv[1], 'rb') as f:
    module = s3m.read(f)
with open(sys.argv[2], 'wb') as f:
    s3m.write_song(module, f)
