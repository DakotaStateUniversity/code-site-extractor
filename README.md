# code-site-extractor

Requirements
------------
* **code-site-extractor** was tested on Python 3.4, on both Linux.
* **code-site-extractor** has no external dependencies. The only non-stdlib libraries it
  uses are [pycparser](https://github.com/eliben/pycparser) and [PLY](https://github.com/dabeaz/ply), which is bundled in ``pycparser`` and ``pycparser/ply``.
* **code-site-extractor** Uses ``cpp`` for preprocessing directives.

Usage
-------
```
usage: get_sites.py [-h] [-o outfile] [-s type] srcfile

Extract sites from file(s) and output them to file.

positional arguments:
  srcfile               source file or directory name

optional arguments:
  -h, --help            show this help message and exit
  -o outfile, --output-file outfile
                        site output file name
  -s type, --sites type
                        which type of site to search for ['all',
                        'buffer_write']
```

Examples
--------

```
python3 get_sites.py ../Juliet_Test_Cases
```
```
python3 get_sites.py -o writes.csv ../Juliet_Test_Cases
```

Package contents
----------------

``code-site-extractor`` package contains the following files and
directories:

* README.md:

  This README file.

* icse/get_sites.py:

  The **code-site-extractor** main source code.

* icse/pycparser:

  The **pycparser** module source code.

* Juliet_Test_Cases:

  C source files selected for testing.

* icse/icse:

  The **code-site-extractor** module source code.

* icse/utils:

  Minimal standard C library include files that should allow to parse any C code.
