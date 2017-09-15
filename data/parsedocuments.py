# PARSES all-nps-sites.json to individual documents 

import json
import os

with open('all-nps-sites.json', 'r') as f:
    nps = json.load(f)

print(len(nps['documents']))
article = 1
for document in nps['documents']:
    with open('article{}.json'.format(article), 'w') as j:
        j.write(json.dumps(document))
    article += 1
