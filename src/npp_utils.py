# Just some utility functions

import re
import sys
import csv
from collections import namedtuple
import glob
import os
import os.path
import urllib
import zipfile
import io

import term

def printv(*arguments):
    print(*arguments, file=sys.stderr)

def number_to_ticket(num):
    '''Takes an integer like `31` and converts it to a ticket string like "AE".'''
    num = int(num) # Take no chances.

    # Weird base-26 maths ahoy, especially since we don't actually have a zero digit
    # Note these correspondances:

    #        1       A  1
    #       27      AA  (1*26) + 1
    #      703     AAA  (27*26) + 1
    #    18279    AAAA  (703*26) + 1
    #   475255   AAAAA  (18279 * 26) + 1

    # We build our output from the least to the most significant digit.
    # Subtract, modulo, shift right, recurse.

    if num < 0: # this shouldn't happen...
        raise ValueError
    elif num == 0: # base case; stop.
        return ''
    else: # general case; recurse.
        num -= 1
        remainder = num % 26
        shift = (num - remainder) / 26
        return number_to_ticket(shift) + chr(remainder + ord('A'))


def ticket_to_number(tickstr):
    '''Takes a ticket string like "AE" and turns it to a number like "31".'''
    res = 0
    for i in range(len(tickstr)):
        res += (26 ** i) * (1 + ord(tickstr[-(1+i)].upper()) - ord('A'))
    return res

def pretty_number(num, use_prefix=False):
    '''Display numbers to a couple of significant figures and a relevant name.
        `use_prefix` should only be specified for numbers with an absolute value larger than one.
    '''
    scale = [(1e24, "septillion"), (1e21, "sextillion"), (1e18, "quintillion"), (1e15, "quadrillion"), (1e12, "trillion"), (1e9, "billion"), (1e6, "million"), (1e3, "thousand")]
    # mid scale numbers will be given directly, small scale numbers will be derived

    if use_prefix:
        scale = [(1e24, "Y"), (1e21, "Z"), (1e18, "E"), (1e15, "P"), (1e12, "T"), (1e9, "G"), (1e6, "M"), (1e3, "K")]

    out = ''

    if (abs(num) > 1e-3) and (abs(num) < 1e3):
        return str(num)
    elif abs(num) >= 1e3:
        for s in scale:
            if abs(num) >= s[0]:
                out = "{:n} {}".format(num/s[0], s[1])
                break
    elif ans(num) <= 1e-3:
        for s in scale:
            if abs(num) <= (1/s[0]):
                out = "{:n} {}ths of a".format(num/s[0], s[1])
                break

    return out


def read_candidates(candsfile):
    '''Generate a dictionary of candidate data from the supplied CSV.
        `candsfile` must be a file-like object.
        returns {state: {ticket: {surname:, ballot_given_nm:, ballot_number:, party:} } } }
    '''

    bigdict = {}

    with candsfile as infile:
        reader = csv.DictReader(infile)

        # We need to do this in a couple of passes because initially we have to
        # count up tickets

        for row in reader:
            if row['nom_ty'] != 'S':
                continue
            if row['state_ab'] not in bigdict:
                bigdict[row['state_ab']] = {}
            if row['ticket'] not in bigdict[row['state_ab']]:
                if row['ticket'] != 'UG':
                    # create the pseudocandidate now
                    bigdict[row['state_ab']][row['ticket']] = {0: {
                        'surname' : 'TICKET',
                        'ballot_given_nm' : 'VOTE',
                        'ballot_number' : ticket_to_number(row['ticket']),
                        'party' : row['party_ballot_nm']
                        } }
                else: ## row['ticket'] == 'UG':
                    bigdict[row['state_ab']]['UG'] = {}

            bigdict[row['state_ab']][row['ticket']][int(row['ballot_position'])] = {
                'surname' : row['surname'],
                'ballot_given_nm' : row['ballot_given_nm'],
                'ballot_number' : -1,
                'party' : row['party_ballot_nm']
                }

        #print("*** BigDict before allocating ballot numbers:\n", bigdict)

        for state in bigdict:
            ballot_number = len(bigdict[state]) - 1 #-1 for UG

            # iterate over regular tickets
            for tnum in range(1, len(bigdict[state])):
                ticket = number_to_ticket(tnum)
                for candidate in range(1, len(bigdict[state][ticket])): # skip ticketvote
                    #print(bigdict[state][ticket][candidate], candidate)
                    ballot_number += 1
                    bigdict[state][ticket][candidate]['ballot_number'] = ballot_number

            # deal with UGs
            if 'UG' in bigdict[state]: # sometimes there aren't any...
                for candidate in range(1, len(bigdict[state]['UG'])+1):
                    ballot_number += 1
                    bigdict[state]['UG'][candidate]['ballot_number'] = ballot_number

    return bigdict

def read_party_abbrvs(partyfile):
    '''Returns {party name on ballot: {party abbreviation}}'''
    bigdict = {}
    with partyfile:
        reader = csv.DictReader(partyfile, fieldnames=['StateAb', 'PartyAb', 'RegisteredPartyAb', 'PartyNm'])
        next(reader)
        for row in reader:
            if row['RegisteredPartyAb']:
                bigdict[row['RegisteredPartyAb']] = row['PartyAb']

            bigdict[row['PartyNm']] = row['PartyAb']

    return bigdict



