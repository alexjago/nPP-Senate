#! /usr/bin/env python3

# Copyright: (c) 2017-2020, Alex Jago <abjago@abjago.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


# We want to reduce each unique preference sequence to some ordering
#    of each of the parties. For example, for four parties there are 65 orderings:
#    (0!) + (4 * 1!) + (6 * 2!) + (4 * 3!) + (4!)

# This script is intended to be upgraded evergreen for the latest format of AEC
#  senate ballot data (subject to some delay immediately after an election).
# Older formats are to be updated by one or more separate scripts.

import csv
from collections import defaultdict
import itertools
import os, os.path
import sys
import configparser
import json
import argparse

from npp_utils import open_csvz
from term import TTYJUMP

###### Structural Things that just need to be defined somewhere. ######
NPP_FIELD_NAMES = ["ID", "Division", "Booth", "Latitude", "Longitude"] # for the output
lenpp = len(NPP_FIELD_NAMES)
BOOTH_FIELD_NAMES = ["State", "DivisionID", "DivisionNm", "PollingPlaceID", "PollingPlaceTypeID", "PollingPlaceNm",
                              "PremisesNm", "PremisesAddress1", "PremisesAddress2", "PremisesAddress3", "PremisesSuburb",
                              "PremisesStateAb", "PremisesPostCode", "Latitude", "Longitude"]
PREFS_FIELD_NAMES = ["State", "Division", "Vote Collection Point Name", "Vote Collection Point ID", "Batch No", "Paper No"]
NON_BOOTH_CONVERT = {"ABSENT" : "Absent", "POSTAL" : "Postal", "PRE_POLL" : "Pre-Poll", "PROVISIONAL" : "Provisional"}

# for prettier printing
ttyjump = TTYJUMP if hasattr(sys.stderr, "isatty") and sys.stderr.isatty() else ''


def groupCombos(groups):
    '''Generate a list of all the orderings.'''
    combinations = ["None"] # special-casing the empty

    for r in range(len(groups)):
        chooseN = list(itertools.combinations(sorted(groups), r+1))
        #print(chooseN)
        for i in chooseN:
            combinations += ["".join(j) for j in list(itertools.permutations(i))]

    return combinations


