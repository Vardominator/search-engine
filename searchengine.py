from flask import Flask, render_template, redirect, url_for,request
from flask import make_response
import json
import os

import indexing
import queryprocessing

app = Flask(__name__)

pos_index = None
kgram_index = None
doc_id_files = {}

@app.route('/test', methods=['GET', 'POST'])
def home():
    return json.dumps({'response': "hello"})

@app.route('/buildindex', methods=['GET', 'POST'])
def buildindex():
    if request.method == 'POST':
        docs = []
        file_contents = {}
        docs_dir = request.form['corpus_dir']

        id = 0
        for root,dirs,files in os.walk(docs_dir):
            files = sorted(files)

            for file in files:
                doc_id_files[id] = file
                id += 1
                with open(os.path.join(docs_dir, file), 'r') as json_data:
                    content = json.load(json_data)
                    docs.append(content['body'])
                    file_contents[file] = {'body': content['body'],
                                           'title': content['title'],
                                           'url': content['url']}

        indexes = indexing.create_index(docs)
        pos_index = indexes[0]
        kgram_index = indexes[1]

        # STORE IN CONTEXT
        app.config['pos_index'] = pos_index
        app.config['kgram_index'] = kgram_index
        app.config['doc_id_files'] = doc_id_files
        app.config['file_contents'] = file_contents

        return json.dumps({
                            'files': files,
                            'doc_count': len(files),
                            'terms': list(pos_index.keys()),
                            'term_count': len(pos_index)
                          })


@app.route('/query', methods=['GET', 'POST'])
def query():
    if request.method == 'POST':

        pos_index = app.config['pos_index']
        kgram_index = app.config['kgram_index']
        doc_id_files = app.config['doc_id_files']
        file_contents = app.config['file_contents']

        query = request.form['query']

        literals = queryprocessing.process_query(query, kgram_index)
        search_results = queryprocessing.query_search(literals, pos_index)

        relevant_files = []
        relevant_contents = {}

        for doc_id in search_results:
            file = doc_id_files[doc_id]
            relevant_files.append(file)
            relevant_contents[file] = file_contents[file]

        return json.dumps({
                            'doc_ids': search_results,
                            'files': relevant_files,
                            'contents': relevant_contents
                          })

if __name__ == "__main__":
    app.run(debug = True)
