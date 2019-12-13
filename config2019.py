# N-Party-Preferred configuration
# You'll need to modify most of these values; hopefully it's straightforward.
# This is the 2019 format. Other years will likely differ.

### Select which variant we want to use (see below for definitions thereof). ###
VARIANT = 'QLD_5PP_KAP'

### Set up potential 'variants'. Prepopulated for convenience###

# GROUPS: define a set of groups for NPP analysis. Required.
#    {'CodeName' : [list of (pseudo)candidates]}
# The AEC's 2019 ballot format eschews ballot numbers in favour of
# ticketcode:name, one per column. Use these to define (pseudo)candidates.
# Tip:   head -n 1 PREFS_PATH | sed -e "s/,/\", \"/g"   will get you 95% there.

# PREFS_PATH: the 'formal preferences' file for a state. Required.

# SA1S_DISTS_PATH: a file mapping SA1s to state-level districts. (Or local!)
# Only required for later stages of analysis; use None otherwise.


VARIANTS = {
    'ACT_2PP' : { 'GROUPS' : {'Alp': ['G:Australian Labor Party', 'G:GALLAGHER Katy', 'G:WAITES Nancy'],
                            'Lib': ['A:Liberal', 'A:SESELJA Zed', 'A:GUNNING Robert']},
              'PREFS_PATH' : "/mnt/Narnia/Psephology/Results/AUS_2019/aec-senate-formalpreferences-24310-ACT.csv",
              'SA1S_DISTS_PATH' : None,
              'STATE': 'ACT'
            },
    'NSW_3PP' : { 'GROUPS' : {'Alp': ["J:Labor/Country Labor", "J:SHELDON Tony", "J:AYRES Tim", "J:LI Jason Yat-Sen", "J:PENGELLY Simonne", "J:CHANDRALA Aruna", "J:SHEAHAN Charlie"],
                            'Lnp': ["D:Liberal & Nationals", "D:HUGHES Hollie", "D:BRAGG Andrew", "D:DAVEY Perin", "D:MOLAN Jim", "D:FARRAWAY Sam", "D:FENELEY Michael"],
                            'Grn': ["G:The Greens", "G:FARUQI Mehreen", "G:JACOBS Rachael", "G:STEER Louise", "G:CLARK Philippa", "G:CHIA Roz", "G:ELLSMORE Sylvie"]},
              'PREFS_PATH' : "/mnt/Narnia/Psephology/Results/AUS_2019/aec-senate-formalpreferences-24310-NSW.csv",
              'SA1S_DISTS_PATH' : None,
              'STATE': 'NSW'
            },
    'NT_2PP' : { 'GROUPS' : {'Alp': ["B:Australian Labor Party (Northern Territory) Branch", "B:McCARTHY Malarndirri", "B:KURNORTH Wayne"],
                            'Lib': ["C:Country Liberals (NT)", "C:McMAHON Sam", "C:BURGOYNE Joshua"]},
              'PREFS_PATH' : "/mnt/Narnia/Psephology/Results/AUS_2019/aec-senate-formalpreferences-24310-NT.csv",
              'SA1S_DISTS_PATH' : None,
              'STATE': 'NT'
            },
    'QLD_4PP' : { 'GROUPS' : {'Alp': ['J:Australian Labor Party', 'J:GREEN Nita', 'J:KETTER Chris', 'J:GILBERT Frank', 'J:MAJOR Tania', 'J:SCHINNERL Stacey', 'J:WARRY Christina'],
                            'Lnp': ['D:Liberal National Party of Queensland', 'D:SCARR Paul', 'D:MCDONALD Susan', 'D:RENNICK Gerard', 'D:MACDONALD Ian', 'D:CAMM Amanda', 'D:TOBIN Nicole'],
                            'Phn': ["B:Pauline Hanson's One Nation", 'B:ROBERTS Malcolm', 'B:DICKSON Steve'],
                            'Grn': ['H:The Greens', 'H:WATERS Larissa', 'H:SIDHU Navdeep Singh', 'H:KLOOT Johanna', 'H:ELLIS Raelene', 'H:BERTRAM Miranda', 'H:KENNEDY Kirsten']},
              'PREFS_PATH' : "/mnt/Narnia/Psephology/Results/AUS_2019/aec-senate-formalpreferences-24310-QLD.csv",
              'SA1S_DISTS_PATH' : None,
              'STATE': 'QLD'
            },
    'QLD_4PP_withKAP' : { 'GROUPS' : {'Alp': ['J:Australian Labor Party', 'J:GREEN Nita', 'J:KETTER Chris', 'J:GILBERT Frank', 'J:MAJOR Tania', 'J:SCHINNERL Stacey', 'J:WARRY Christina'],
                            'Lnp': ['D:Liberal National Party of Queensland', 'D:SCARR Paul', 'D:MCDONALD Susan', 'D:RENNICK Gerard', 'D:MACDONALD Ian', 'D:CAMM Amanda', 'D:TOBIN Nicole'],
                            'Phk': ["B:Pauline Hanson's One Nation", "Q:Katter's Australian Party (KAP)", 'B:ROBERTS Malcolm', 'B:DICKSON Steve', 'Q:MARRIOTT Joy', 'Q:WALLACE Gregory John', 'Q:WEBB Alan'],
                            'Grn': ['H:The Greens', 'H:WATERS Larissa', 'H:SIDHU Navdeep Singh', 'H:KLOOT Johanna', 'H:ELLIS Raelene', 'H:BERTRAM Miranda', 'H:KENNEDY Kirsten']},
              'PREFS_PATH' : "/mnt/Narnia/Psephology/Results/AUS_2019/aec-senate-formalpreferences-24310-QLD.csv",
              'SA1S_DISTS_PATH' : None,
              'STATE' : 'QLD'
            },
    'QLD_5PP_KAP' : { 'GROUPS' : {'Alp': ['J:Australian Labor Party', 'J:GREEN Nita', 'J:KETTER Chris', 'J:GILBERT Frank', 'J:MAJOR Tania', 'J:SCHINNERL Stacey', 'J:WARRY Christina'],
                            'Lnp': ['D:Liberal National Party of Queensland', 'D:SCARR Paul', 'D:MCDONALD Susan', 'D:RENNICK Gerard', 'D:MACDONALD Ian', 'D:CAMM Amanda', 'D:TOBIN Nicole'],
                            'Phn': ["B:Pauline Hanson's One Nation", 'B:ROBERTS Malcolm', 'B:DICKSON Steve'],
                            'Kap': ["Q:Katter's Australian Party (KAP)", 'Q:MARRIOTT Joy', 'Q:WALLACE Gregory John', 'Q:WEBB Alan'],
                            'Grn': ['H:The Greens', 'H:WATERS Larissa', 'H:SIDHU Navdeep Singh', 'H:KLOOT Johanna', 'H:ELLIS Raelene', 'H:BERTRAM Miranda', 'H:KENNEDY Kirsten']},
              'PREFS_PATH' : "/mnt/Narnia/Psephology/Results/AUS_2019/aec-senate-formalpreferences-24310-QLD.csv",
              'SA1S_DISTS_PATH' : None,
              'STATE' : 'QLD'
            },
    'SA_3PP' : { 'GROUPS' : {'Alp': ["O:Australian Labor Party", "O:GALLACHER Alex", "O:SMITH Marielle", "O:GORE Emily", "O:HARRISON Larissa"],
                            'Lib': ["G:Liberal", "G:RUSTON Anne", "G:FAWCETT David", "G:ANTIC Alex", "G:GICHUHI Lucy"],
                            'Grn': ["J:The Greens", "J:HANSON-YOUNG Sarah", "J:SUMNER Major Moogy", "J:ROZITISOLDS Gwydion", "J:SETO Robyn"]},
              'PREFS_PATH' : "/mnt/Narnia/Psephology/Results/AUS_2019/aec-senate-formalpreferences-24310-SA.csv",
              'SA1S_DISTS_PATH' : None,
              'STATE': 'SA'
            },
    'TAS_4PP' : { 'GROUPS' : {'Alp': ["I:Australian Labor Party", "I:BROWN Carol", "I:BILYK Catryna", "I:SHORT John", "I:SINGH Lisa", "I:ROBERTS Wayne", "I:FLANAGAN Robert"],
                            'Lib': ["E:Liberal", "E:COLBECK Richard", "E:CHANDLER Claire", "E:DENISON Tanya"],
                            'Jln': ["L:Jacqui Lambie Network", "L:LAMBIE Jacqui", "L:WILLIAMS Glynn", "L:REYNOLDS Chris"],
                            'Grn': ["D:The Greens", "D:McKIM Nick", "D:HUTCHINSON Helen", "D:MARSH Simone"]},
              'PREFS_PATH' : "/mnt/Narnia/Psephology/Results/AUS_2019/aec-senate-formalpreferences-24310-TAS.csv",
              'SA1S_DISTS_PATH' : None,
              'STATE': 'TAS'
            },
    'VIC_3PP' : { 'GROUPS' : {'Alp': ["X:Australian Labor Party", "X:CICCONE Raffaele", "X:WALSH Jess", "X:MARSHALL Gavin", "X:SARWARA Parvinder", "X:DOUGLAS Karen", "X:CRAWFORD Louise"],
                            'Lnp': ["A:LIBERAL/THE NATIONALS", "A:PATERSON James", "A:HUME Jane", "A:VAN David", "A:RANK Anita", "A:HOPPITT Kyle", "A:MULCAHY Julian"],
                            'Grn': ["V:The Greens (VIC)", "V:RICE Janet", "V:SABARATNAM Apsara", "V:PROCTOR Claire", "V:THOMSON Nakita", "V:BARNES Alice", "V:CAMERON Judy"]},
              'PREFS_PATH' : "/mnt/Narnia/Psephology/Results/AUS_2019/aec-senate-formalpreferences-24310-VIC.csv",
              'SA1S_DISTS_PATH' : None,
              'STATE': 'VIC'
            },
    'WA_3PP' : { 'GROUPS' : {'Alp': ["G:Australian Labor Party", "G:DODSON Patrick", "G:PRATT Louise", "G:HERBERT Alana", "G:FRENCH Thomas", "G:GHOSH Varun", "G:VAUGHAN Alison"],
                            'Lib': ["C:Liberal", "C:REYNOLDS Linda", "C:BROCKMAN Slade", "C:O'SULLIVAN Matt", "C:BOTHA Trischa"],
                            'Grn': ["D:The Greens (WA)", "D:STEELE-JOHN Jordon", "D:WATSON Giz", "D:LONSDALE Heather", "D:KHADKA Bhuwan", "D:van GROOTEL Jacqueline", "D:CAHILL Jordan Louise"]},
              'PREFS_PATH' : "/mnt/Narnia/Psephology/Results/AUS_2019/aec-senate-formalpreferences-24310-WA.csv",
              'SA1S_DISTS_PATH' : None,
              'STATE': 'WA'
            },
}