def booth_NPPs(SCENARIO, PARTIES, STATE, FORMAL_PREFS_PATH, POLLING_PLACES_PATH, NPP_BOOTHS_PATH):
    '''The actual main processing happens here.'''

    combinations = groupCombos(PARTIES)
    total_combos = len(combinations)

    #print(total_combos)
    #print(combinations)
    #exit()

    ################################

    # Iterate over booth metadata

    booths = {}
    divisionOrdTotals = {}
    divisionSpecials = {}
    PPIds = {}

    # ^^ this too

    with open(POLLING_PLACES_PATH) as boothscsv:

        # 2019 problems: there's a pre-header line. Skip it.
        boothscsv.seek(0)
        next(boothscsv)

        # Onward!
        boothsreader = csv.DictReader(boothscsv, fieldnames=BOOTH_FIELD_NAMES)

        for boothrow in boothsreader:
            #print(boothrow)
            if(boothrow['State'] == STATE):
                booths[boothrow['DivisionNm'] + boothrow['PollingPlaceNm']] = [boothrow['PollingPlaceID'],
                    boothrow['DivisionNm'], boothrow['PollingPlaceNm'], boothrow['Latitude'], boothrow['Longitude']] + [0]*total_combos

    # print(booths)


    #print("*** Distributing Preferences: {}, in {}. ***\n".format(" vs ".join(PARTIES.keys()), STATE), file=sys.stderr)
    print()
    # Iterate over prefs
    with open_csvz(FORMAL_PREFS_PATH) as prefscsv:

        # The primary difference from 2016 to 2019 here is that now everyone has
        # their own column whereas previously they were in almost a sub-csv

        # first in the header we have all the metadata defined in PREFS_FIELD_NAMES
        # and then however many columns it takes for all the (pseudo)candidates

        prefsreader = csv.DictReader(prefscsv)
        progress = 0

        # 2019 problems: we used to index by candidate numbers.
        # We still can but we'll need to rewrite PARTIES a bit
        # also want to properly deal with ATL/BTL

        # first figure out which are BTLs and ATLs
        ATL_start = len(PREFS_FIELD_NAMES) # relative to file in general
        BTL_start = 0 # relative to ATL_start (?)
        for i in prefsreader.fieldnames[ATL_start+1:]:
            # find the second "A:" or if there are none, then presumably we started at "UG:""
            #print(i)
            if i.startswith("A:"):
                BTL_start = prefsreader.fieldnames.index(i) - ATL_start
                break
        #print("ATL_start: ", ATL_start, "BTL_start: ", BTL_start, file=sys.stderr)
        #print([(i, prefsreader.fieldnames[i]) for i in range(len(prefsreader.fieldnames))], file=sys.stderr)

        # Create candidate number index ...
        cand_nums = {prefsreader.fieldnames[ATL_start:][i]: i+1 for i in range(len(prefsreader.fieldnames[ATL_start:]))} # i+1 in there for 1-indexing
        #print(cand_nums, "\n\n", file=sys.stderr)
        # ... and a lookup
        GROUPS = {}
        for p in PARTIES.keys():
            #print(p)
            GROUPS[p] = [cand_nums[c] for c in PARTIES[p]]

        GROUPS_ATL = {}
        GROUPS_BTL = {}
        for p in PARTIES.keys():
            GROUPS_ATL[p] = []
            GROUPS_BTL[p] = []
            for c in PARTIES[p]:
                if cand_nums[c] > BTL_start: #`>` rather than `>=`. BTL-start is zero-indexed, candidate numbers are one-indexed.
                    GROUPS_BTL[p].append(cand_nums[c])
                else:
                    GROUPS_ATL[p].append(cand_nums[c])

        #print("GROUPS", GROUPS, "GROUPS_ATL", GROUPS_ATL, "GROUPS_BTL", GROUPS_BTL)


        # Iterate over all the rows of the main thing
        for prefrow in prefsreader:
            #print(prefrow)
            progress += 1

            # if progress > 10:
            #     exit()


            if (progress % 10000 == 0):
                print(ttyjump+f"... Preferencing progress: {progress:n} ballots", file=sys.stderr)
                #break

            divnm = str(prefrow['Division'])
            boothnm = str(prefrow['Vote Collection Point Name'])

            if divnm.startswith('---'): # 2016 weirdness
                sys.exit("Please use `16to19.py` to first upgrade your old data to the new format.")

            #seq = str(prefrow['Preferences']).split(',')
            # 2019 problems: dealing with the switchover
            seq = list(prefrow.values())[ATL_start:]

            # 2016: Need to convert all to ints and fill in empties
            # 2019: Should be all ints already, but empties need filling still
            seq_ints = [len(seq)] * len(seq) # create prefilled

            for i in range(len(seq)):
                try:
                    seq_ints[i] = int(seq[i])
                except Exception:
                    pass

            #print(seq_ints)

            # Now to analyse 4PP. We categorise the preference sequence by its highest value for each group of candidates


            best = {}
            # first set 'best' to worse than worst for each party (best == 1)
            for i in GROUPS:
                best[i] = len(seq) + 1

            # this should all take into account ATL vs BTL
            is_BTL = (seq_ints[BTL_start:].count(1) == 1) and (seq_ints[BTL_start:].count(2) == 1) and \
                        (seq_ints[BTL_start:].count(3) == 1) and (seq_ints[BTL_start:].count(4) == 1) and \
                        (seq_ints[BTL_start:].count(5) == 1) and (seq_ints[BTL_start:].count(6) == 1)
            ## ^ this seems like a lot but the short-circuits are friendly
            GROUPS = GROUPS_BTL if is_BTL else GROUPS_ATL

            for p in GROUPS:
                for i in GROUPS[p]:
                    if seq_ints[i-1] < best[p]: # the i-1 comes from the [pseudo]candidate numbers being one-indexed
                        best[p] = seq_ints[i-1]

            order = sorted([(best[i], i) for i in GROUPS])

            # Now we test. Exploit the requirements of optional preferential:
            #    items may only be ranked equal-last.

            pref = "".join([i[1] for i in order if i[0] < len(seq)])

            if pref == "":
                pref = "None"

            #if (progress % 10000 == 0):
            #    print(progress, divnm, boothnm)
            #    print(seq_ints, pref, order, "BTL" if is_BTL else "ATL")


            try:
                booths[divnm+boothnm][lenpp + combinations.index(pref)] += 1
            except KeyError:
                # This is a postal/prepoll/etc - booth ID exists, lat/long doesn't, but we're about to aggregate over boothid anyway
                booths[divnm+boothnm] = ['', divnm, boothnm, '', ''] + [0] * total_combos ## ... putting boothid in here broke aggregation
                booths[divnm+boothnm][lenpp + combinations.index(pref)] += 1

    print(ttyjump+f"... Preferencing complete: {progress:n} ballots", file=sys.stderr) # final count
    print("... Aggregating Absents, Postals, Prepolls & Provisionals", file=sys.stderr)


    whichkeys = list(NON_BOOTH_CONVERT.keys())
    boothkeys = list(booths.keys())

    toRemove = []

    for i in boothkeys:
        if booths[i][0] == '':
            #print(booths)
            for w in whichkeys:
                if booths[i][2].startswith(w):
                    try:
                        for j in range(lenpp, len(booths[i])):
                                                #divnm  +   boothbm
                            divisionSpecials[booths[i][1]+NON_BOOTH_CONVERT[w]][j] += booths[i][j]
                    except KeyError:
                        #print(w, NON_BOOTH_CONVERT[w])                        # agg/division       name                actual prefs data
                        divisionSpecials[booths[i][1]+NON_BOOTH_CONVERT[w]] = booths[i][0:2] + [NON_BOOTH_CONVERT[w]] + booths[i][3:]

                    toRemove.append(i)

    for i in toRemove:
        booths.pop(i)

    # print(divisionSpecials)

    booths.update(divisionSpecials)

    ### Sum over booths to generate totals column

    boothkeys = list(booths.keys()) #regen

    for i in boothkeys:
        booths[i].append(sum([int(j) for j in booths[i][5:]]))

    print("... Writing File", file=sys.stderr, end='')

    with open(NPP_BOOTHS_PATH, 'w') as fp:
        print(*(NPP_FIELD_NAMES + combinations + ["Total"]), sep=',', file=fp, flush=True)

        for ids in booths.keys():

            print(*booths[ids], sep=',', file=fp)

    print("... Done!\n", file=sys.stderr)

