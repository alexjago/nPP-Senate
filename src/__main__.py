#!/usr/bin/env python3

# Copyright: (c) 2020, Alex Jago <abjago@abjago.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


import os
import sys
import argparse
import configparser
import json
import os.path
import shutil
import urllib

# Import other modules.
import upgrade_16to19
import Booth_NPP
import SA1s_Aggregator
import SA1s_Converter
import SA1s_Multiplier
import aec_downloads
import Configuration
import term

# we should have a thing for the configuration file.
# `list_scenarios` should be in there, for example, and imported here and into Booth_NPP (if desired).
# But most of what's in there should be for generation.

def must_refresh(fn, *source_fns):
    if not os.path.exists(fn):
        return True
    testt = os.path.getmtime(fn)
    for i in source_fns:
        if os.path.getmtime(i) > testt:
            return True
    else: #this is a for-else...
        return False

def missing_param_skip(args, confp, SCENARIO, params):
    '''Prints a diagnostic and returns True when you should skip this scenario due to missing parameters.'''
    cfpitems = [i[0] for i in confp.items(SCENARIO)]
    for i in params:
        if i.lower() not in cfpitems:
            print(f"*   Skipping Scenario {SCENARIO} due to missing {skipcause} in {args.configfile.name}", file=sys.stderr)
            return True
    else:
        return False

def missing_path_skip(SCENARIO, params):
    # sometimes a path will be 'None'
    for i in params:
        if not os.path.exists(i):
            print(f"*   Skipping Scenario {SCENARIO} due to {i} being non-existent", file=sys.stderr)
            return True
    else:
        return False

def data_download(args):
    aec_downloads.download(args)
    also_upgrade = input(term.BOLD+"Also upgrade old-format data in place? [Y]/n "+term.END).strip().upper()
    if also_upgrade.startswith('Y') or also_upgrade == '':
        # OK so we need a CANDIDATESFILE
        dls = aec_downloads.make_output(aec_downloads.Which.DICTIONARY)
        for YEAR in dls:
            yeardir = os.path.join(args.download, str(YEAR))
            if YEAR is not '2019':
                candsfile = ''
                for thing in dls[YEAR]:
                    if dls[YEAR][thing] == 'CANDIDATES':
                        candsfile = os.path.join(yeardir, os.path.basename(urllib.parse.urlparse(thing)[2]).replace(".zip", ".csv"))
                newargs = parse_argv(['upgrade', 'prefs', candsfile, yeardir, yeardir])
                upgrade_prefs(newargs)


def upgrade_prefs(args):
    # We don't need starting year yet, but we will next time. Probably need to peek at the input file,
    #  and also put the file/directory stuff here.
    upgrade_16to19.main(args, False)


def upgrade_sa1s(args):
    SA1s_Converter.main(args, SA1s_Converter.CORR_HDRS, SA1s_Converter.SA1s_DISTs_HDRS, False)


def list_scenarios(args):
    # most of these we rely on another file, but this one is simple enough to inline
    confp = configparser.ConfigParser()
    confp.read_file(args.configfile)
    printme = [["Scenario", "Preferred Parties", "Place", "Year"]]
    for scenario in confp.sections():
        state = confp[str(scenario)]['STATE']
        parties = json.loads(confp[str(scenario)]['GROUPS'])
        year = confp[str(scenario)]['YEAR']
        printme.append([scenario, " v. ".join(parties.keys()), state, year])
    if hasattr(sys.stdout, "isatty") and sys.stdout.isatty() and len(printme) > 1:
        for c, i in enumerate(Booth_NPP.elastic(printme)):
            # We print to stdout rather than stderr because this isn't diagnostic,
            #  this is the main program output.
            if c == 0:
                print('\033[1m'+i+'\033[0m', file=sys.stdout)
            else:
                print(i, file=sys.stdout)
    else:
        for i in printme:
            print(*i, sep="\t", file=sys.stdout) # also stdout for same reason


