#! /usr/bin/env python3

# outputs an html file full of links

import argparse
import sys
#import webbrowser
import os
import os.path
import urllib
import urllib.request
import shutil
import zipfile
import glob
from enum import Enum

import term
import npp_utils

class Which(Enum):
    HTML = "html"
    DICTIONARY = "dictionary"

STATES = ['ACT', 'NT', 'NSW', 'QLD', 'SA', 'TAS', 'VIC', 'WA']
## yes, yes, two of them are territories, shh.

ELECTION_IDS = {'2016': '20499', '2019': '24310'}

POLLING_PLACES_TEMPLATE = 'https://results.aec.gov.au/ID/Website/Downloads/GeneralPollingPlacesDownload-ID.csv'
FORMAL_PREFERENCES_TEMPLATE = 'http://results.aec.gov.au/ID/Website/External/aec-senate-formalpreferences-ID-STATE.zip'
POLITICAL_PARTIES_TEMPLATE = "https://results.aec.gov.au/ID/Website/Downloads/GeneralPartyDetailsDownload-ID.csv"

SA1s_PPs = {'2016': 'http://aec.gov.au/Elections/Federal_Elections/2016/files/polling-place-by-sa1s-2016.xlsx', \
'2019': 'https://aec.gov.au/Elections/federal_elections/2019/files/downloads/polling-place-by-sa1s-2019.csv'}

CANDIDATES = {'2016': 'https://www.aec.gov.au/Elections/federal_elections/2016/files/2016federalelection-all-candidates-nat-30-06-924.csv',
'2019': 'https://www.aec.gov.au/Elections/federal_elections/2019/files/2019federalelection-all-candidates-nat-17-05.csv'}


TEMPLATE_HTML = \
'''
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>AEC Data Links</title>
  </head>
  <body>
    <h1>Links to download AEC data</h1>
    <p>You'll need all four "nation-wide" files, and the "Formal Preferences" file for each state/territory that you wish to analyse, for each election year. You'll also need to extract the ZIPs.</p>
    CONTENT
  </body>
</html>
'''

TEMPLATE_LIST = \
'''
<h2>YEAR</h2>
<ul>
LIST_ITEMS
</ul>
<hr><br>
'''

TEMPLATE_ITEM = '<li>ITEM</li>'
TEMPLATE_LINK = '<a href="LINK">TEXT</a>'

def make_output(which):
    '''Returns either an HTML file, or a dictionary, depending on the value of `which`
    '''

    downloads = {}

    content = ''

    for YEAR, ID in ELECTION_IDS.items():
        downloads[YEAR] = {}

        polling_places = POLLING_PLACES_TEMPLATE.replace('ID', ID)
        political_parties = POLITICAL_PARTIES_TEMPLATE.replace('ID', ID)
        sa1s_pps = SA1s_PPs[YEAR]
        candidates = CANDIDATES[YEAR]

        list_items = []
        downloads[YEAR][polling_places] = "POLLING_PLACES_PATH"
        downloads[YEAR][political_parties] = "PARTY_DETAILS"
        downloads[YEAR][sa1s_pps] = "SA1S_BREAKDOWN_PATH"
        downloads[YEAR][candidates] = "CANDIDATES"

        pptext = 'Polling Places (nation-wide)'
        if YEAR == 2016:
            pptext += " NB: needs to be converted to CSV"

        list_items.append(TEMPLATE_ITEM.replace('ITEM', TEMPLATE_LINK).replace('LINK', polling_places).replace('TEXT', pptext))
        list_items.append(TEMPLATE_ITEM.replace('ITEM', TEMPLATE_LINK).replace('LINK', sa1s_pps).replace('TEXT', 'Votes by SA1 (nation-wide)'))
        list_items.append(TEMPLATE_ITEM.replace('ITEM', TEMPLATE_LINK).replace('LINK', candidates).replace('TEXT', 'Candidates (nation-wide)'))
        list_items.append(TEMPLATE_ITEM.replace('ITEM', TEMPLATE_LINK).replace('LINK', political_parties).replace('TEXT', 'Political Parties (nation-wide)'))


        for STATE in STATES:
            formalprefs = FORMAL_PREFERENCES_TEMPLATE.replace('ID', ID).replace('STATE', STATE)
            list_items.append(TEMPLATE_ITEM.replace('ITEM', TEMPLATE_LINK).replace('LINK', formalprefs).replace('TEXT', f'Formal Preferences for {STATE}'))
            downloads[YEAR][formalprefs] = STATE


        content += TEMPLATE_LIST.replace('LIST_ITEMS', '\n'.join(list_items)).replace('YEAR', str(YEAR))

    if which == Which.HTML:
        return TEMPLATE_HTML.replace('CONTENT', content)
    elif which == Which.DICTIONARY:
        return downloads


