# This script:

# (1): takes SA1-by-SA1 NPP data
# (2): takes SA1 population & district split data
# (3): scales (1) to fit [the totals of] (2)
# (4): splits (3) according to (2) where necessary
# (5): aggregates (4) by district

import csv
import sys
import os.path

from config import *


# (1): takes SA1-by-SA1 4PP data

sa1s_prefs_fn = os.path.join(OUTPUTDIR, STATE, SA1S_PREFS_FN)

sa1s_dists_fn = SA1S_DISTRICTS_PATH

output_fn = os.path.join(OUTPUTDIR, STATE, NPP_DISTS_FN)

aec_sa1s = {}

districts = {}

outfieldnames = []

print("Progress:\t loading", file=sys.stderr)

with open(sa1s_prefs_fn) as consol_sa1s_fp:
    
    consolreader = csv.reader(consol_sa1s_fp)
    
    outfieldnames = next(consolreader)

    for row in consolreader:
        aec_sa1s[row[0]] = row[1:]

print("Progress:\t accumulating", file=sys.stderr)

with open(sa1s_dists_fn) as ecq_sa1s_fp:

    ecqreader = csv.reader(ecq_sa1s_fp)

    ecqheaders = next(ecqreader)

    for i in ecqreader: # this will start from the first actual data, yay
        try:
            aec_sa1 = aec_sa1s[i[0]]
        except KeyError:
            continue
        
        try:                        
            multiplier = float(i[2])/float(aec_sa1[-1])
        except ZeroDivisionError:
            ecq_total = 0.0
            multiplier = 0.0

        if i[1] in districts:
            for j in range(len(districts[i[1]])):
                districts[i[1]][j] += float(aec_sa1[j]) * multiplier
        else:
            districts[i[1]] = [float(j) * multiplier for j in aec_sa1]


print("Progress:\t writing", file=sys.stderr)


with open(output_fn, 'w') as output_fp:

    print("District", *outfieldnames[1:], sep = ",", file = output_fp)

    dists_sorted = sorted([[d] + districts[d] for d in districts.keys()])

    for d in dists_sorted:
        print(*d, sep = ",", file = output_fp)

print("Progress:\t done", file=sys.stderr)

    
        

        
    
    