def run_distribute(args, confp, scenlist):
    try:
        for SCENARIO in scenlist:
            #print(confp.items(SCENARIO))

            if missing_param_skip(args, confp, SCENARIO, ['YEAR', 'GROUPS', 'STATE', 'PREFS_PATH', 'POLLING_PLACES_PATH', 'OUTPUT_DIR', 'NPP_BOOTHS_FN']):
                continue

            YEAR = confp[SCENARIO]['YEAR']
            PARTIES = json.loads(confp[SCENARIO]['GROUPS'])
            STATE = confp[SCENARIO]['STATE']
            FORMAL_PREFS_PATH = confp[SCENARIO]['PREFS_PATH']
            POLLING_PLACES_PATH = confp[SCENARIO]['POLLING_PLACES_PATH']
            OUTPUT_DIR = confp[SCENARIO]['OUTPUT_DIR']
            NPP_BOOTHS_PATH = os.path.join(OUTPUT_DIR, SCENARIO, confp[SCENARIO]['NPP_BOOTHS_FN'])

            if missing_path_skip(SCENARIO, [FORMAL_PREFS_PATH, POLLING_PLACES_PATH]):
                continue

            if not (must_refresh(NPP_BOOTHS_PATH, FORMAL_PREFS_PATH, POLLING_PLACES_PATH, args.configfile.name) or args.refresh):
                print(f"*   Skipping scenario {SCENARIO} - distribution already done!", file=sys.stderr)
                continue

            print("*** Distributing: scenario {}: {}, in {} [{}] ***".format(SCENARIO, " vs ".join(PARTIES.keys()), STATE, YEAR), file=sys.stderr)
            Booth_NPP.make_dirs(OUTPUT_DIR, SCENARIO)
            Booth_NPP.booth_NPPs(SCENARIO, PARTIES, STATE, FORMAL_PREFS_PATH, POLLING_PLACES_PATH, NPP_BOOTHS_PATH)

    except KeyError as k:
        sys.exit(f"There was an issue with the arguments or configuration file: {k}")


def run_project(args, confp, scenlist):
    try:
        for SCENARIO in scenlist:
            if missing_param_skip(args, confp, SCENARIO, ['OUTPUT_DIR', 'NPP_BOOTHS_FN', 'STATE', 'YEAR', 'GROUPS', 'SA1S_BREAKDOWN_PATH', 'SA1S_PREFS_FN']):
                continue

            YEAR = confp[SCENARIO]['YEAR']
            PARTIES = json.loads(confp[SCENARIO]['GROUPS'])
            STATE = confp[SCENARIO]['STATE']
            SA1S_DISTRICTS_PATH = confp[SCENARIO]['SA1S_DISTS_PATH']
            SA1S_BREAKDOWN_PATH = confp[SCENARIO]['SA1S_BREAKDOWN_PATH']
            OUTPUT_DIR = confp[SCENARIO]['OUTPUT_DIR']
            NPP_BOOTHS_PATH = os.path.join(OUTPUT_DIR, SCENARIO, confp[SCENARIO]['NPP_BOOTHS_FN'])
            SA1S_PREFS_PATH = os.path.join(OUTPUT_DIR, SCENARIO, confp[SCENARIO]['SA1S_PREFS_FN'])

            if missing_path_skip(SCENARIO, [NPP_BOOTHS_PATH, SA1S_BREAKDOWN_PATH]):
                print(NPP_BOOTHS_PATH, SA1S_BREAKDOWN_PATH, file=sys.stderr)
                continue

            if not (must_refresh(SA1S_PREFS_PATH, NPP_BOOTHS_PATH, SA1S_BREAKDOWN_PATH, args.configfile.name) or args.refresh):
                print(f"*   Skipping scenario {SCENARIO} - projection already done!", file=sys.stderr)
                continue

            print("*** Projecting scenario {}: {}, in {} [{}] ***".format(SCENARIO, " vs ".join(PARTIES.keys()), STATE, YEAR), file=sys.stderr)
            SA1s_Multiplier.main(SCENARIO, NPP_BOOTHS_PATH, STATE, YEAR, PARTIES, SA1S_BREAKDOWN_PATH, SA1S_PREFS_PATH)
    except KeyError as k:
        sys.exit(f"There was an issue with the arguments or configuration file: {k}")


