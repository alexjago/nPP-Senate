#!/usr/bin/env python3

# This is a script to generate configuration files for the rest of `npp`

import os
import sys
import argparse
import csv
import configparser
import json
import re
import os.path
import readline # for input things
from collections import OrderedDict

from npp_utils import *
import term
import aec_downloads


def interpolate(thingval, scenario, confp):
    # find %(...)s and substitute
    pattern = re.compile(r'(\%\((\w+)\)s)')
    stringyboi = thingval
    searchme = pattern.search(stringyboi)
    while searchme:
        gg = searchme.group(1, 2)
        repl = confp.get('DEFAULT', gg[1])
        stringyboi = stringyboi.replace(gg[0], repl)
        searchme = pattern.search(stringyboi)
    else:
        return stringyboi
### end

def load_config_from_file(cf):
    '''Returns a dict matching the configuration file.
       Correctly handles the JSON bits and bobs. And the paths.
    '''
    out = {}

    with cf:
        confp = configparser.ConfigParser()
        confp.read_file(cf)

        out = {}

        out['DEFAULT'] = dict(confp.defaults())

        #print(out)

        out['DEFAULT_INTERPOLATED'] = {}

        for thing in out['DEFAULT']:
            out['DEFAULT_INTERPOLATED'][thing] = interpolate(out['DEFAULT'].get(thing.lower(), ''), 'DEFAULT', confp)

        for SCENARIO in confp.sections():
            out[SCENARIO] = {}
            OUTPUT_DIR = confp[SCENARIO]['OUTPUT_DIR']

            # special treatment
            out[SCENARIO]['NPP_BOOTHS_PATH'] = os.path.join(OUTPUT_DIR, SCENARIO, confp[SCENARIO]['NPP_BOOTHS_FN'])
            out[SCENARIO]['NPP_DISTS_PATH'] = os.path.join(OUTPUT_DIR, SCENARIO, confp[SCENARIO]['NPP_DISTS_FN'])
            out[SCENARIO]['GROUPS'] = json.loads(confp[SCENARIO]['GROUPS'])
            out[SCENARIO]['SA1S_PREFS_PATH'] = os.path.join(OUTPUT_DIR, SCENARIO, confp[SCENARIO]['SA1S_PREFS_FN'])

            # just a copy, but don't bother if it's the same as the default or it doesn't exist
            for thing in ['SA1S_BREAKDOWN_PATH', 'YEAR', 'STATE', 'NPP_BOOTHS_FN', 'NPP_DISTS_FN', 'SA1S_PREFS_FN', 'PREFS_PATH', 'POLLING_PLACES_PATH', 'SA1S_DISTS_PATH']:
                interpolated_default = interpolate(out['DEFAULT'].get(thing.lower(), ''), SCENARIO, confp)
                if (confp.get(SCENARIO, thing) != interpolated_default):
                    out[SCENARIO][thing] = confp.get(SCENARIO, thing)
                else:
                    pass

    return out
### end

def dumpgroups(obj):
    '''Just wraps json.dumps() and does a couple of presentational line breaks at the end of arrays'''
    from json import dumps

    if isinstance(obj, str):
        return obj
    else:
        return "],\n     ".join(dumps(obj).split('],'))


