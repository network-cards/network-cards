from pytest import PytestUnhandledCoroutineWarning
#!/usr/bin/env python3

# Jim Bagrow
# schema2table.py
# Last Modified: 2020-05-03

import sys
import os
import json

SCHEMA_FILE = "schema/v0.0.1/network_card.schema.json"

D = json.load(open(SCHEMA_FILE))


print(r"%from schema2table.py")
print(r"\begin{description}")
for b in ['overall', 'structure', 'metainfo']:
    box = D['properties'][b]['properties']
    print(rf"\item[{b.capitalize()}]")
    print(r"\begin{description}")
    for k in box:
        print(rf"\item[{k}] {box[k]['description']}")
        #print(k, box[k]['description'])
    print(r"\end{description}")
print(r"\end{description}")
