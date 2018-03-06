# We want to reduce each unique preference sequence to some ordering
#    of each of the parties. For four parties I believe there are 65 orderings:
#    (0!) + (4 * 1!) + (6 * 2!) + (4 * 3!) + (4!)

import csv
from collections import defaultdict
import itertools
import os, os.path

from config import *

# Generate booth data structure (combinations hardcoded):
fieldnames = ["ID", "Division", "Booth", "Latitude", "Longitude"]

combinations = ["None"] # special-casing the empty

for r in range(len(PARTIES)):
    chooseN = list(itertools.combinations(sorted(PARTIES), r+1))
    for i in chooseN:
        combinations += ["".join(j) for j in list(itertools.permutations(i))]

total_combos = len(combinations)

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
    boothsreader = csv.DictReader(boothscsv, fieldnames=boothfieldnames)

    for boothrow in boothsreader:
##        print(boothrow)
        if(boothrow['State'] == STATE):
            booths[boothrow['DivisionNm'] + boothrow['PollingPlaceNm']] = [boothrow['PollingPlaceID'],
                                                                           boothrow['DivisionNm'], boothrow['PollingPlaceNm'],
                                                                           boothrow['Latitude'], boothrow['Longitude']] + [0]*total_combos

#with open(newpollingplacesfn, 'w') as fp:
#    print(*fieldnames, sep=',', file=fp, flush=True)    

print("*** Distributing Preferences ***", file=sys.stderr)

# Iterate over prefs
with open(FORMAL_PREFS_PATH, newline='') as prefscsv:

    allrows = [row for row in prefscsv]
    
    prefsreader = csv.DictReader(allrows)

    progress = 0

    # Iterate over all the rows of the main thing
    for prefrow in prefsreader:

        progress += 1

##        if progress > 10:
##            break

        if (progress % 100000 == 0):
            print("Preferencing:\t", progress, file=sys.stderr)
##            break

        divnm = str(prefrow['ElectorateNm'])
        boothnm = str(prefrow['VoteCollectionPointNm'])

        if divnm[0] == '-':
            continue
        
        seq = str(prefrow['Preferences']).split(',')

        # Need to convert all to ints and fill in empties

        seq_ints = [len(seq)] * len(seq)
        
        for i in range(len(seq)):
            if seq[i].isnumeric():
                seq_ints[i] = int(seq[i])

#        print(seq_ints)

        # Now to analyse 4PP. We categorise the preference sequence by its highest value for each group of candidates

        best = {}

        # first set 'best' to worse than worst for each party (best == 1)
        for i in PARTIES:
            best[i] = len(seq) + 1

        for p in PARTIES:        
            for i in PARTIES[p]:
                if seq_ints[i-1] < best[p]:
                    best[p] = seq_ints[i-1]

        order = sorted([(best[i], i) for i in PARTIES])

#        print(order)

        
        # Now we test. Exploit the requirements of optional preferential:
        #    items may only be ranked equal-last.

        pref = "".join([i[1] for i in order if i[0] < len(seq)])

        if pref == "":
            pref = "None"

#        print(pref)

#        exit()

        try:
            booths[divnm+boothnm][5 + combinations.index(pref)] += 1
        except KeyError:
            booths[divnm+boothnm] = ['', divnm, boothnm, '', ''] + [0] * total_combos
            booths[divnm+boothnm][5 + combinations.index(pref)] += 1

print("*** Aggregating Absents/Postals/Prepolls/Provisionals ***", file=sys.stderr)

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

npp_fn = os.path.join(OUTPUTDIR, STATE, NPP_BOOTHS_FN)

try:
    os.makedirs(os.path.join(OUTPUTDIR, STATE))
except FileExistsError:
    pass # sweet, nothing to do

with open(npp_fn, 'w') as fp:
    print(*(fieldnames + combinations + ["Total"]), sep=',', file=fp, flush=True)

    for ids in booths.keys():
        
        print(*booths[ids], sep=',', file=fp)

print("*** Done! ***", file=sys.stderr)




        
        

        
            
        

                        

