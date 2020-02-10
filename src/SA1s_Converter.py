#! /usr/bin/env python3

# Copyright: (c) 2017-2020, Alex Jago <abjago@abjago.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# This script:

# (1): takes an ABS SA1-old to SA1-new correspondence file
# (2): takes an SA1-old to district file (`SA1s_DISTS`)
# (3): updates (2) according to (1)

import csv
import sys
import os.path
import argparse
from collections import defaultdict
import random

# NB use relevant config file name here
# from config2019 import *

CORR_HDRS = ['SA1_7DIGITCODE_old', 'SA1_7DIGITCODE_new', 'RATIO']
SA1s_DISTs_HDRS = ['SA1_Id', 'Dist_Name', 'Pop', 'Pop_Share']
VERBOSE = False # for development

def parse_argv():
    parser = argparse.ArgumentParser("Upgrade SA1s_DISTS file from old SA1s to new")
    parser.add_argument('--no-infile-headers', action='store_true', help="Indicate lack of header row for infile")
    parser.add_argument('correspondencefile', type=argparse.FileType('r'), help="Columns should be: "+', '.join(CORR_HDRS))
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="Columns should be: "+', '.join(SA1s_DISTs_HDRS))
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="Columns will be: "+', '.join(SA1s_DISTs_HDRS))
    return parser.parse_args()

def main(args, CORR_HDRS, SA1s_DISTs_HDRS, VERBOSE):

    cli_args = args

    if VERBOSE: print(cli_args, file=sys.stderr)

    # load up correspondence
    corrs = defaultdict(list)

    with cli_args.correspondencefile as cf:
        # key by old id
        c_rdr = csv.reader(cf)
        c_hdrs = next(c_rdr)
        for r in c_rdr:
            corrs[r[0]].append((r[1], float(r[2])))

    if VERBOSE: print(len(corrs), [(i, corrs[i]) for i in random.sample(list(corrs), 10)], file=sys.stderr)

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
                sa1 = new[0] # now key by new ID
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

# end main()

if __name__ == "__main__":
    sys.exit(main(parse_argv(), CORR_HDRS, SA1s_DISTs_HDRS, VERBOSE))