def examine(args):
    if args.examine == sys.stdout:
        dls = make_output(Which.DICTIONARY)
        for YEAR in dls:
            print(*dls[YEAR].keys(), sep='\n')
        return

    print(make_output(Which.HTML), file=args.examine)
    # try:
    #     # we try very hard to suppress error outputs that we can't control and all that
    #     os.close(1)
    #     os.close(2)
    #     webbrowser.get().open_new_tab('file://' + os.path.realpath(args.examine.name))
    #     sys.exit()
    # except Exception as e:
    #     pass # we muted ourselves!

def unarchive_if_possible(dlto, year_dir):
    '''Unarchives a file if possible, returns True if it did.'''
    unzip_exts = []
    _uf = shutil.get_unpack_formats()
    for i in _uf:
        unzip_exts += i[1]

    dl_ext = os.path.splitext(dlto)[1]
    #print(dlto, dl_ext, unzip_exts)
    if os.path.exists(dlto) and (dl_ext in unzip_exts):
        shutil.unpack_archive(dlto, year_dir)
        os.remove(dlto)
        print("Unarchived", dlto)
        return True

    return False

def download(args):
    dls = make_output(Which.DICTIONARY)
    if not os.path.exists(args.download):
        os.makedirs(args.download)

    skipfiles = []

    for YEAR in dls:
        year_dir = os.path.join(args.download, str(YEAR))
        if not os.path.exists(year_dir):
            os.makedirs(year_dir)
        for URL in dls[YEAR].keys():
            fn = os.path.basename(urllib.parse.urlparse(URL)[2])
            dlto = os.path.join(year_dir, fn)
            globfn = glob.glob(os.path.splitext(dlto)[0] + "*")

            # if unarchive_if_possible(dlto, year_dir):
            #     continue
            #elif not os.path.exists(dlto) and not globfn:
            if not os.path.exists(dlto) and not globfn:
                print("Downloading:", dlto, '\n')
                dltmp = dlto + '.download'
                urllib.request.urlretrieve(URL, filename=dltmp, reporthook=progresshook)
                shutil.move(dltmp, dlto)
                print(term.TTYJUMP+term.TTYJUMP+"Downloaded", dlto)
                #unarchive_if_possible(dlto, year_dir)
            elif os.path.exists(dlto) or globfn:
                skipfiles.append(dlto)
                #print(f"skipping {fn} as it is already downloaded or unarchived.")
                continue

    print("Done! Skipped", len(skipfiles), "files as they appear to be already downloaded (and perhaps also unarchived).")


def progresshook(block_count, block_size, total_size):
    if total_size > -1:
        fraction = block_count * block_size / total_size
        print(term.TTYJUMP + '{:%} transferred of {}B so far...'.format(fraction, npp_utils.pretty_number(total_size, use_prefix=True)))
    else:
        print(term.TTYJUMP + '{}B transferred so far...'.format(npp_utils.pretty_number(block_count*block_size, use_prefix=True)))


def parse_argv():
    parser = argparse.ArgumentParser(description="Get all necessary AEC data.")
    mxg = parser.add_mutually_exclusive_group(required=True)
    mxg.add_argument('-d', '--download', metavar='DL_FOLDER', help="download everything to specified folder")
    mxg.add_argument('-e', '--examine', metavar="AEC_Downloads.html", type=argparse.FileType('w'), help="write list of downloads, either as specified HTML file, or plain text URLs to standard output")

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_argv()
    #print(args)
    if args.examine:
        examine(args)
    if args.download:
        download(args)
