# This script:

# (1): takes an SA1 correspondence file
# (2): takes an `SA1s_DISTS` file
# (3): updates (2) with the data from (1)

import csv
import sys
import os.path
import argparse
from collections import defaultdict
import random

# NB use relevant config file name here
from config2019 import *

CORR_HDRS = ['SA1_7DIGITCODE_old', 'SA1_7DIGITCODE_new', 'RATIO']
SA1s_DISTs_HDRS = ['SA1_Id', 'Dist_Name', 'Pop', 'Pop_Share']
VERBOSE = False

parser = argparse.ArgumentParser("Upgrade SA1s_DISTS file from old SA1s to new")
parser.add_argument('--verbose', action='store_true')
parser.add_argument('--no-infile-headers', action='store_true', help="Indicate lack of header row for infile")
parser.add_argument('correspondencefile', type=argparse.FileType('r'), help="Columns should be: "+', '.join(CORR_HDRS))
parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="Columns should be: "+', '.join(SA1s_DISTs_HDRS))
parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="Columns will be: "+', '.join(SA1s_DISTs_HDRS))

cli_args = parser.parse_args()
VERBOSE |= cli_args.verbose

def printv(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)

printv(cli_args)

# load up correspondence
corrs = defaultdict(list)
#print(dir(corr))
with cli_args.correspondencefile as cf:
    # key by old id
    c_rdr = csv.reader(cf)
    c_hdrs = next(c_rdr)
    for r in c_rdr:
        corrs[r[0]].append((r[1], float(r[2])))


printv(len(corrs), [(i, corrs[i]) for i in random.sample(list(corrs), 10)])

intermediate = {}
# build
with cli_args.infile as infile:
    inr = csv.reader(infile)
    if not cli_args.no_infile_headers:
        next(inr)
    for r in inr:
        old = r[0]
        corr = corrs[old]
        for new in corr:
            sa1 = new[0]
            dist = r[1]
            pop = float(r[2])*new[1]
            if sa1 not in intermediate: # double-layered defaultdict a bit much
                intermediate[sa1] = {dist : pop}
            else:
                if dist not in intermediate[sa1]:
                    intermediate[sa1][dist] = pop
                else:
                    intermediate[sa1][dist] += pop

with cli_args.outfile as outfile:
    outw = csv.writer(outfile)
    outw.writerow(SA1s_DISTs_HDRS)

    for (sa1,dists) in intermediate.items():
        poptotal = sum(dists.values())
        poptotal = 1 if (poptotal == 0) else poptotal
        for (d, p) in dists.items():
            outw.writerow([sa1, d, p, p/poptotal])