# end big function

def elastic(ls):
    '''Implement elastic "tabstops" for human display'''
    widths = {}
    for i in ls:
        for c, j in enumerate(i):
            widths[c] = max(len(str(j)), widths.get(c, 0))
    out = []
    for i in ls:
        i_out = ''
        for c, j in enumerate(i):
            i_out += str(j) + " "*(2 + widths[c] - len(str(j)))
        out.append(i_out)
    return out

def make_dirs(OUTPUT_DIR, SCENARIO):
    try:
        os.makedirs(os.path.join(OUTPUT_DIR, SCENARIO))
    except FileExistsError:
        pass # sweet, nothing to do

def main():
    '''Setup and configuration. Calls booth_NPPs(), potentially in a loop.'''

    argparser = argparse.ArgumentParser(description="Perform N-Party-Preferred distribution on Australian Senate ballot data.")
    argparser.add_argument("configfile", type=argparse.FileType('r'), help="configuration file defining paths and scenarios")
    mxg = argparser.add_mutually_exclusive_group(required=True)
    mxg.add_argument("-l", "--list-scenarios", action="store_true", help="list all scenarios as defined in `configfile`, without actually running any of them")
    mxg.add_argument("-a", "--run-all-scenarios", action="store_true", help="run every scenario defined in `configfile`")
    mxg.add_argument("-s", "--scenario", metavar='scenario', action="append", help="run a scenario code defined in `configfile` (can be specified multiple times to run several scenarios)")

    argp = argparser.parse_args()

    confp = configparser.ConfigParser()
    confp.read_file(argp.configfile)

    try:
        if argp.scenario and not (set(argp.scenario).intersection(set(confp.sections()))):
            print(f"Error: no specified scenario is defined.", file=sys.stderr)
        if argp.list_scenarios:
            printme = [["Scenario", "Preferred Parties", "Place", "Year"]]
            for SCENARIO in confp.sections():
                STATE = confp[str(SCENARIO)]['STATE']
                PARTIES = json.loads(confp[str(SCENARIO)]['GROUPS'])
                YEAR = confp[str(SCENARIO)]['YEAR']
                printme.append([SCENARIO, " v. ".join(PARTIES.keys()), STATE, YEAR])
            if hasattr(sys.stdout, "isatty") and sys.stdout.isatty() and len(printme) > 1:
                for c, i in enumerate(elastic(printme)):
                    if c > 0:
                        print(i, file=sys.stdout) # stdout because this isn't diagnostic
                    else:
                        print('\033[1m'+i+'\033[0m', file=sys.stdout) # stdout because this isn't diagnostic
            else:
                for i in printme:
                    print(*i, sep="\t", file=sys.stdout) # also stdout for same reason
        else:
            scenlist = confp.sections() if argp.run_all_scenarios else argp.scenario
            for SCENARIO in scenlist:
                YEAR = confp[SCENARIO]['YEAR']
                PARTIES = json.loads(confp[SCENARIO]['GROUPS'])
                STATE = confp[SCENARIO]['STATE']
                FORMAL_PREFS_PATH = confp[SCENARIO]['PREFS_PATH']
                POLLING_PLACES_PATH = confp[SCENARIO]['POLLING_PLACES_PATH']
                OUTPUT_DIR = confp[SCENARIO]['OUTPUT_DIR']
                NPP_BOOTHS_PATH = os.path.join(OUTPUT_DIR, SCENARIO, confp[SCENARIO]['NPP_BOOTHS_FN'])

                print("*** Running Scenario {}: {}, in {} [{}] ***\n".format(SCENARIO, " vs ".join(PARTIES.keys()), STATE, YEAR), file=sys.stderr)
                make_dirs(OUTPUT_DIR, SCENARIO)
                booth_NPPs(SCENARIO, PARTIES, STATE, FORMAL_PREFS_PATH, POLLING_PLACES_PATH, NPP_BOOTHS_PATH)
    except KeyError as k:
        sys.exit(f"There was an issue with the arguments or configuration file: {k}")

if __name__ == "__main__":
    main()