def filter_candidates(candsdict, state, filter, tty=False):
    '''Gets candidates in `state` that the given regex `filter` at least partially matches.
        If the input exactly matches a ticket, then the ticket will be returned.
        Returns a list of Candidate(ticket, party, surname, ballot_given_nm, ballot_number)
    '''

    headers = ['ticket', 'party', 'surname', 'ballot_given_nm', 'ballot_number']
    Candidate = namedtuple('Candidate', headers)
    data = []
    filt = re.compile(filter, re.IGNORECASE)

    ticketsplus = [number_to_ticket(tnum) for tnum in range(1, len(candsdict[state]))] + ['UG']
    for tk in ticketsplus:
        cands = candsdict[state][tk]
        for balnum, cv in cands.items():
            cand = ['']*len(headers)
            any_match = False
            for i, header in enumerate(headers):
                field = str(tk) if (i==0) else str(cv[header])
                cand[i] = field
                s = re.search(filt, field)
                if s:
                    any_match = True
                    if tty:
                        cand[i] = field[:s.start()] + term.UNDERLINE + field[s.start():s.end()] + term.END + field[s.end():]
                    else:
                        cand[i] += ''
                if (filter in ticketsplus) and not (filter == str(tk)):
                    # If a filter is a ticket literal but not THIS ticket...
                    any_match = False #... then we only want to match THAT ticket

            if any_match:
                data.append(Candidate(*cand))

    return data

def walk_filesystem(base_dir, files_dict, aec=True, state=None, taboo=0):
    ''' Searches subdirectories of `base_dir` for files that match the URLs we download.
        if aec==True"
            files_dict = {YEAR: {URL: "purpose"}}
        elif aec=False:
            files_dict = {YEAR: {"file_name_to_match": "purpose"}}

        taboo is the count of filenames that have been rejected for this search

        returns {YEAR: {"purpose" : realpath}}
    '''
    outdict = {}

    #print(base_dir, files_dict, aec, state)

    for YEAR in files_dict:
        outdict[str(YEAR)] = {}

        for root, dirs, files in os.walk(base_dir):
            #print(root, dirs, files)
            #print(YEAR, state, aec)

            dir_tiers = {}

            for dir in dirs:
                dir_tiers[dir] = 0
                if state and (state in dir):
                    dir_tiers[dir] += 5
                if YEAR in dir:
                    dir_tiers[dir] += 2
                if (str(int(YEAR)+1) in dir) or (str(int(YEAR)-1) in dir):
                    dir_tiers[dir] += 1

            dir_list = sorted([(v,k) for k,v in dir_tiers.items()])[::-1]
            print(root, taboo, dir_list)

            if taboo >= len(dir_list):
                return outdict

            for score, dir in dir_list[taboo:]: # narrow things down
                #print("recursing to", dir)
                if score < 1:
                    continue
                rez = walk_filesystem(os.path.join(root, dir), files_dict, aec=aec, state=state, taboo=taboo)
                if len(rez[YEAR]):
                    return rez

            for PREFILE in files_dict[YEAR]:
                fn = PREFILE
                if aec:
                    fn = os.path.basename(urllib.parse.urlparse(PREFILE)[2]).replace(".zip", ".csv")
                if fn in files:
                    outdict[YEAR][files_dict[YEAR][PREFILE]] = os.path.realpath(os.path.join(root, fn))
                elif False:
                    pass

    return outdict
# end walk_filesystem


def tty_len(string):
    '''Gives visual length of a string, accounting for ANSI control characters.'''
    tty_adj = 0
    for sym in term.ALL_SYMBOLS:
        if sym in string:
            tty_adj += len(sym)
    return len(string) - tty_adj


def elastic(ls):
    '''Implement elastic "tabstops" for human display.
        Takes a list of lists of stringables, and converts the inner list to strings.'''
    widths = {}
    for i in ls:
        for c, j in enumerate(i):
            widths[c] = max(tty_len(str(j)), widths.get(c, 0))
    out = []
    for i in ls:
        i_out = ''
        for c, j in enumerate(i):
            i_out += str(j) + " "*(2 + widths[c] - tty_len(str(j)) )
        out.append(i_out)
    return out


def open_csvz(file, buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None):
    '''Opens a zip as a io.TextIOWrapper for reading, as though it were not zipped.
        If the file is not zipped, opens() it directly and returns that.
        Only mode 'r' is supported.
    '''
    if zipfile.is_zipfile(file):
        zz = zipfile.ZipFile(file, mode='r')
        zipname = zz.namelist()[0]
        #print("opening", zipname, "from", file, file=sys.stderr)
        return io.TextIOWrapper(zz.open(zipname, 'r'),
            encoding=encoding, errors=errors)

    elif isinstance(file, io.IOBase):
        return file

    else:
        return open(file, mode='r', buffering=buffering, encoding=encoding, errors=errors, newline=newline, closefd=closefd, opener=opener)