def run_combine(args, confp, scenlist):
    # need to refactor SA1s_Converter
    try:
        for SCENARIO in scenlist:

            if missing_param_skip(args, confp, SCENARIO, \
                ['GROUPS', 'SA1S_DISTS_PATH', 'OUTPUT_DIR', 'SA1S_PREFS_FN', 'NPP_DISTS_FN']):
                continue

            YEAR = confp[SCENARIO]['YEAR']
            PARTIES = json.loads(confp[SCENARIO]['GROUPS'])
            STATE = confp[SCENARIO]['STATE']
            SA1S_DISTRICTS_PATH = confp[SCENARIO]['SA1S_DISTS_PATH']
            OUTPUT_DIR = confp[SCENARIO]['OUTPUT_DIR']
            SA1S_PREFS_PATH = os.path.join(OUTPUT_DIR, SCENARIO, confp[SCENARIO]['SA1S_PREFS_FN'])
            NPP_DISTS_PATH = os.path.join(OUTPUT_DIR, SCENARIO, confp[SCENARIO]['NPP_DISTS_FN'])

            if missing_path_skip(SCENARIO, [SA1S_PREFS_PATH, SA1S_DISTRICTS_PATH]):
                continue

            outputs = [NPP_DISTS_PATH]
            if args.js:
                outputs.append(os.path.splitext(NPP_DISTS_PATH)[0] + ".js")
            refresh = False
            for o in outputs:
                refresh |= must_refresh(o, SA1S_PREFS_PATH, SA1S_DISTRICTS_PATH, args.configfile.name)

            if not (refresh or args.refresh):
                print(f"*   Skipping scenario {SCENARIO} - combination already done!", file=sys.stderr)
                continue

            print("*** Combining scenario {}: {}, in {} [{}] ***".format(SCENARIO, " vs ".join(PARTIES.keys()), STATE, YEAR), file=sys.stderr)
            SA1s_Aggregator.main(SCENARIO, PARTIES, SA1S_DISTRICTS_PATH, SA1S_PREFS_PATH, NPP_DISTS_PATH, args.js)
    except KeyError as k:
        sys.exit(f"There was an issue with the arguments or configuration file: {k}")


def run(args):
    #print("Hello World!")
    #print(args)

    confp = configparser.ConfigParser()
    confp.read_file(args.configfile)

    # Figure out if we have a valid set of scenarios
    if args.scenarios and not (set(args.scenarios).intersection(set(confp.sections()))):
        sys.exit(f"Error: no specified scenario is defined.")
    # ... and define that list
    scenlist = confp.sections() if args.all else args.scenarios

    if args.distribute:
        run_distribute(args, confp, scenlist)
    elif args.project:
        #SA1s_Multiplier.run(args, confp)
        run_project(args, confp, scenlist)
    elif args.combine:
        run_combine(args, confp, scenlist)
    elif not (args.distribute or args.project or args.combine):
        #print("Intelligently running each possible action", file=sys.stderr)
        run_distribute(args, confp, scenlist)
        run_project(args, confp, scenlist)
        run_combine(args, confp, scenlist)


