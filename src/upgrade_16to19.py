#! /usr/bin/env python3

# Copyright: (c) 2020, Alex Jago <abjago@abjago.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# This is a script to upgrade 2016 Senate ballot data to the 2019 format.
# There's not a *lot* of differences but there are differences nonetheless.

import os
import sys
import argparse
import csv
from fnmatch import fnmatch
import shutil
import tempfile
import os.path
import io, zipfile

from npp_utils import *
from term import TTYJUMP

DEFAULT_FILTER = "aec-senate-formalpreferences*"
DEFAULT_SUFFIX = "_to19"
VERBOSITY = False

HEADERFIELDS = ["State", "Division", "Vote Collection Point Name", "Vote Collection Point ID", "Batch No", "Paper No"] # in 2019 edition

def process_candsfile(candsfile):
    '''Gets the candidate ticket data, and the state associated with each Division, from analysis of `candspath`.
       Returns {"StateAbbreviation": {"TicketID": [partyname, candidate1name, ...]}}
       and {"DivisionName": "StateAbbreviation"}
    '''
    # Basically equivalent to cut -d ',' -f 3,4 candspath | sort | uniq

    divstates = {}
    candidates = {}

    with candsfile:
        reader = csv.DictReader(candsfile)
        for row in reader:
            # fields used multiple times
            state_ab = row['state_ab']
            ticket = row['ticket']
            party_ballot_nm = row["party_ballot_nm"]
            ballot_position = int(row['ballot_position'])

            divstates[row['div_nm']] = state_ab # yes this repeats work, no there aren't that many candidates, completes in a split second

            if row['nom_ty'] == 'S':

                # Set up structure
                if state_ab not in candidates:
                    candidates[state_ab] = {}
                if ticket not in candidates[state_ab]:
                    candidates[state_ab][ticket] = [party_ballot_nm]

                # Update ticket name in the event of joint tickets
                if party_ballot_nm not in candidates[state_ab][ticket][0]:
                    candidates[state_ab][ticket][0] += "/" + party_ballot_nm

                # Extend ticket as necessary
                ext =  1+ballot_position - len(candidates[state_ab][ticket])
                if ext > 0:
                    candidates[state_ab][ticket] += [None]*ext

                # Place data!
                candidates[state_ab][ticket][ballot_position] = ticket + ':' + row['surname'] + " " + row['ballot_given_nm']

    return candidates, divstates


def is_already_upgraded(path):
    '''Check if a path is already upgraded.'''
    if not os.path.exists(path):
        return 0

    with open_csvz(path) as infile:
        #print(infile, file=sys.stderr)
        inreader = csv.DictReader(infile)

        #print(inreader.fieldnames, file=sys.stderr)

        if inreader.fieldnames[:6] == HEADERFIELDS:
            return 1
        else:
            return 0


def upgrade(candidates, divstates, infile, outfile):
    '''Upgrade a specified `infile` and put it at `outfile`.
        If `infile` was already upgraded, return 1, else 0
    '''

    inreader = csv.DictReader(infile)

    # Our main task is to take `row['Preferences']` and split it out into columns, while giving it new and useful columns
    # small problem: we'd like to go row by row to keep memory usage low, but we don't know what state we're in yet... and we need that to set fieldnames
    # So we'll use a regular writer and special case the first time in the loop

    outwriter = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
    #print("infile", infile, "outfile", outfile, "inreader:", repr(inreader), "outwriter", repr(outwriter), "\n", flush=True)

    progress = 0

    cands_ATLs = []
    cands_BTLs = []
    State = None

    jump = ''
    if hasattr(sys.stderr, "isatty") and sys.stderr.isatty():
        jump = TTYJUMP

    for row in inreader:
        # skip that header divider
        if row['ElectorateNm'].startswith("---"):
            continue

        Division = row['ElectorateNm']
        VoteCollectionPointName = row['VoteCollectionPointNm']
        VoteCollectionPointId = row['VoteCollectionPointId']
        BatchNo = row['BatchNo']
        PaperNo = row['PaperNo']
        Preferences = row['Preferences']

        if progress == 0: # very first row written! we need to write headers too...
            #print("first row!", row, "\n")
            # and figure out who our candidates are...
            State = divstates[Division]

            for tnum in range(1, len(candidates[State])): # the range setup means we should ignore the UGs
                tick = number_to_ticket(tnum)
                cands_ATLs.append(tick + ":" + candidates[State][tick][0])
                cands_BTLs += candidates[State][number_to_ticket(tnum)][1:]

            cands_BTLs += candidates[State]["UG"][1:]

            print("Upgrading", State, "ballot data from 2016 format to 2019, file:",infile.name,"\n", file=sys.stderr)
            outwriter.writerow((HEADERFIELDS + cands_ATLs + cands_BTLs))
        # end of IF

        # deal with preferences

        #printv(repr(Preferences))

        prefs = Preferences.split(",") # may require more processing here

        outwriter.writerow([State, Division, VoteCollectionPointName, VoteCollectionPointId, BatchNo, PaperNo] + prefs)

        progress += 1

        if (progress % 100000 == 0):
            print(jump+"... Progress:", pretty_number(progress), "ballots upgraded...", file=sys.stderr)

    print(jump+f"... Finished {State}! {progress:n} ballots upgraded.", file=sys.stderr)
    # end of loop

    return 0