def addScenarios(args, existing_config, new_config, aec_files_dict, all_cands):
    '''Create new scenarios. Returns a an updated version of new_config.'''

    # Loop:
    # - new Group
    # - select candidates (by search?)
    # - finalise Group

    newScen = input("Define a new Scenario? [Y]/n: ").upper()
    while newScen.startswith('Y') or not newScen:

        scenario = {'GROUPS': None,
                    'PREFS_PATH': None,
                    'YEAR': None,
                    'STATE': None,
                    'SA1S_DISTS_PATH': None,
                    'OUTPUT_DIR': None,
                    'SA1S_BREAKDOWN_PATH': None,
                    'POLLING_PLACES_PATH': None}

        # oh god why are there so many things

        data_dir_dict = {}
        dist_dir_dict = {}

        data_dir = os.path.realpath(args.data_dir) if args.data_dir else existing_config['DEFAULT_INTERPOLATED'].get('data_dir', '')
        if data_dir:
            new_config.set(new_config.default_section, 'DATA_DIR', data_dir)

        dist_dir = os.path.realpath(args.dist_dir) if args.dist_dir else existing_config['DEFAULT_INTERPOLATED'].get('dist_dir', '')
        if dist_dir:
            new_config.set(new_config.default_section, 'DIST_DIR', dist_dir)


        # Get initial, important data

        state_choices = all_cands.keys()
        while scenario['STATE'] not in state_choices:
            scenario['STATE'] = input("Pick a state or territory for your scenario:\n Options are "+', '.join(state_choices)+ ": ")

        if existing_config['DEFAULT_INTERPOLATED'].get('year'):
            scenario['YEAR'] = existing_config['DEFAULT_INTERPOLATED'].get('year')
        else:
            year = ''
            while not year:
                year = input("Input the year of this Scenario: ")
            scenario['YEAR'] = year

        # Let's get some more DEFAULTS
        data_dir_dict = walk_filesystem(data_dir, aec_files_dict, aec=True)
        dist_dir_dict = walk_filesystem(dist_dir,
            {scenario['YEAR']: {"SA1s_Electorates.csv": "SA1S_DISTS_PATH", "SA1s_Districts.csv": "SA1S_DISTS_PATH", "SA1s_Wards.csv": "SA1S_DISTS_PATH"}},
            aec=False, state=scenario['STATE'])
        # with dist_dir it's basically just hints and hopes

        print(data_dir_dict)

        party_details = None
        if args.party_details:
            party_details = args.party_details
        elif 'PARTY_DETAILS' in data_dir_dict.get(scenario['YEAR'], {}):
            party_details = open(data_dir_dict[scenario['YEAR']]['PARTY_DETAILS'], 'r')

        party_abs = read_party_abbrvs(party_details) if party_details else None

        #print(data_dir_dict)
        #print(dist_dir_dict)

        # Prompt for input where needed
        # these are for the ones with multiples
        press_return = "(press RETURN to skip)"
        input_a_path = "Please input a path to the file "
        prompts = \
        { 'PREFS_PATH': f"containing the formal preferences of this Scenario {press_return}:\n",
          'SA1S_DISTS_PATH': f"containing the SA1s-to-Districts mapping of this Scenario {press_return}:\n",
          'SA1S_BREAKDOWN_PATH': "containing the Polling-Places-to-SA1s mapping in ",
          'POLLING_PLACES_PATH': "describing Australian polling booths in "
          }

        if existing_config['DEFAULT_INTERPOLATED'].get('prefs_path'):
            scenario['PREFS_PATH'] = existing_config['DEFAULT_INTERPOLATED'].get('prefs_path')
        else:
            if data_dir:
                if scenario['STATE'] in data_dir_dict.get(scenario['YEAR'], {}):
                    scenario['PREFS_PATH'] = data_dir_dict[scenario['YEAR']][scenario['STATE']]
                else:
                    resp = input(input_a_path+prompts['PREFS_PATH']+data_dir+os.sep)
                    scenario['PREFS_PATH'] = '' if resp == '' else os.path.join(data_dir, resp)
            else:
                scenario['PREFS_PATH'] = input(input_a_path+prompts['PREFS_PATH'])

        if existing_config['DEFAULT_INTERPOLATED'].get('sa1s_dists_path'):
            scenario['SA1S_DISTS_PATH'] = existing_config['DEFAULT_INTERPOLATED'].get('sa1s_dists_path')
        elif dist_dir:
            taboo = 0
            use_dd = 'x'
            while 'SA1S_DISTS_PATH' in dist_dir_dict.get(scenario['YEAR'], {}):
                use_dd = input("Is "+dist_dir_dict[scenario['YEAR']]['SA1S_DISTS_PATH']+"\nthe file containing the SA1s-to-Districts mapping for "+scenario['STATE']+" in "+scenario['YEAR']+"? [Y]/n ").upper().strip()
                if use_dd not in ['Y', '']:
                    taboo += 1
                    dist_dir_dict = walk_filesystem(dist_dir,
                                {scenario['YEAR']: {"SA1s_Electorates.csv": "SA1S_DISTS_PATH", "SA1s_Districts.csv": "SA1S_DISTS_PATH", "SA1s_Wards.csv": "SA1S_DISTS_PATH"}},
                                aec=False, state=scenario['STATE'], taboo=taboo)
                else:
                    scenario['SA1S_DISTS_PATH']  = dist_dir_dict[scenario['YEAR']]['SA1S_DISTS_PATH']
                    break
            else:
                resp = input(input_a_path+prompts['SA1S_DISTS_PATH']+dist_dir+os.sep)
                scenario['SA1S_DISTS_PATH'] = '' if resp == '' else os.path.join(dist_dir, resp)
        else:
            scenario['SA1S_DISTS_PATH'] = input(input_a_path+prompts['SA1S_DISTS_PATH'])

        if args.output_dir:
            scenario['OUTPUT_DIR'] = args.output_dir
        elif existing_config['DEFAULT_INTERPOLATED'].get('output_dir'):
            scenario['OUTPUT_DIR'] = existing_config['DEFAULT_INTERPOLATED'].get('output_dir')
        else:
            scenario['OUTPUT_DIR'] = input(f"Please input a path to the output directory of this Scenario {press_return}:\n")

        if args.sa1s_breakdown:
            scenario['SA1S_BREAKDOWN_PATH'] = args.sa1s_breakdown.name
        elif existing_config['DEFAULT_INTERPOLATED'].get('sa1s_breakdown_path'):
            scenario['SA1S_BREAKDOWN_PATH'] = existing_config['DEFAULT_INTERPOLATED'].get('sa1s_breakdown_path')
        else:
            if data_dir:
                if 'SA1S_BREAKDOWN_PATH' in data_dir_dict.get(scenario['YEAR'], {}):
                    scenario['SA1S_BREAKDOWN_PATH'] = data_dir_dict[scenario['YEAR']]['SA1S_BREAKDOWN_PATH']
                else:
                    resp = input(input_a_path+prompts['SA1S_BREAKDOWN_PATH']+scenario['YEAR']+f" {press_return}:\n"+data_dir+os.sep)
                    scenario['SA1S_BREAKDOWN_PATH'] = '' if resp == '' else os.path.join(data_dir, resp)
            else:
                scenario['SA1S_BREAKDOWN_PATH'] = input(input_a_path+prompts['SA1S_BREAKDOWN_PATH']+scenario['YEAR']+f" {press_return}:\n")

        if args.polling_places:
            scenario['POLLING_PLACES_PATH'] = args.polling_places.name
        elif existing_config['DEFAULT_INTERPOLATED'].get('polling_places_path'):
            scenario['POLLING_PLACES_PATH'] = existing_config['DEFAULT_INTERPOLATED'].get('polling_places_path')
        else:
            if data_dir:
                if 'POLLING_PLACES_PATH' in data_dir_dict.get(scenario['YEAR'], {}):
                    scenario['POLLING_PLACES_PATH'] = data_dir_dict[scenario['YEAR']]['POLLING_PLACES_PATH']
                else:
                    resp = input(input_a_path+prompts['POLLING_PLACES_PATH']+scenario['YEAR']+f" {press_return}:\n"+data_dir+os.sep)
                    scenario['POLLING_PLACES_PATH'] = '' if resp == '' else os.path.join(data_dir, resp)
            else:
                scenario['POLLING_PLACES_PATH'] = input(input_a_path+prompts['POLLING_PLACES_PATH']+scenario['YEAR']+f" {press_return}:\n")

        filter = r'.*'

        groups = {}

        makeNewGroup = input("Define a new Group of tickets and candidates? [Y]/n: ").upper()
        while makeNewGroup.startswith('Y') or not makeNewGroup:
            newGroup = []
            addingCandsToGroup = True
            groupParties = set()

            while addingCandsToGroup:
                filter = input(f"Search in {scenario['STATE']} (case-insensitive, regex allowed):\n")
                fc = filter_candidates(all_cands, scenario['STATE'], filter, tty=True)
                if fc:
                    print(f"Selected Candidates for {scenario['STATE']}:")
                    elasticated = elastic([fc[0]._fields] + fc)
                    print(term.BOLD + elasticated[0] + term.END)
                    print(*elasticated[1:], sep='\n')

                    whatdo = input("Add selected candidates to group? [Y]/n: ").upper()

                    if whatdo.startswith('Y') or not whatdo:
                        for cand in fc:
                            candstr = ''
                            partystr = cand.party
                            if cand.surname == 'TICKET' and cand.ballot_given_nm == 'VOTE':
                                candstr = cand.ticket + ':' + cand.party
                            else:
                                candstr = cand.ticket + ':' + cand.surname + ' ' + cand.ballot_given_nm

                            for s in term.ALL_SYMBOLS:
                                candstr = candstr.replace(s, '')
                                partystr = partystr.replace(s, '')
                            if candstr not in newGroup:
                                newGroup.append(candstr)

                            groupParties.add(partystr)
                    else:
                        continue # no more zero-candidate groups

                    whatdo = input('Add more candidates to the same group? y/[N]: ')
                    if whatdo.startswith('Y'):
                        continue
                    else:
                        addingCandsToGroup = False

                else:
                    print("No candidates found.")
                    continue

            # done adding candidates?


            # group name...
            groupCode = None

            listParties = list(groupParties)
            if len(listParties) == 1 and party_abs and listParties[0]:
                suggestedCode = party_abs[listParties[0]].title()
                keepit = input("Use suggested Group Code "+suggestedCode+" ? [Y]/n: ")
                if keepit.startswith("Y") or not keepit:
                    groupCode = suggestedCode

            while not groupCode:
                groupCode = input("Please type a 3-5 letter code to name the new Group: ").strip().title()
                if groupCode in groups:
                    print(groupCode, "already exists.")
                    groupCode = None


            print(f"New group {groupCode} in {scenario['STATE']} with the following ATL tickets and/or BTL candidates:\n", *newGroup)
            groups[groupCode] = newGroup

            makeNewGroup = input("\nDefine another new Group of tickets and candidates: [Y]/n: ").upper()
        # end while newGroup

        scenario['GROUPS'] = dumpgroups(groups)

        # confirm other things

        print(" v ".join(groups.keys()), "in", scenario['STATE'], "in", scenario['YEAR'])

        scenCode = None
        groupcodes = [k.upper() for k in groups]
        suggestedScenCode = '_'.join([scenario['STATE'], str(len(groups))+"PP"] + groupcodes)
        if suggestedScenCode not in new_config:
            useSugg = input("Use suggested Scenario Code "+suggestedScenCode+" ? [Y]/n: ").upper()
            if useSugg.startswith('Y') or not useSugg:
                scenCode = suggestedScenCode

        while not scenCode:
            scenCode = input("Please type a unique code to identify the new Scenario: ").strip().upper()
            if scenCode in existing_config:
                print(scenCode, "already exists. ", end='')
                scenCode = None

        new_config[scenCode] = scenario

        newScen = input("\nDefine another new Scenario: [Y]/n: ").upper()
    # end while newScen

    return new_config