def parse_argv(argv):
    '''Sets up and performs the parsing, and exit early in the case of invalid input that can't be specified in ArgParse.
    Returns the result of parse_args.'''

    os.environ['COLUMNS'] = str(shutil.get_terminal_size()[0])

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='sub-commands', dest='subcommand_name', help="Try "+term.UNDERLINE+"%(prog)s "+term.BOLD+"subcommand"+term.END+term.UNDERLINE+" -h"+term.END)

    # we have to propagate the add_arguments up from the other files, sadly

    data_p =  subparsers.add_parser('data', help="Get [URLs to] all necessary AEC data.")
    data_mxg = data_p.add_mutually_exclusive_group()
    data_mxg.add_argument('-d', '--download', metavar='DL_FOLDER', help="download everything to specified folder")
    data_mxg.add_argument('-e', '--examine', metavar="FILE", type=argparse.FileType('w'), default=sys.stdout,
                            help="write list of downloads to FILE as HTML, or pass `-` to output plain text to stdout instead.")

    upgrade_p = subparsers.add_parser('upgrade', help="Either: (1) upgrade a preference file to the latest format; (2) convert an SA1s-Districts file.")
    upgrade_subs = upgrade_p.add_subparsers(dest='upgrade_verb') # can't use `required` until 3.7
    upgrade_prefs = upgrade_subs.add_parser('prefs', help="upgrade a preference file to the latest format")

    upgrade_prefs.add_argument('--suffix', default=upgrade_16to19.DEFAULT_SUFFIX, help="optional suffix for when filenames would collide; default is `"+upgrade_16to19.DEFAULT_SUFFIX+"`")
    upgrade_prefs.add_argument('--filter', default=upgrade_16to19.DEFAULT_FILTER, help="shell-style expression to filter input filenames from directory; default is `"+upgrade_16to19.DEFAULT_FILTER+"`")
    upgrade_prefs.add_argument('candidates', type=argparse.FileType('r'), help="AEC candidate CSV file")
    upgrade_prefs.add_argument('input', help="input file or directory")   # supporting directories means we give up ArgParse's FileType magic :(
    upgrade_prefs.add_argument('output', help="output file or directory")

    upgrade_sa1s = upgrade_subs.add_parser('sa1s', help="convert an SA1s-Districts file from old SA1s to new")
    upgrade_sa1s.add_argument('--no-infile-headers', action='store_true', help="Indicate lack of header row for infile")
    upgrade_sa1s.add_argument('correspondencefile', type=argparse.FileType('r'), help="Columns should be: "+', '.join(SA1s_Converter.CORR_HDRS))
    upgrade_sa1s.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="Columns should be: "+', '.join(SA1s_Converter.SA1s_DISTs_HDRS))
    upgrade_sa1s.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="Columns will be: "+', '.join(SA1s_Converter.SA1s_DISTs_HDRS))

    generate_p = subparsers.add_parser('generate', help="Generate a configuration file interactively, possibly using an existing file as a basis.")
    generate_defaults_p = generate_p.add_argument_group(title='default values optional arguments', description='(these will be asked for interactively if not specified - so specify them in the terminal if possible; --data-dir and --dest-dir in particular are used to automatically find other files)')
    generate_defaults_p.add_argument('--year')
    generate_defaults_p.add_argument('--data-dir')
    generate_defaults_p.add_argument('--dist-dir')
    generate_defaults_p.add_argument('--polling-places', type=argparse.FileType('r'))
    generate_defaults_p.add_argument('--sa1s-breakdown', type=argparse.FileType('r'))
    generate_defaults_p.add_argument('--output-dir')

    generate_p.add_argument('--party-details', type=argparse.FileType('r'), help="The AEC's 'Political Parties' CSV")
    generate_p.add_argument('--from', dest='from_cfg', metavar='OLD_CONFIG', type=argparse.FileType('r'), help='An existing configuration file to take defaults from.')
    generate_p.add_argument('candidates', metavar='CANDIDATES_FILE', type=argparse.FileType('r'), help="AEC candidate CSV file")
    generate_p.add_argument('configfile', metavar='NEW_CONFIG', help="The configuration file to generate.")

    list_p = subparsers.add_parser('list', help="List scenarios from the configuration file.", \
        epilog="Scenario tables are printed to standard output. If that's a terminal, they'll be pretty-printed with elastic tabstops. If that's a pipe or file, they'll be tab-separated to make further processing as straightforward as possible.")
    list_p.add_argument('configfile', type=argparse.FileType('r'))

    run_p = subparsers.add_parser('run', help="Run scenarios from the configuration file.", \
        epilog="Note: You probably don't need to worry about [-d | -p | -c]. If you leave them out, all three phases will be performed intelligently and in order (distribution, projection, combination) for each scenario desired.")
    run_p.add_argument('-r', '--refresh', action='store_true', help="refresh every file created, even if it already exists and is newer than all its source files.")
    run_p.add_argument('--js', action='store_true', help='also output JS from the combination stage, for website predictor')
    run_verbs = run_p.add_mutually_exclusive_group()
    run_verbs.add_argument('-d', '--distribute', action='store_true', help='perform only the party-preferred distribution phase')
    run_verbs.add_argument('-p', '--project', action='store_true', help='perform only the polling-places to SA1s projection phase')
    run_verbs.add_argument('-c', '--combine', action='store_true', help='perform only the SA1s to districts combination phase')
    run_select = run_p.add_mutually_exclusive_group(required=True)
    run_select.add_argument('-a', '--all', action='store_true', help="run all scenarios specified in the configuration file")
    run_select.add_argument('-s', '--scenario', dest='scenarios', metavar='scenario', action='append', help="run one or more scenarios specified in the configuration file (specify each additional scenario with another -s SCENARIO)")
    run_p.add_argument('configfile', type=argparse.FileType('r'))

    gui_p = subparsers.add_parser('gui', help="Launch the Graphical User Interface [not yet implemented].")

    args = parser.parse_args(argv)
    # maybe reset columns here?
    return args
# end parsing


def main(args):
    if args.subcommand_name == 'data':
        if args.download:
            data_download(args)
        else:
            aec_downloads.examine(args)
    elif args.subcommand_name == 'upgrade':
        if args.upgrade_verb == None:
            sys.exit(sys.argv[0] + " upgrade: error: must specify an action {prefs, sa1s}")
        elif args.upgrade_verb == 'prefs':
            upgrade_prefs(args)
        elif args.upgrade_verb == 'sa1s':
            upgrade_sa1s(args)
    elif args.subcommand_name == 'list':
        list_scenarios(args)
    elif args.subcommand_name == 'generate':
        Configuration.generate_config_cli(args)
    elif args.subcommand_name == 'run':
        run(args)
    elif args.subcommand_name == 'gui': # ultimately in ['gui', None]:
        sys.exit("GUI not implemented yet, sorry.")
    else:
        print("N-Party-Preferred distribution of Australian Senate ballots by polling place, projection down to SA1s, aggregation to state/local districts.\n",
                "Try", term.UNDERLINE+sys.argv[0]+" --help"+term.END, "for usage instructions.")

if __name__ == '__main__':
    main(parse_argv(sys.argv[1:]))
