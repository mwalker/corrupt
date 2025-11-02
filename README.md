corrupt
=======

Command line utility to simulate file corruption.

Given an input file it randomly corrupts bits or characters, which can be useful in testing how well other programs deal with file corruption. Options include setting the bit error rate, sector-based corruption, truncating files, adding garbage to the end of files, and running on ascii and binary files.

Dependencies
------------

Python 3.x

Usage
-----

### Basic bit-based corruption

Corrupt approximately every 100,000th bit (bit error rate of 1e-5):

    python corrupt.py -n 100000 infile -o outfile

Use scientific notation for bit error rate:

    python corrupt.py -n 1e-6 infile -o outfile

Use percentage for bit error rate:

    python corrupt.py -n 0.001% infile -o outfile

### Sector-based corruption

Corrupt 1 sector per 10 sectors (default 2048-byte sectors):

    python corrupt.py -s 10 infile -o outfile

Corrupt 5% of sectors:

    python corrupt.py -s 5% infile -o outfile

Use custom sector size (4096 bytes):

    python corrupt.py -s 10 --sector-size 4096 infile -o outfile

Control number of bit errors per corrupted sector (default 20):

    python corrupt.py -s 10 -e 50 infile -o outfile

Zero out entire corrupted sectors instead of bit flipping:

    python corrupt.py -s 5% -z infile -o outfile

### Other options

Corrupt and also truncate after 4K:

    python corrupt.py -t 4096 infile -o outfile

Corrupt and add 30 bytes of random data at the end:

    python corrupt.py -g 30 infile -o outfile

Corrupt a text file, ensuring output is printable ASCII characters:

    python corrupt.py -a input.txt -o output.txt

Debug mode to see calculated error rates:

    python corrupt.py -n 1e-6 -d infile -o outfile

### Standard input/output

Input/output defaults to stdin/stdout if no files specified:

    python corrupt.py < infile > outfile

All the above options can be combined.

Options
-------

    -n              Bit error rate: number of bits per error, percentage (%), or scientific notation (e.g., 1e-6)
    -s              Sector error rate: number of sectors per error or percentage (%)
    --sector-size   Sector size in bytes (default: 2048)
    -e              Number of bit errors per corrupted sector (default: 20)
    -z              Zero out entire corrupted sectors instead of bit flipping
    -t              Truncate file after T bytes
    -g              Add G bytes of random garbage at the end of the file
    -a              Assume ASCII input and enforce ASCII output
    -d              Print debug information (calculated error rates)
    -o              Output file (default: stdout)

Examples
--------

Simulate a storage device with 0.01% sector failure rate, zeroing bad sectors:

    python corrupt.py -s 0.01% -z disk.img -o corrupted.img

High bit error rate for stress testing:

    python corrupt.py -n 1e-4 -d test.bin -o test_corrupted.bin

Realistic sector errors (10 bit flips per bad sector, 1% of sectors affected):

    python corrupt.py -s 1% -e 10 input.dat -o output.dat
