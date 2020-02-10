#! /usr/bin/env bash
python3 -m zipapp src -o 'nparty.pyz' -p "/usr/bin/env python3"
chmod +x nparty.pyz
./nparty.pyz data -e AEC_Downloads.html
