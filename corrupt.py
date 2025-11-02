import sys
import random
import struct
import argparse
import string

parser = argparse.ArgumentParser()
parser.add_argument('input', nargs='?', type=argparse.FileType('rb'),
        default=sys.stdin.buffer,
        help='input file. defaults to stdin')
parser.add_argument('-o', '--output', type=argparse.FileType('wb'),
        default=sys.stdout.buffer, action='store',
        help='output filename. defaults to stdout')
parser.add_argument('-n', action='store', type=str, default=None,
        help='''average good bits per error, percentage with %% suffix, or bit error rate in scientific notation.
                e.g., -n 1000000, -n 0.001%%, -n 10e-6 for 0.00001 bit error rate''')
parser.add_argument('-s', action='store', type=str, default=None,
        help='''sector-based error rate: number or percentage with %% suffix.
                e.g., -s 10 for 1 bad sector per 10 sectors, -s 5%% for 5%% of sectors corrupted''')
parser.add_argument('--sector-size', action='store', type=int, default=2048,
        help='sector size in bytes. defaults to 2048')
parser.add_argument('-e', '--errors-per-sector', action='store', type=int, default=20,
        help='number of bit errors to introduce per corrupted sector. defaults to 20')
parser.add_argument('-z', '--zero-sectors', action='store_true',
        help='zero out entire corrupted sectors instead of flipping individual bits')
parser.add_argument('-t', '--truncate', action='store',
        type=int, default=None,
        help='truncate file after T bytes')
parser.add_argument('-g', '--garbage', action='store', type=int, default=0,
        help='add G bytes of garbage at the end of the file')
parser.add_argument('-a', '--ascii', action='store_true',
        help='assume ASCII input and enforce ASCII output')
parser.add_argument('-d', '--debug', action='store_true',
        help='print debug information')
args = parser.parse_args()

# Parse error rate: convert percentage or sectors to good bits per error
if args.n is not None and args.s is not None:
    parser.error('Cannot specify both -n and -s')
elif args.s is not None:
    # Sector-based error rate
    if args.s.endswith('%'):
        # Percentage of sectors corrupted
        sector_percent = float(args.s[:-1])
        if sector_percent <= 0 or sector_percent > 100:
            parser.error('Sector error percentage must be between 0 and 100')
        # Convert to sectors per error
        sectors_per_error = 100.0 / sector_percent
        n = int(sectors_per_error * args.sector_size * 8)
    else:
        # Number of sectors per error
        sectors = float(args.s)
        if sectors <= 0:
            parser.error('Sectors per error must be positive')
        n = int(sectors * args.sector_size * 8)
elif args.n is not None:
    # Bit-based error rate
    if args.n.endswith('%'):
        error_rate_percent = float(args.n[:-1])
        if error_rate_percent <= 0:
            parser.error('Error rate percentage must be positive')
        n = int(100 / error_rate_percent)
    elif 'e' in args.n.lower():
        # Scientific notation - interpret as bit error rate
        bit_error_rate = float(args.n)
        if bit_error_rate <= 0 or bit_error_rate > 1:
            parser.error('Bit error rate must be between 0 and 1')
        n = int(1.0 / bit_error_rate)
    else:
        n = int(args.n)
        if n <= 0:
            parser.error('Average good bits per error must be positive')
else:
    # Default to 1 error per 1 million bits
    n = 1000000

if args.debug:
    bit_error_rate = 1.0 / n
    print(f'Debug: n = {n} (average good bits per error)', file=sys.stderr)
    if bit_error_rate < 0.0001:
        print(f'Debug: bit error rate = {bit_error_rate:.2e}', file=sys.stderr)
    else:
        print(f'Debug: bit error rate = {bit_error_rate:.10f}', file=sys.stderr)

CHUNK = 4096
cstart = 0
cend = 0
nextn = random.randint(0,n)
data = args.input.read(CHUNK)
while len(data) > 0:
    data = bytearray(data)  # Convert to mutable bytearray
    cend = cstart + len(data)
    while cend > nextn//8:
        k = nextn - cstart * 8
        byte_idx = k//8

        # Determine which sector contains this corruption point
        sector_start = (cstart + byte_idx) // args.sector_size * args.sector_size
        sector_end = sector_start + args.sector_size

        if args.zero_sectors:
            # Zero out the entire sector (or the portion within this chunk)
            chunk_sector_start = max(sector_start, cstart)
            chunk_sector_end = min(sector_end, cend)
            local_start_idx = chunk_sector_start - cstart
            local_end_idx = chunk_sector_end - cstart
            data[local_start_idx:local_end_idx] = bytes(local_end_idx - local_start_idx)
        else:
            # Introduce multiple bit errors within the sector
            for _ in range(args.errors_per_sector):
                # Pick a random bit within this sector
                bit_offset = random.randint(0, args.sector_size * 8 - 1)
                abs_byte = sector_start + bit_offset // 8

                # Only corrupt if this byte is in the current chunk
                if cstart <= abs_byte < cend:
                    local_byte_idx = abs_byte - cstart
                    if args.ascii:
                        data[local_byte_idx] = ord(random.choice(string.printable))
                    else:
                        data[local_byte_idx] ^= (1 << (bit_offset % 8))

        nextn += random.randint(0,2*n)
    cstart = cend
    if args.truncate is not None and cend > args.truncate:
        args.output.write(bytes(data[:args.truncate - cstart]))
        break
    args.output.write(bytes(data))
    data = args.input.read(CHUNK)

random.seed()
garbage = args.garbage
while garbage > 0:
    if args.ascii:
        b = random.choice(string.printable).encode('ascii')
    else:
        b = bytes([random.randint(0, 255)])
    args.output.write(b)
    garbage -= 1

args.output.close()
