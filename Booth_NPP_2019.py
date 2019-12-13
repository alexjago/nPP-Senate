# We want to reduce each unique preference sequence to some ordering
#    of each of the parties. For four parties I believe there are 65 orderings:
#    (0!) + (4 * 1!) + (6 * 2!) + (4 * 3!) + (4!)

# The AEC's file format changed quite a bit from 2016.
# Further, we want to use `Candidate_Collation.py` now...

import csv
from collections import defaultdict
import itertools
import os, os.path
import sys
import configparser
import argparse

from config2019 import * ### Error? See config2019.py
# ^^ for datastructure needs with only stdlib
import Candidate_Collation

# Generate booth data structure (combinations hardcoded):
fieldnames = ["ID", "Division", "Booth", "Latitude", "Longitude"]

combinations = ["None"] # special-casing the empty

for r in range(len(PARTIES)):
    chooseN = list(itertools.combinations(sorted(PARTIES), r+1))
    #print(chooseN)
    for i in chooseN:
        combinations += ["".join(j) for j in list(itertools.permutations(i))]

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

boothfieldnames = ['State','DivisionID','DivisionNm','PollingPlaceID','PollingPlaceTypeID','PollingPlaceNm',
                   'PremisesNm','PremisesAddress1','PremisesAddress2','PremisesAddress3','PremisesSuburb',
                   'PremisesStateAb','PremisesPostCode','Latitude','Longitude']

with open(POLLING_PLACES_PATH) as boothscsv:

    # 2019 problems: there's a pre-header line. Skip it.
    boothscsv.seek(0)
    next(boothscsv)

    # Onward!
    boothsreader = csv.DictReader(boothscsv, fieldnames=boothfieldnames)

    for boothrow in boothsreader:
        #print(boothrow)
        if(boothrow['State'] == STATE):
            booths[boothrow['DivisionNm'] + boothrow['PollingPlaceNm']] = [boothrow['PollingPlaceID'],
                boothrow['DivisionNm'], boothrow['PollingPlaceNm'], boothrow['Latitude'], boothrow['Longitude']] + [0]*total_combos

# print(booths)


#with open(newpollingplacesfn, 'w') as fp:
#    print(*fieldnames, sep=',', file=fp, flush=True)

print("*** Distributing Preferences ***", file=sys.stderr)
print("    {}, in {}\n".format(" vs ".join(PARTIES.keys()), STATE), file=sys.stderr)

# Iterate over prefs
with open(FORMAL_PREFS_PATH, newline='') as prefscsv:

    # allrows = [row for row in prefscsv]

    # The primary difference from 2016 to 2019 here is that now everyone has
    # their own column whereas previously they were in almost a sub-csv

    # first in the header we have all the metadata
    fixedhead = ["State", "Division", "Vote Collection Point Name", "Vote Collection Point ID", "Batch No", "Paper No"]
    # and then however many columns it takes for all the (pseudo)candidates

    prefsreader = csv.DictReader(prefscsv)
    progress = 0

    # 2019 problems: we used to index by candidate numbers.
    # We still can but we'll need to rewrite PARTIES a bit

    # Create candidate number index
    cand_nums = {prefsreader.fieldnames[5:][i]: i for i in range(len(prefsreader.fieldnames[5:]))}
    #print(PARTIES)
    # and a lookup
    GROUPS = {}
    for p in PARTIES.keys():
        GROUPS[p] = [cand_nums[c] for c in PARTIES[p]]
    #print(GROUPS)

    # Iterate over all the rows of the main thing
    for prefrow in prefsreader:
        #print(prefrow)
        progress += 1

#        if progress > 10:
#            break

        if (progress % 100000 == 0):
            if hasattr(sys.stderr, "isatty") and sys.stderr.isatty():
                print('\033[F'+"    Preferencing:\t", progress, file=sys.stderr)
            else:
                print("    Preferencing:\t", progress, file=sys.stderr)
            #break

        divnm = str(prefrow['Division'])
        boothnm = str(prefrow['Vote Collection Point Name'])

        if divnm[0] == '-':
            continue

        #seq = str(prefrow['Preferences']).split(',')
        # 2019 problems: dealing with the switchover
        seq = list(prefrow.values())[6:]

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

        for p in GROUPS:
            for i in GROUPS[p]:
                if seq_ints[i-1] < best[p]:
                    best[p] = seq_ints[i-1]

        order = sorted([(best[i], i) for i in GROUPS])

        # Now we test. Exploit the requirements of optional preferential:
        #    items may only be ranked equal-last.

        pref = "".join([i[1] for i in order if i[0] < len(seq)])

        if pref == "":
            pref = "None"

#        print(pref)

        try:
            booths[divnm+boothnm][5 + combinations.index(pref)] += 1
        except KeyError:
            booths[divnm+boothnm] = ['', divnm, boothnm, '', ''] + [0] * total_combos
            booths[divnm+boothnm][5 + combinations.index(pref)] += 1

print("\n*** Aggregating Absents/Postals/Prepolls/Provisionals ***", file=sys.stderr)

which = {"ABSENT" : "Absent", "POSTAL" : "Postal", "PRE_POLL" : "Pre-Poll", "PROVISIONAL" : "Provisional"}

whichkeys = list(which.keys())
boothkeys = list(booths.keys())

toRemove = []

for i in boothkeys:
    if booths[i][0] == '':
        for w in whichkeys:
            if booths[i][2].startswith(w):
                try:
                    for j in range(5, len(booths[i])):
                        divisionSpecials[booths[i][1]+which[w]][j] += booths[i][j]
                except KeyError:
                    divisionSpecials[booths[i][1]+which[w]] = booths[i][0:2] + [which[w]] + booths[i][3:]
                toRemove.append(i)

for i in toRemove:
    booths.pop(i)

# print(divisionSpecials)

booths.update(divisionSpecials)

### Sum over booths to generate totals column

boothkeys = list(booths.keys()) #regen

for i in boothkeys:
    booths[i].append(sum([int(j) for j in booths[i][5:]]))

print("*** Writing File ***", file=sys.stderr)

npp_fn = os.path.join(OUTPUTDIR, VARIANT, NPP_BOOTHS_FN)

try:
    os.makedirs(os.path.join(OUTPUTDIR, VARIANT))
except FileExistsError:
    pass # sweet, nothing to do

with open(npp_fn, 'w') as fp:
    print(*(fieldnames + combinations + ["Total"]), sep=',', file=fp, flush=True)

    for ids in booths.keys():

        print(*booths[ids], sep=',', file=fp)

print("*** Done! ***", file=sys.stderr)
