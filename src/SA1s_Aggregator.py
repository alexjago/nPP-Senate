#! /usr/bin/env python3

# Copyright: (c) 2017-2020, Alex Jago <abjago@abjago.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# This script:

# (1): takes SA1-by-SA1 NPP data
# (2): takes SA1 population & district split data
# (3): scales (1) to fit [the totals of] (2)
# (4): splits (3) according to (2) where necessary
# (5): aggregates (4) by district

import csv
import sys
import os.path
import json
import argparse

# we'll use this one later
ttyjump = '\033[F\033[2K' if (hasattr(sys.stderr, "isatty") and sys.stderr.isatty()) else ""

def main(SCENARIO, PARTIES, SA1S_DISTRICTS_PATH, SA1S_PREFS_PATH, NPP_DISTS_PATH, WRITE_JS):
    ''' 1. Take SA1-by-SA1 NPP data from SA1S_PREFS_PATH
        2. Take SA1 population & district split data from SA1S_DISTRICTS_PATH
        3. Scale (1) to fit (2) [if 3rd & 4th columns exist in (2)]
        4. Also split (3) according to (2) where necessary/available
        5. Aggregates (4) by district.
        6. Output to NPP_DISTS_PATH
    '''
    # (1): takes SA1-by-SA1 4PP data

    aec_sa1s = {}

    districts = {}

    outfieldnames = []

    print("... Combining progress:\t loading...", file=sys.stderr)

    with open(SA1S_PREFS_PATH) as consol_sa1s_fp:

        consolreader = csv.reader(consol_sa1s_fp)

        outfieldnames = next(consolreader)

        for row in consolreader:
            aec_sa1s[row[0]] = row[1:]

    with open(SA1S_DISTRICTS_PATH) as ecq_sa1s_fp:

        ecqreader = csv.reader(ecq_sa1s_fp)

        ecqheaders = next(ecqreader)

        progress = 0
        for i in ecqreader: # this will start from the first actual data, yay
            progress += 1
            try:
                aec_sa1 = aec_sa1s[i[0]]
            except KeyError:
                #print(i)
                continue

            # multiplier is the ratio of the total voters the SA1 is expected to have,
            # to the total votes cast from that SA1 at the election.

            try:
                multiplier = float(i[2])/float(aec_sa1[-1])
            except ZeroDivisionError:
                multiplier = 0.0
            except IndexError:
                # Perhaps you only have a list saying which SA1 is in which electorate.
                # If that happens the i[2] will barf.
                # That's OK, just use what we have
                multiplier = 1.0

            if i[1] in districts:
                for j in range(len(districts[i[1]])):
                    districts[i[1]][j] += float(aec_sa1[j]) * multiplier
            else:
                districts[i[1]] = [float(j) * multiplier for j in aec_sa1]

            if progress % 100 == 0:
                print(ttyjump + f"... Combining progress: accumulating {progress} SA1s ...", file=sys.stderr)

        print(ttyjump + f"... Combining complete: {progress} SA1s accumulated into {len(districts)} districts.\n", file=sys.stderr)


    print(ttyjump+"... Writing File", file=sys.stderr, end='')

    with open(NPP_DISTS_PATH, 'w') as output_fp:

        print("District", *outfieldnames[1:], sep = ",", file = output_fp)
        dists_sorted = sorted([[d] + districts[d] for d in districts.keys()])
        for d in dists_sorted:
            print(*d, sep = ",", file = output_fp)

    if WRITE_JS:
        output_fn = os.path.splitext(NPP_DISTS_PATH)[0] + ".js"
        output_obj = {"parties": {},
                        "field_names": outfieldnames[1:],
                        "data": districts}

        for (p, s) in PARTIES.items():
            pname = s[0].split(':')[1]
            output_obj["parties"][p] = pname if pname else p

        with open(output_fn, 'w') as output_fp:
            print("var district_prefs = " + json.dumps(output_obj), file=output_fp)

    print("... Done!\n", file=sys.stderr)
# end of main()

def parse_argv():
    parser = argparse.ArgumentParser("Aggregate SA1-by-SA1 NPP data by electoral district")
    parser.add_argument('--js', action='store_true', help='also output JS for website predictor')
    parser.add_argument('configfile', type=argparse.FileType('r'))
    mxg = parser.add_mutually_exclusive_group(required=True)
    mxg.add_argument("-a", "--all", action="store_true", help="run every scenario defined in `configfile`")
    mxg.add_argument("-s", "--scenario", dest='scenarios', metavar='scenario', action="append", help="run a scenario code defined in `configfile` (can be specified multiple times to run several scenarios)")
    # not going to support listing scenarios here

    return parser.parse_args()


def run(args, confp):
    try:
        if args.scenarios and not (set(args.scenarios).intersection(set(confp.sections()))):
            print(f"Error: no specified scenario is defined.", file=sys.stderr)
        else:
            scenlist = confp.sections() if argp.all else argp.scenarios
            for SCENARIO in scenlist:
                YEAR = confp[SCENARIO]['YEAR']
                PARTIES = json.loads(confp[SCENARIO]['GROUPS'])
                STATE = confp[SCENARIO]['STATE']
                SA1S_DISTRICTS_PATH = confp[SCENARIO]['SA1S_DISTS_PATH']
                OUTPUT_DIR = confp[SCENARIO]['OUTPUT_DIR']
                SA1S_PREFS_PATH = os.path.join(OUTPUT_DIR, SCENARIO, confp[SCENARIO]['SA1S_PREFS_FN'])
                NPP_DISTS_PATH = os.path.join(OUTPUT_DIR, SCENARIO, confp[SCENARIO]['NPP_DISTS_FN'])

                print("*** Combining Scenario {}: {}, in {} [{}] ***\n".format(SCENARIO, " vs ".join(PARTIES.keys()), STATE, YEAR), file=sys.stderr)
                main(SCENARIO, PARTIES, SA1S_DISTRICTS_PATH, SA1S_PREFS_PATH, NPP_DISTS_PATH, args.js)
    except KeyError as k:
        sys.exit(f"There was an issue with the arguments or configuration file: {k}")


if __name__ == "__main__":
    args = parse_argv()
    confp = configparser.ConfigParser()
    confp.read_file(argp.configfile)
    run(args, confp)
