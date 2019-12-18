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

# NB update relevant config file name here
from config2019 import *

# deal with 2016/2019 changes
npp_fn = os.path.join(OUTPUTDIR, VARIANT, NPP_BOOTHS_FN) if VARIANT else os.path.join(OUTPUTDIR, STATE, NPP_BOOTHS_FN)

# Generate booth data structure (combinations hardcoded):
nppfields = ["ID", "Division", "Booth", "Latitude", "Longitude"]

combinations = ["None"] # special-casing the empty

for r in range(len(PARTIES)):
    chooseN = list(itertools.combinations(sorted(PARTIES), r+1))
    for i in chooseN:
        combinations += ["".join(j) for j in list(itertools.permutations(i))]

total_combos = len(combinations)



### Load in booth data

booths = {}

boothsfields = nppfields+combinations+["Total"]

with open(npp_fn) as consolcsv:
    consolreader = csv.DictReader(consolcsv) # fieldnames implicit from the first line

    for row in consolreader:
        booths[row["Division"]+row["Booth"]] = row # key by 'divbooth'


###

lines = []

# So we'll have 7 columns of stuff before the prefs start:
sa1sfields = ["year","state_ab", "div_nm", "SA1_id", "pp_id", "pp_nm", "votes"]

with open(SA1S_BREAKDOWN_PATH) as sa1scsv:

    sa1sreader = csv.DictReader(sa1scsv) # fieldnames implicit from the first line

    progress = 0

    for srow in sa1sreader:

        # deal with state weirdness
        if not ((srow["year"] in ["2016", "2019"]) and srow["state_ab"]==STATE):
            continue

##        if (progress == 10):
##            break

        # basically a big vector multiply

        bob = [srow["SA1_id"]]
        db = [ booths[srow["div_nm"]+srow["pp_nm"]][i] for i in boothsfields[5:] ]
##        print("db:\t", db)
        for i in range(len(db)):
            try:
                bob.append(float(srow["votes"]) * float(db[i]) / float(db[-1]))
            except ZeroDivisionError:
                bob.append(0.0)

        lines.append(bob)

##        print("bob:\t", bob)

        progress+= 1
        if (progress % 10000 == 0):
            print("Multiply:\t", progress, file=sys.stderr)


### Hmm... 200 MB file. pivot table would go badly.
# Let's do the accumulation phase here too.

sa1s = {}

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

print("Progress:\t Writing File...", file=sys.stderr)

sa1s_prefs_fn = os.path.join(OUTPUTDIR, VARIANT, SA1S_PREFS_FN) if VARIANT else os.path.join(OUTPUTDIR, STATE, SA1S_PREFS_FN)

with open(sa1s_prefs_fn, 'w') as fp:
    print(*(["SA1_id"] + boothsfields[5:]), sep=',', file=fp, flush=True)

    for line in outlines:
        print(*line, sep=',', file=fp)

print("Progress:\t Done!", file=sys.stderr)
