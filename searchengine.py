from flask import Flask, render_template, redirect, url_for,request
from flask import make_response
import json
import os

import indexing
import queryprocessing

app = Flask(__name__)

index = None
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
                with open(os.path.join(docs_dir, file), 'r') as f:
                    content = f.read()
                    docs.append(content)
                    file_contents[file] = content

        index = indexing.create_index(docs)

        # STORE IN CONTEXT
        app.config['index'] = index
        app.config['doc_id_files'] = doc_id_files
        app.config['file_contents'] = file_contents

        return json.dumps({
                            'files': files,
                            'doc_count': len(files),
                            'terms': list(index.keys()),
                            'term_count': len(index)
                          })


@app.route('/query', methods=['GET', 'POST'])
def query():
    if request.method == 'POST':

        index = app.config['index']
        doc_id_files = app.config['doc_id_files']
        file_contents = app.config['file_contents']

        query = request.form['query']
        
        literals = queryprocessing.process_query(query)
        search_results = queryprocessing.query_search(literals, index)
        
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