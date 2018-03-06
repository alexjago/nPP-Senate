# N-Party-Preferred configuration
# You'll need to modify most of these values; hopefully it's straightforward.
# This is the 2016 format. Other years will likely differ.

##STATE = 'SA'
STATE = 'QLD'

### How many parties do we care about and where are those parties' candidates?
# Numbers are as follows: Group A Ticket, Group B Ticket, ... , final Ticket,
#   Group A Candidate 1, Group A Candidate 2, ... , final Ungrouped Candidate

### SA
##PARTIES = {
##    'ALP' : [2, 26, 27, 28, 29, 30, 31],
##    'Lib' : [8, 46, 47, 48, 49, 50, 51],
##    'NXT' : [6, 40, 41, 42, 43]
##}

# Qld
PARTIES = {
    'Grn' : [37, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139],
    'Lab' : [4, 45, 46, 47, 48, 49, 50],
    'Lnp' : [7, 55, 56, 57, 58, 59, 60, 61, 62],
    'Phn' : [24, 99, 100, 101, 102]
}

### Paths to input spreadsheets ###

# The giant spreadsheet of formal preferences (one per state/territory)

### SA
##FORMAL_PREFS_PATH = "/Volumes/Tardis/Documents Archive/Electoral Results/Federal-2016/South Australia/aec-senate-formalpreferences-20499-SA.csv"

# QLD
FORMAL_PREFS_PATH = "/Volumes/Tardis/Documents Archive/Electoral Results/Federal-2016/aec-senate-formalpreferences-20499-QLD.csv"


# The relatively tiny spreadsheet detailing all the polling places (nationwide)
POLLING_PLACES_PATH = "/Volumes/Tardis/Documents Archive/Electoral Results/Federal-2016/GeneralPollingPlacesDownload-20499.csv"

# The reasonably large spreadsheet detailing the number of voters from each
#    SA1 at each booth {technically for House, but we compensate} (nationwide)

SA1S_BREAKDOWN_PATH = "/Volumes/Tardis/Documents Archive/Electoral Results/Federal-2016/polling-place-by-sa1s-2016.csv"

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


