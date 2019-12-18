# Senate N-Party-Preferred Analysis

## 2019 update

The AEC have changed a few aspects of their spreadsheets and so there are updated new editions of some files: `config2019.py` and `Booth_NPP_2019.py`.

Subsequent scripts should function *almost* unchanged: they'll probably need modification to use the correct version of the `config` file.

## Requirements

- A working Python 3 install, preferably 3.5 or better.


### NPP distribution

- The full preference CSV for your selected State or Territory. The Queensland one for 2016 was last seen [here](http://results.aec.gov.au/20499/Website/External/aec-senate-formalpreferences-20499-QLD.zip) and is about 550MB after decompression.
- The AEC's "this many people from each SA1 voted at this booth" spreadsheet, last seen [here](http://aec.gov.au/Elections/Federal_Elections/2016/files/polling-place-by-sa1s-2016.xlsx) for 2016. Needs to be converted to CSV.
- The list of polling places and their associated information, last seen [here](http://results.aec.gov.au/20499/Website/Downloads/GeneralPollingPlacesDownload-20499.csv) for 2016.

### SA1 Projection & district aggregation

In addition to the above, you'll need to generate a spreadsheet detailing the allocation of SA1s to districts. This is intended for projecting Senate results onto state districts, which was necessary ahead of Queensland 2017 (One Nation) and South Australia 2018 (Nick Xenophon's SA-BEST) but otherwise isn't very useful.

In other words, your spreadsheet should look like this:

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

You're pretty much on your own for generating this spreadsheet, as I expect the various state electoral commissions all present the requisite data in different ways. The above example is the first 10 lines of my Queensland one for 2016.

Things that will probably help:

- QGIS or another GIS program
- LibreOffice Calc or another spreadsheet editor
- The information made available as part of the last state redistribution
    - A shapefile or equivalent of all SA1s
    - A shapefile or equivalent of all the districts

**Note that SA1s can change a bit after each census.** Your state electoral commission and the AEC will use the latest available SA1s, which don't always match - for example, the 2017 Qld redistribution and the 2016 federal election used the same SA1s, but those were updated for the 2019 federal election... and the 2017 data wasn't. Extract an SA1s correspondance table from its spreadsheet on the ABS site. When all is done, it should look a bit like this:

| SA1_7DIGITCODE_2011 | SA1_7DIGITCODE_2016 | RATIO     |
|---------------------|---------------------|-----------|
| 1100101             | 1153965             | 1         |
| 1100102             | 1153902             | 0.4439326 |
| 1100102             | 1153962             | 0.5560674 |
| 1100103             | 1153967             | 1         |


## How To

Zeroth, ensure that that everything exists, is uncorrupted, and that all your spreadsheets are in CSV format.

First, edit `configYYYY.py` to update the paths to the three AEC spreadsheets described in **NPP distribution** and to the SA1-to-districts spreadsheet described in **SA1 Projection & district aggregation**.

Second, run `Booth_NPP_YYYY.py` to generate `{State}/NPP_Booths.csv`. A couple of minutes later, you'll have a spreadsheet where each row represents a polling place, and (most of) the columns represent the number of ballots cast matching a preference order. Absents, postals, declaration pre-polls and provisionals have been aggregated. There's also a "total" column.

Third, run `SA1s_Multiplier.py` to generate `{State}/NPP_SA1s.csv`. Each row will be for a specific SA1/Booth/Division combination. Again, most of the columns will list the number of ballots cast matching a preference order, except that they'll be fractions of a vote now.

Third-and-a-half, run `SA1s_Converter.py correspondencefile [infile] [outfile]` if required. `outfile` is your new `SA1S_DISTS_PATH` for step 4.

Fourth, to perform district aggregation, run `SA1s_Aggregator.py` to generate `{State}/District_NPPS.csv` (and optinally a JS version too for the web-based predictor). Each row represents a district named in the SA1-to-districts spreadsheet. Columns (mostly) list the expected numbers of ballots cast in each district that match the preference order in the columns' headings.

Having done all that, you can [simulate elections](https://abjago.net/4PP-QLD-projections-from-senate-results/predictor.html) with accurate knowledge of how people preferenced!
