# N-Party-Preferred configuration
# You'll need to modify most of these values; hopefully it's straightforward.
# This is the 2016 format. Other years will likely differ.

STATE = '3PP_WA'

##STATE = 'ACT'
##STATE = 'NSW'
##STATE = 'NT'
##STATE = 'QLD'
##STATE = 'SA'
##STATE = 'TAS'
##STATE = 'VIC'
##STATE = 'WA'

### How many parties do we care about and where are those parties' candidates?
# Numbers are as follows: Group A Ticket, Group B Ticket, ... , final Ticket,
#   Group A Candidate 1, Group A Candidate 2, ... , final Ungrouped Candidate

# Included and commented out are nPP sets for 2016's winning parties. I've ordered
# them left to right. Hopefully the acronyms make sense - you can change them.

### ACT 2PP
# PARTIES = {
#    'Lab' : [3, 15, 16],
#    'Lib' : [6, 21, 22]
#  }

### ACT 3PP
#PARTIES = {
#   'Grn' : [8, 19, 20],
#   'Lab' : [3, 15, 16],
#   'Lib' : [6, 21, 22]
# }

### NSW 5PP
#PARTIES = {
#    'Grn' : [38, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166],
#    'Lab' : [14, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95],
#    'Ldp' : [4, 50, 51],
#    'Lnp' : [6, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65],
#    'Phn' : [19, 105, 106, 107]
#    }

### NSW 3PP
#PARTIES = {
#    'Grn' : [38, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166],
#    'Lab' : [14, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95],
#    'Lnp' : [6, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65]
#    }


### NT 2PP
#PARTIES = {
#    'Lab' : [6, 18, 19],
#    'Clp' : [5, 16, 17]
#    }

### NT 3PP
#PARTIES = {
#    'Grn' : [4, 14, 15],
#    'Lab' : [6, 18, 19],
#    'Clp' : [5, 16, 17]
#    }

### Qld 4PP
##PARTIES = {
##     'Grn' : [37, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139],
##     'Lab' : [4, 45, 46, 47, 48, 49, 50],
##     'Lnp' : [7, 55, 56, 57, 58, 59, 60, 61, 62],
##     'Phn' : [24, 99, 100, 101, 102]
##     }

### QldHanson weirdness
## PARTIES = {
##	'Tik' : [24],
##	'Han' : [99],
##	'Rob' : [100],
##	'Oth' : [101, 102]
## }

### Qld Grn-3PP
#PARTIES = {
#     'Grn' : [37, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139],
#     'Lab' : [4, 45, 46, 47, 48, 49, 50],
#     'Lnp' : [7, 55, 56, 57, 58, 59, 60, 61, 62]
#     }

### SA [3PP for state election modelling]
#PARTIES = {
#    'Lab' : [2, 26, 27, 28, 29, 30, 31],
#    'NXT' : [6, 40, 41, 42, 43],
#    'Lib' : [8, 46, 47, 48, 49, 50, 51]
#    }

# SA 5PP
##PARTIES = {
##    'Grn' : [4, 34, 35, 36, 37],
##    'Lab' : [2, 26, 27, 28, 29, 30, 31],
##    'Nxt' : [6, 40, 41, 42, 43],
##    'Lib' : [8, 46, 47, 48, 49, 50, 51],
##    'Ffp' : [14, 62, 63]
##    }

### SA Grn-3PP
#PARTIES = {
#    'Grn' : [4, 34, 35, 36, 37],
#    'Lab' : [2, 26, 27, 28, 29, 30, 31],
#    'Lib' : [8, 46, 47, 48, 49, 50, 51]
#    }


### Tas 4PP
#PARTIES = {
#    'Grn' : [3, 30, 31, 32],
#    'Lab' : [2, 24, 25, 26, 27, 28, 29],
#    'Jln' : [13, 56, 57, 58],
#    'Lib' : [6, 37, 38, 39, 40, 41, 42]
#    }

# Tas Grn-3PP
#PARTIES = {
#    'Grn' : [3, 30, 31, 32],
#    'Lab' : [2, 24, 25, 26, 27, 28, 29],
#    'Lib' : [6, 37, 38, 39, 40, 41, 42]
#    }