### end


def generate_config_cli(args):
    # 1. Figure out files.
    # 1.1. In particular if FROM exists, read it and close it.

    existing_config = {}
    all_cands = {}
    new_config = configparser.ConfigParser(defaults= {
            'NPP_BOOTHS_FN' : 'NPP_Booths.csv',
            'SA1S_PREFS_FN' : 'SA1_Prefs.csv',
            'NPP_DISTS_FN' : 'District_NPPs.csv'
        }
    )

    if args.from_cfg:
        existing_config = load_config_from_file(args.from_cfg)
    else:
        existing_config['DEFAULT_INTERPOLATED'] = {}

    all_cands = read_candidates(args.candidates)

    aec_files_dict = aec_downloads.make_output(aec_downloads.Which.DICTIONARY)
    print("files_dict", aec_files_dict)

    # factored out the new scenario generation
    new_config = addScenarios(args, existing_config, new_config, aec_files_dict, all_cands)

    # Existing Scenarios?
    if args.from_cfg:
        retain_existing = input("Retain all existing Scenarios in updated configuration file? [Y]/n ").strip().upper()
        if retain_existing == '' or retain_existing.startswith('Y'):
            for scen in existing_config:
                if scen in ['DEFAULT', 'DEFAULT_INTERPOLATED', new_config.default_section]:
                    continue
                new_config.add_section(scen)
                for thing in existing_config[scen]:
                    new_config.set(scen, thing, dumpgroups(existing_config[scen][thing]))


        print("Please note that modification of existing Scenarios is [currently] unsupported by this tool. You'll need to edit the configuration file manually.")


    # factor out shared values (create defaults)
    for keyme in ['year', 'output_dir', 'sa1s_breakdown_path', 'polling_places_path']:
        samevals = set()
        for scenario in new_config.sections():
            samevals.add(new_config.get(scenario, keyme.lower(), raw=True, fallback=''))

        if len(samevals) == 1:
            value = str(samevals.pop()).strip()

            for scen in new_config.sections():
                new_config.remove_option(scen, keyme.lower())

            new_config.set(new_config.default_section, keyme.lower(), value)

    # insert interpolations, attempt more removals
    for sharedkey in ['data_dir', 'dist_dir', 'year', 'output_dir', 'sa1s_breakdown_path', 'polling_places_path']:
        if not sharedkey in new_config.defaults().keys():
            continue
        whoami = new_config.get(new_config.default_section, sharedkey.lower())
        if whoami:
            # handle general case
            for scenario in new_config.sections():
                for option in new_config.options(scenario): # this will take from DEFAULTSECT if need be...
                    value = new_config.get(scenario, option, fallback='')
                    if value == whoami: # ... hence eager removal
                        new_config.remove_option(scenario, sharedkey.lower())
                    elif value.startswith(whoami):
                        new_config.set(scenario, option, value.replace(whoami, "%("+sharedkey+")s") )
            # handle defaults section too
            for option in new_config.defaults().keys():
                if option == sharedkey:
                    continue
                value = new_config.get(new_config.default_section, option, fallback='')
                if value.startswith(whoami):
                    new_config.set(new_config.default_section, option, value.replace(whoami, "%("+sharedkey+")s") )


    with open(args.configfile, 'w') as cf:
        new_config.write(cf)

    # write file

def parse_argv():
    parser = argparse.ArgumentParser(description="Generate configuration files for NPP interactively.")
    defaults_p = parser.add_argument_group(title='DEFAULT', description='(these will be asked for interactively if not specified)')
    defaults_p.add_argument('--year')
    defaults_p.add_argument('--data-dir')
    defaults_p.add_argument('--dist-dir')
    defaults_p.add_argument('--polling-places', type=argparse.FileType('r'))
    defaults_p.add_argument('--sa1s-breakdown', type=argparse.FileType('r'))
    defaults_p.add_argument('--output-dir')

    parser.add_argument('--party-details', type=argparse.FileType('r'), help="The AEC's 'Political Parties' CSV")
    parser.add_argument('--from', dest='from_cfg', metavar='OLD_CONFIG', type=argparse.FileType('r'), help='An existing configuration file to modify.')
    parser.add_argument('candidates', type=argparse.FileType('r'), help="AEC candidate CSV file")
    parser.add_argument('configfile', metavar='NEW_CONFIG', help="The configuration file to generate.")
    # ^^ we forego the ArgParse FileType here because it might be the same as what's in --from

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_argv()
    generate_config_cli(args)
