# PARSES all-nps-sites.json to individual documents 

import json
import os

with open('data/all-nps-sites.json', 'r') as f:
    nps = json.load(f)

if not os.path.exists('data/documents'):
    os.makedirs('data/documents')

article = 1
for document in nps['documents']:
    # if article <= 11:
    with open('data/documents/{}.json'.format(article), 'w') as j:
        j.write(json.dumps(document))
    article += 1
