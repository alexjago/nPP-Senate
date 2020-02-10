#! /usr/bin/env python3

# Copyright: (c) 2017-2020, Alex Jago <abjago@abjago.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# The AEC have given us a
# "this many people from this SA1 voted at this booth"
# spreadsheet. This is almost tailor made for projecting Senate results
# onto state electoral boundaries.

# the usual suspects
import csv
import json
from collections import defaultdict
import itertools
import os
import sys
import argparse

## NB update relevant config file name here
#from config2019 import *
# Mr Gorbachev, tear down etc etc

# Generate booth data structure (combinations hardcoded):
NPP_FIELDS = ["ID", "Division", "Booth", "Latitude", "Longitude"]

# So we'll have 7 columns of stuff before the prefs start:
SA1s_FIELDS = ["year","state_ab", "div_nm", "SA1_id", "pp_id", "pp_nm", "votes"]

# we'll use this one later
ttyjump = '\033[F\033[2K' if (hasattr(sys.stderr, "isatty") and sys.stderr.isatty()) else ""


def main(SCENARIO, NPP_BOOTHS_PATH, STATE, YEAR, PARTIES, SA1S_BREAKDOWN_PATH, SA1S_PREFS_PATH):

    combinations = ["None"] # special-casing the empty

    for r in range(len(PARTIES)):
        chooseN = list(itertools.combinations(sorted(PARTIES), r+1))
        for i in chooseN:
            combinations += ["".join(j) for j in list(itertools.permutations(i))]

    total_combos = len(combinations)


    ### Load in booth data

    booths = {}

    boothsfields = NPP_FIELDS+combinations+["Total"]

    with open(NPP_BOOTHS_PATH) as consolcsv:
        consolreader = csv.DictReader(consolcsv) # fieldnames implicit from the first line

        for row in consolreader:
            booths[row["Division"]+row["Booth"]] = row # key by 'divbooth'


    ###

    lines = []

    with open(SA1S_BREAKDOWN_PATH) as sa1scsv:

        sa1sreader = csv.DictReader(sa1scsv) # fieldnames implicit from the first line

        progress = 0
        print()
        for srow in sa1sreader:

            if not srow["state_ab"]==STATE:
                continue # All SA1s nationwide are in the one file - so any row with the wrong state can be safely skipped.
            elif not (srow["year"] == YEAR):
                sys.exit("Problem in `{SA1s_BREAKDOWN_PATH}`: Unsupported election year: "+srow["year"]+". Exiting.")
                # However, the wrong year is definitely cause for concern

            # if progress == 0:
            #     print(f"Projecting Senate results for scenario {SCENARIO} from "+srow["year"]+" onto state/territory-level electoral boundaries.\n", file=sys.stderr)

            # basically a big vector multiply

            bob = [srow["SA1_id"]]
            db = [ booths[srow["div_nm"]+srow["pp_nm"]][i] for i in boothsfields[5:] ]
            ##  print("db:\t", db)
            for i in range(len(db)):
                try:
                    bob.append(float(srow["votes"]) * float(db[i]) / float(db[-1]))
                except ZeroDivisionError:
                    bob.append(0.0)

            lines.append(bob)

            ##  print("bob:\t", bob)

            progress+= 1
            if (progress % 1000 == 0):
                print(ttyjump+f"... Projection progress: {progress:n} SA1s...", file=sys.stderr)

    print(ttyjump+f"... Projection complete: {progress:n} SA1s", file=sys.stderr)

    # Accumulation phase.

    sa1s = {}
    print(f"... Progress: summing SA1s...", file=sys.stderr)
    for line in lines:
        sa1_id = line[0]

        if sa1_id not in sa1s:
            sa1s[sa1_id] = line[1:]
        else:
            for i in range(1, len(line)):
                sa1s[sa1_id][i-1] += line[i]


    outlines = []

    for ids in sa1s.keys():
        outlines.append([ids] + sa1s[ids])

    outlines.sort()

    print(ttyjump+"... Writing File...", file=sys.stderr, end='')


    with open(SA1S_PREFS_PATH, 'w') as fp:
        print(*(["SA1_id"] + boothsfields[5:]), sep=',', file=fp, flush=True)

        for line in outlines:
            print(*line, sep=',', file=fp)

    print("... Done!\n", file=sys.stderr)

# end main()


def run(argp, confp):
    try:
        if argp.scenarios and not (set(argp.scenarios).intersection(set(confp.sections()))):
            print(f"Error: no specified scenario is defined.", file=sys.stderr)
        else:
            scenlist = confp.sections() if argp.all else argp.scenarios
            for SCENARIO in scenlist:
                YEAR = confp[SCENARIO]['YEAR']
                PARTIES = json.loads(confp[SCENARIO]['GROUPS'])
                STATE = confp[SCENARIO]['STATE']
                SA1S_DISTRICTS_PATH = confp[SCENARIO]['SA1S_DISTS_PATH']
                SA1S_BREAKDOWN_PATH = confp[SCENARIO]['SA1S_BREAKDOWN_PATH']
                OUTPUT_DIR = confp[SCENARIO]['OUTPUT_DIR']
                NPP_BOOTHS_PATH = os.path.join(OUTPUT_DIR, SCENARIO, confp[SCENARIO]['NPP_BOOTHS_FN'])
                SA1S_PREFS_PATH = os.path.join(OUTPUT_DIR, SCENARIO, confp[SCENARIO]['SA1S_PREFS_FN'])

                print("*** Projecting Scenario {}: {}, in {} [{}] ***\n".format(SCENARIO, " vs ".join(PARTIES.keys()), STATE, YEAR), file=sys.stderr)
                main(SCENARIO, NPP_BOOTHS_PATH, STATE, YEAR, PARTIES, SA1S_BREAKDOWN_PATH, SA1S_PREFS_PATH)
    except KeyError as k:
        sys.exit(f"There was an issue with the arguments or configuration file: {k}")


def parse_argv():
    parser = argparse.ArgumentParser(help="Project booth results down onto SA1s")
    # pretty much everything comes from the configfile, yeah?
    parser.add_argument('configfile', type=argparse.FileType('r'))
    mxg = parser.add_mutually_exclusive_group(required=True)
    mxg.add_argument("-a", "--all", action="store_true", help="run every scenario defined in `configfile`")
    mxg.add_argument("-s", "--scenario", dest='scenarios', metavar='scenario', action="append", help="run a scenario code defined in `configfile` (can be specified multiple times to run several scenarios)")
    # not going to support listing scenarios here

    return parser.parse_args()



if __name__ == "__main__":
    argp = parser.parse_args()
    confp = configparser.ConfigParser()
    confp.read_file(argp.configfile)
    run(argp, confp)
