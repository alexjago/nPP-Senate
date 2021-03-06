# Senate N-Party-Preferred Analysis

Australian Senate ballot data permits fine-grained analysis of voting behaviour.

Senate ballots are consistent across an entire State or Territory and feature the widest range of parties.

Crucially, the Australian Electoral Commission publishes the preference sequence of every ballot paper, localised to the polling place it was cast at. The Commission also publishes a correspondence describing how many people from each [SA1][1] voted at each polling place. In combination, this permits projecting Senate results onto other geographies - in particular, state or local districts - with far higher accuracy compared to purely polling-place based analysis.

[1]: https://www.abs.gov.au/websitedbs/D3310114.nsf/home/Australian+Statistical+Geography+Standard+(ASGS)

This project, however, takes its name from an earlier step in the analysis: a party-preferred distribution. This is based on the observation that in lower house elections (Federal, State or Local), only three or four parties might contest a district. The theory is that a party-preferred distribution of Senate ballots will more closely reflect lower house results than simple Senate primaries will. Additionally, the full Senate ballot data permits full analysis of subsequent preference flows too, with the caveat that Senate voting is partial-preferential.

## Requirements

Python 3.6 or higher.

## February 2020 update

Big changes are happening!

### One thing to run it all

There is now a unified program, titled simply `nparty` to deal with all aspects of the analysis. GUI is hopefully coming soon. [Download it here.](https://github.com/alexjago/nPP-Senate/releases/tag/v0.3)

### Better configuration

It always felt bad using `.py` files for configuration. Now they are sensible `.cfg` files.

There is a sub-program, `npp generate`, to assist in creating these configuration files.

### Downloader

Provided that the AEC doesn't change the URLs, `nparty` knows how to download all the files. It can also output a list of them. Matching SA1s to districts and wards is still not a solved problem though.

### Dealing with the 2016/2019 format change

Instead of maintaining parallel analysis tools for two different data formats, there is now a tool to upgrade the old data format to the new. 

### Predictor site

Still a work in progress.


# Let's Go!

Before anything else, you'll need to ensure that you have Python installed. The minimum required version is 3.6.  

[You'll probably want to download and run `nparty.pyz`.](https://github.com/alexjago/nPP-Senate/releases/download/v0.3/nparty.pyz) It's a command-line application. Generally, you'll invoke it as `python3 nparty.pyz *options*`; try `python3 nparty.pyz --help` for a usage summary. If you're on Mac or Linux you should be able to run `chmod +x nparty.pyz` to make it self-executing, then you can call it as `./nparty.pyz` instead.

Please note that subsequent parts of this guide will refer to the program simply as `nparty`.

## Setup

### Data acquisition

`nparty data -e HTML_FILE` will write an HTML file to the specified location and attempt to open it in your web browser. The page contains the latest known links to all the requisite AEC data files.

You can also automatically download (and, where possible, format-upgrade) all of those files, for 2016 and 2019, to a specified folder location. Do this with `nparty data -d DL_FOLDER`.

**Please note that the download is a couple of hundred megabytes.** `nparty` is clever enough to read from compressed ZIP files, so there is no need to unzip - save your disk space. However, any `.xlsx` files will need to be converted to `.csv`

To do anything more than party-preferred distribution at the federal booth level, you will need additional geography data. More on that later.

### Configuration

[Please refer to `2019.cfg` for an example configuration file.](https://github.com/alexjago/nPP-Senate/blob/master/2019.cfg) You can hand-edit your local copy if you choose.

Configuration files are based around the concept of a "scenario", which combines:

- a state/territory
- a year
- a set of groups of tickets and candidates to *distribute* ballots to
- optionally, a mapping to *project* polling-place-level results down to the SA1 level
- optionally, another mapping to *combine* SA1-level results up to a district level

`nparty generate` will assist you in generating a configuration file. It has two required arguments: the AEC's "candidates" file, and where to save the new configuration file.

There are also many optional arguments, corresponding generally to the other AEC files for a given election. It is recommended that you specify as many of these as you can, as otherwise you will need to type them later when prompted, or else hand-edit them into the configuration file.

You can also use `--from` to specify an existing configuration file to expand upon.

`nparty list` will provide a *precis* of the scenarios described in a configuration file.

## Analysis

The three analysis stages (distribute, project, & combine) are invoked by `nparty run`. By default, all defined scenarios will be progressed through as many stages as possible. You can specify that only one stage, and only specific scenarios, be run.

### N-Party-Preferred distribution

Party-preferred distribution is the first stage of actual analysis. It is invoked individually by `nparty run --distribute`.

This command typically takes a couple of minutes in the larger states, and by convention outputs a file called `Booth_NPPs.csv`. This is a spreadsheet where each row represents a polling place, and (most of) the columns represent the number of ballots cast matching a preference order. Absents, postals, declaration pre-polls and provisionals have been aggregated.

Note that this is preference *orders*. Suppose that there are three parties: Red, Blue, and Yellow. One ballot might list a preference for Red but not Blue or Yellow; the corresponding column is `Red`. Another might preference Yellow then Blue; column `YelBlu`. A third might preference Blue, Yellow, Red; column `BluYelRed`.

### SA1 Projection

SA1 projection is the second stage of analysis.

The AEC provides a spreadsheet which says "this many people from this SA1 voted at this polling place". Please note that the 2016 version of this spreadsheet is supplied as an `.xlsx` and hence needs to be converted to `.csv`.

Usually this step will be performed automatically as part of `nparty run`, but it can be individually invoked by `nparty run --project`.

By convention, this stage outputs a file called `SA1_Prefs.csv`.

### Combining SA1s into Districts

District combination is the third stage of analysis, and will require additional work from you.

It is individually invoked as `nparty run --combine` and has an additional option `--js`, which will output the results not just as a CSV, but in a format usable by the website predictor. By convention, this stage outputs a file called `District_NPPs.csv` (or `District_NPPs.js`).

In particular, what you'll need to find or create is a spreadsheet (referred to as `SA1s_Dists`) detailing which [parts of] SA1s are in which districts. It should look a bit like this:

| SA1_id  | Dist_Name |  Pop  |      Pop_Share       |
| :-----: | :-------: | ----: | :------------------- |
| 3100101 | CAPALABA  | 325.0 |         1.0          |
| 3100102 | CAPALABA  | 199.0 |         1.0          |
| 3100103 | CAPALABA  | 433.0 |  0.9954022988505747  |
| 3100103 | REDLANDS  |  2.0  | 0.004597701149425287 |
| 3100104 | CAPALABA  | 268.0 |         1.0          |
| 3100105 | CAPALABA  | 149.0 |         1.0          |
| 3100106 | CAPALABA  | 176.0 |         1.0          |
| 3100107 | CAPALABA  | 181.0 |         1.0          |
| 3100108 | CAPALABA  | 306.0 |         1.0          |

As you can see, there are two lines for SA1 3100103, as it is split between districts. The third column details the absolute population in each part, and the fourth column details the proportion. The header names aren't important, but the column order is.

**Senate vote counts for each SA1 will be projected onto those SA1 populations. If you don't have population data, or don't want to do that, you can make a spreadsheet using the first two columns only.** Then raw Senate vote totals will be used.

| SA1_id  | Dist_Name |
| :-----: | :-------: |
| 3100101 | CAPALABA  |
| 3100102 | CAPALABA  |
| (etc)   | (etc)     |

#### `SA1s_Dists` creation

You're pretty much on your own for generating this spreadsheet, as I expect the various state electoral commissions all present the requisite data in different ways. The above example is the first 10 lines of my Queensland one for 2016.

Things that will probably help:

- QGIS or another GIS program
- LibreOffice Calc or another spreadsheet editor
- The information made available as part of the last state redistribution
    - The third and fourth columns will likely only be possible with this information
- A shapefile or equivalent of all SA1s.
    - This should be available for download from the Australian Bureau of Statistics.
- A shapefile or equivalent of all the districts.
    - Ben Raue compiles these on his website, http://www.tallyroom.com.au/

The process I follow for making a two-column spreadsheet is this:

- New project in QGIS
- Import SA1 boundaries
- Convert SA1s to Centroids (this changes polygons to points, keeping attached data)
- Import district boundaries
- Perform a spatial join (this takes the data from each district and attaches it to those points)
- Export relevant fields to a spreadsheet

#### SA1 Census changes

**Note that SA1s can change with each census.** Your state electoral commission and the AEC will use the latest available SA1s, which don't always match - for example, the 2017 Qld redistribution and the 2016 federal election used the same SA1s (from the 2011 Census), but for the 2019 federal election, the 2016 Census boundaries were finally available... and the 2017 data wasn't updated; the ECQ had no reason to do so. Hence, extract an SA1s correspondance table from its spreadsheet on the ABS site. When all is done, it should look a bit like this:

| SA1_7DIGITCODE_2011 | SA1_7DIGITCODE_2016 | RATIO     |
|---------------------|---------------------|-----------|
| 1100101             | 1153965             | 1         |
| 1100102             | 1153902             | 0.4439326 |
| 1100102             | 1153962             | 0.5560674 |
| 1100103             | 1153967             | 1         |

This spreadsheet shall be referred to `correspondencefile`. You can use this spreadsheet with `nparty upgrade sa1s correspondencefile [infile] [outfile]` to turn an `SA1s_Dists` defined in terms of outdated SA1s, to one defined in terms of newer SA1s.

# Next Steps

Having done all that, you can [simulate elections](https://abjago.net/4PP-QLD-projections-from-senate-results/predictor.html) with more precise knowledge of how people preferenced!