### Vic 4PP
#PARTIES = {
#    'Grn' : [37, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136],
#    'Lab' : [4, 45, 46, 47, 48, 49, 50, 51, 52],
#    'Dhj' : [1, 39, 40],
#    'Lnp' : [32, 110, 111, 112, 113, 114, 115, 116]
#    }

### Vic 3PP
#PARTIES = {
#    'Grn' : [37, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136],
#    'Lab' : [4, 45, 46, 47, 48, 49, 50, 51, 52],
#    'Lnp' : [32, 110, 111, 112, 113, 114, 115, 116]
#    }


### WA 4PP
#PARTIES = {
#    'Grn' : [10, 54, 55, 56, 57, 58, 59],
#    'Lab' : [4, 35, 36, 37, 38, 39, 40, 41],
#    'Lib' : [24, 87, 88, 89, 90, 91, 92, 93],
#    'Phn' : [18, 74, 85, 76]
#}

### WA 3PP
PARTIES = {
    'Grn' : [10, 54, 55, 56, 57, 58, 59],
    'Lab' : [4, 35, 36, 37, 38, 39, 40, 41],
    'Lib' : [24, 87, 88, 89, 90, 91, 92, 93]
}


### Paths to input spreadsheets ###

# The giant spreadsheet of formal preferences (one per state/territory)

### ACT
#FORMAL_PREFS_PATH = "/media/Narnia/Psephology/Results/AUS_2016/aec-senate-formalpreferences-20499-ACT.csv"

### NSW
#FORMAL_PREFS_PATH = "/media/Narnia/Psephology/Results/AUS_2016/aec-senate-formalpreferences-20499-NSW.csv"

### NT
#FORMAL_PREFS_PATH = "/media/Narnia/Psephology/Results/AUS_2016/aec-senate-formalpreferences-20499-NT.csv"

# QLD
#FORMAL_PREFS_PATH = "/media/Narnia/Psephology/Results/AUS_2016/aec-senate-formalpreferences-20499-QLD.csv"

### SA
#FORMAL_PREFS_PATH = "/media/Narnia/Psephology/Results/AUS_2016/aec-senate-formalpreferences-20499-SA.csv"

### TAS
#FORMAL_PREFS_PATH = "/media/Narnia/Psephology/Results/AUS_2016/aec-senate-formalpreferences-20499-TAS.csv"

### VIC
#FORMAL_PREFS_PATH = "/media/Narnia/Psephology/Results/AUS_2016/aec-senate-formalpreferences-20499-VIC.csv"

### WA
FORMAL_PREFS_PATH = "/media/Narnia/Psephology/Results/AUS_2016/aec-senate-formalpreferences-20499-WA.csv"

# The relatively tiny spreadsheet detailing all the polling places (nationwide)
POLLING_PLACES_PATH = "/media/Narnia/Psephology/Results/AUS_2016/GeneralPollingPlacesDownload-20499.csv"

# The reasonably large spreadsheet detailing the number of voters from each
#    SA1 at each booth {technically for House, but we compensate} (nationwide)

SA1S_BREAKDOWN_PATH = "/media/Narnia/Psephology/Results/AUS_2016/polling-place-by-sa1s-2016.csv"

# A spreadsheet mapping SA1s to districts
SA1S_DISTRICTS_PATH = "/Volumes/Tardis/Documents Archive/Redistributions/Qld-State-2016/Final/ESRI-SA1/ecq_sa1s_splitshare.csv"

### Paths to output spreadsheets

# If blank, current directory
OUTPUTDIR = ""

# If you modify the below items, filenames won't match the README...

# This spreadsheet details NPP preferences by booth
# Will go in OUTPUTDIR/STATE/ ...
NPP_BOOTHS_FN = "NPP_Booths.csv"

# This spreadsheet details NPP prefs by SA1
# Will go in OUTPUTDIR/STATE/ ...

SA1S_PREFS_FN = "SA1_Prefs.csv"

# This spreadsheet details NPP prefs by district (according to the mapping in
#    SA1S_DISTRICTS_PATH, that is, rather than by federal Divisions)
# Will go in OUTPUTDIR/STATE/ ...
NPP_DISTS_FN = "District_NPPs.csv"