# end of function


def parse_argv():
    parser = argparse.ArgumentParser(description="Upgrade 2016 Senate ballots to 2019 format.")
    parser.add_argument('--suffix', default=DEFAULT_SUFFIX, help="optional suffix for when filenames would collide; default is `"+DEFAULT_SUFFIX+"`")
    parser.add_argument('--filter', default=DEFAULT_FILTER, help="shell-style expression to filter input filenames from directory; default is `"+DEFAULT_FILTER+"`")
    parser.add_argument('candidates', type=argparse.FileType('r'), help="AEC candidate CSV file")
    parser.add_argument('input', help="input file or directory")   # supporting directories means we give up ArgParse's FileType magic, but also we just want paths for these anyway :(
    parser.add_argument('output', help="output file or directory")

    return parser.parse_args(arguments)


def upgrade_single_file(candidates, divstates, inpath, outpath):
    '''Zip-aware upgrading of a single file `inpath` placed at `outpath`.
    '''
    tmp_path = ''
    # abstract over inpath==outpath by always writing to a tempfile and then moving it

    # we abstract over reading a zipfile with open_csvz()
    # we abstract over writing a zipfile by giving upgrade() a StringIO
    #  for output and then writing the zipfile ourselves.
    with (sys.stdin if inpath == '-' else open_csvz(inpath)) as infile, io.StringIO() as upgradeio:
        upgrade(candidates, divstates, infile, upgradeio)

        print("Writing file...", file=sys.stderr)

        if zipfile.is_zipfile(inpath):
            # need to write a zipfile
            with (sys.stdout if outpath == '-' else \
                    tempfile.NamedTemporaryFile(mode='wb', delete=False, dir=os.path.dirname(outpath)) ) as outfile:
                tmp_path = outfile.name

                with zipfile.ZipFile(outfile, mode='w',compression=zipfile.ZIP_DEFLATED) as zf:
                    zf.writestr(os.path.basename(outpath.replace('.zip', '.csv')), upgradeio.getvalue())

        else:
            # just write upgradeio to disk
            with (sys.stdout if outpath == '-' else \
                    tempfile.NamedTemporaryFile(mode='wb', delete=False, dir=os.path.dirname(outpath)) ) as outfile:
                tmp_path = outfile.name
                shutil.copyfileobj(upgradeio, outfile)

    # do the movement
    if outpath != '-':
        shutil.move(tmp_path, outpath)
        print(TTYJUMP, file=sys.stderr)

# done!


def main(args, VERBOSITY):

    #printv(args)

    candidates, divstates = process_candsfile(args.candidates)

    # Figure out what the heck args.input and args.output will be

    if os.path.isdir(args.input):
        if not os.path.isdir(args.output):
            if os.path.exists(args.output):
                return "Error: output path exists but is not a directory, when input path is also a directory."
            else:
                os.makedirs(args.output)

        for (rootpath, dirnames, filenames) in os.walk(args.input):
            upgrade_count = 0
            upgrade_skip = 0
            for file_base in filenames:
                file = os.path.join(rootpath, file_base)
                #print(file)
                #print(file_base, args.filter)
                if fnmatch(file_base, args.filter):
                    #print("and matched!")
                    inpath = file
                    outpath = os.path.join(args.output, file_base)

                    # do all the work...

                    if is_already_upgraded(outpath):
                        upgrade_skip += 1
                        continue
                    else:
                        upgrade_single_file(candidates, divstates, inpath, outpath)
                        upgrade_count += 1

                elif fnmatch(file_base, "*.xls*"):
                    print("You'll need to manually convert", file, "to a CSV.", file=sys.stderr)

        print(f"Done! Upgraded {upgrade_count} files and skipped over {upgrade_skip} already upgraded.", file=sys.stderr)

    elif os.path.exists(args.input):
        outpath = args.output # unless...
        if os.path.isdir(args.output):
            outpath = os.path.join(args.output, os.path.basename(args.input))

        if not is_already_upgraded(outpath):
            upgrade_single_file(candidates, divstates, args.input, outpath)

    else:
        return "Error: input does not exist."

if __name__ == '__main__':
    args = parse_argv()
    sys.exit(main(sys.argv[1:], VERBOSITY))
