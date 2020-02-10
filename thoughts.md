# Thoughts

## Configuration

Ideally, we would be using .ini files for config instead of .py

YAML or TOML would be better but need a third party module. Goal is for only stdlib imports. JSON is yuck for this.

Also rename VARIANT to SCENARIO - it"s more obvious what"s going on then.

The main issue is the nesting and strings.

Currently we have:

        VARIANTS = {"VariantName" :
            {"GROUPS":
                {PartyName : [pseudocandidates]}
             "OtherSettings" : ...
            }
        }

Represented as an INI we could make the case for top level `[VariantNames]`... but we"d arguably need an extra field for

All values out of a ConfigParser are treated as *strings*, so we can effectively do things like `json.loads(value)` if we want. This actually solves the problem.

So a sensible config file looks a lot like this (and there should be one for each election year).
Note the lack of a defined variant - I've decided that this should be done at runtime.

        [DEFAULT]
        # This section is special; it has all of the top-level information.
        # You can refer to values in this section, even from other sections, like so: %{ValueName}s

        # Inputs        
        YEAR = 2019
        DATA_DIR = /mnt/Narnia/Psephology/Results/AUS_2019
        POLLING_PLACES_PATH = %{DATA_DIR}s/GeneralPollingPlacesDownload-24310.csv
        SA1S_BREAKDOWN_PATH = %{DATA_DIR}s/polling-place-by-sa1s-2019.csv

        # Outputs (can be overridden in individual Scenarios)
        OUTPUT_DIR = AUS_%{YEAR}s
        # These will go in OUTPUT_DIR/Scenario/ ...
        NPP_BOOTHS_FN = NPP_Booths.csv
        SA1S_PREFS_FN = SA1_Prefs.csv
        NPP_DISTS_FN = District_NPPs.csv


        [ACT_3PP]
        # This and other non-DEFAULT sections define "Scenarios" - sets of competing groups of [pseudo]candidates.

        # Note the structure of GROUPS, and that all names must be enclosed with double quotes
        #   {"GroupLabel" : ["GroupMember", ...], ...}
        # (The value of GROUPS is actually a JSON array...)
        # You can (and should) indent for readability - just remember to outdent for the next key!
        GROUPS = {"Alp": ["G:Australian Labor Party", "G:GALLAGHER Katy", "G:WAITES Nancy"],
                  "Lib": ["A:Liberal", "A:SESELJA Zed", "A:GUNNING Robert"],
                  "Grn": ["B:The Greens", "B:KYBURZ Penny", "B:DAVIDSON Emma"]}     

        # Where the actual preferences path is.
        PREFS_PATH = %{DATA_DIR}s/aec-senate-formalpreferences-24310-ACT.csv

        # This file maps SA1s to districts at state or local level.
        # If it doesn't exist, leave off the ` = path`
        SA1s_DISTS_PATH

        # Finally, the state (or territory!) that this scenario applies to.
        STATE = ACT

And yeah, that's pretty much it bar the shouting (and the coding).

Maybe this is the ultimate outcome of Candidate_Collation? Interactive config file generation?

## One Thing To Run Them All.

Ideally we'd do something like

    npp ((--generate | --list | --distribute --project --combine (--all | --scenario scenario1 ...)) configfile | --upgrade infile outfile

or better (notes below):

    npp
    |____ upgrade   # [1]
    |     |______ prefs candidatesfile input output
    |     |______ sa1s correspondencefile [< infile] [> outfile]
    |____ generate [--from prevfile] [>> configfile]    # [2]
    |____ list [< configfile] [>]   # [3]
    |____ run (--distribute --project --combine) (--all | --scenario scenario) configfile   # [4,5,6]
    |____ gui   # [7]

1. `upgrade --prefs` should just auto-figure-out which year it is getting and then upgrade to latest. The angle brackets are to suggest < for "can use stdin" and > for "can use stdout". Drop the `--no-infile-headers` thing; figure it out from first field of first line.
2. Also should be able to use a previous file as a base, hence `--from`
3. Basically just like it did on 02/02/2020. Outputs just to stdout.
4. `--distribute --project --combine` aren't strictly necessary - just run everything as far as it can go based on what filenames are defined. If an option *is* set, do just that stage (mutex options).
5. `--all` and `--scenario` are mutex options; `--scenario` should be either `nargs='+'` or `action='append'`.
6. We absolutely rely on `configfile` at this point. It shouldn't be optional. The question is, can it run from stdin? I think not.
7. The effective default: `npp` with no arguments should be `npp gui`. Takes no arguments - everything will be handled graphically.


## ZipApp.

All of this also requires putting things into a module better. This also ties in with `zipapp`.
