S3MML
=====

Convert ScreamTracker 3 modules to MML targeting specific sound chips.

Usage:

	usage: mk.py [-h] {pmd} infile [outfile]

	Convert a ScreamTracker 3 module to MML for the target compiler. Currently,
	only AdLib instruments are supported, and the only target compiler is PMD.

	positional arguments:
	  {pmd}       target MML compiler
	  infile      input S3M file
	  outfile     output MML file (default based on infile name)

	optional arguments:
	  -h, --help  show this help message and exit

Some quick notes off the top of my head:

- The program will not warn you if you use unsupported effect commands, which
  is most of them. Cxx is supported if it's in the first channel, and Gxx is
  used to tie notes of different pitches (but it "bends" them instantly
  regardless of the parameter).
- ST3 itself handles Gxx on AdLib instruments in a weird way, at least in
  DOSBox. Schism Tracker and Adlib Tracker 2 play Gxx the way you'd normally
  expect.
- The beginning of a new pattern is always treated as a note-off for every
  channel.
- If you find a bug or want a feature, open an issue in the GitHub issue
  tracker or make a pull request. Or like, message me on IRC if that's what you
  normally do.

PMD-specific notes
------------------

PMD (Professional Music Driver) supports multiple sound chips, but this
converter specifically targets the OPNA.

- Channels 1-6 are FM, and 7-9 are SSG. The converter does not support any form
  of PCM.
- Unlike the OPL2, the OPNA can only use sine waves as FM operators.
- The SSG still supports the envelopes that FM instruments use, but of course
  the timbres will always be square waves.

Links
-----

- [Scream Tracker 3](http://www.pouet.net/prod.php?which=13351)
- [OpenMPT](https://openmpt.org/)
- [Schism Tracker](http://schismtracker.org/)
- [PMD](http://battleofthebits.org/lyceum/View/Professional+Music+Driver+\(PMD\)/)