### Paths for generic/nationwide inputs ###

# The relatively tiny spreadsheet detailing all the polling places
POLLING_PLACES_PATH = "/mnt/Narnia/Psephology/Results/AUS_2019/GeneralPollingPlacesDownload-24310.csv"

# The reasonably large spreadsheet detailing the number of voters from each
#    SA1 at each booth {technically for House, but we compensate}

SA1S_BREAKDOWN_PATH = "/mnt/Narnia/Psephology/Results/AUS_2019/polling-place-by-sa1s-2019.csv"


### Paths for outputs ###

# If blank, current directory
OUTPUTDIR = "AUS_2019"

# If you modify the below items, filenames won't match the README...

# This spreadsheet details NPP preferences by booth
# Will go in OUTPUTDIR/VARIANT/ ...
NPP_BOOTHS_FN = "NPP_Booths.csv"

# This spreadsheet details NPP prefs by SA1
# Will go in OUTPUTDIR/VARIANT/ ...

SA1S_PREFS_FN = "SA1_Prefs.csv"

# This spreadsheet details NPP prefs by district (according to the mapping in
#    SA1S_DISTS_PATH, that is, rather than by federal Divisions)
# Will go in OUTPUTDIR/VARIANT/ ...
NPP_DISTS_FN = "District_NPPs.csv"



################################################################################
### Adapt from 2019 to 2016 variables. DO NOT EDIT. ############################
################################################################################
PARTIES = VARIANTS[VARIANT]['GROUPS']
STATE = VARIANTS[VARIANT]['STATE']
FORMAL_PREFS_PATH = VARIANTS[VARIANT]['PREFS_PATH']
SA1S_DISTRICTS_PATH = VARIANTS[VARIANT]['SA1S_DISTS_PATH']
